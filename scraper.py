
from bs4 import BeautifulSoup as bs
from config import buffertime_st,buffertime_mt,usemultiprocessing, debug
from utils import is_verification
from selenium import webdriver
from damagecontrol import damageControl
import time
import pickle
#Initialize the webdriver and return it to the caller

""" from selenium import webdriver
PROXY = "11.456.448.110:8080"
chrome_options = WebDriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=%s' % PROXY)
chrome = webdriver.Chrome(chrome_options=chrome_options)
chrome.get("https://www.google.com") """

def init_driver(username,password,cookies=None,proxy=None):
    #Initialize Chrome Options
    chrome_options = webdriver.ChromeOptions()
    
    #Enable Proxy Servers, (change in config.py)
    if proxy:
        chrome_options.add_argument('--proxy-server=%s' % proxy)
    
    #Show the screen or not
    if not debug:
        chrome_options.add_argument('headless')
        chrome_options.add_argument('window-size=1920x1080')
        chrome_options.add_argument("disable-gpu")

    #Initialize the driver with options
    try:
        driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
    except:
        print("Error: Could not initialize driver with options, trying without options")
        driver = webdriver.Chrome('./chromedriver')
    
    #If no cookies are passed, login and get the cookies
    if not cookies:

        #open linkedin site
        driver.get('https://www.linkedin.com/login')

        #Use credentials
        driver.find_element_by_id("username").send_keys(username)
        driver.find_element_by_id("password").send_keys(password)

        #Log in to linkedin
        driver.find_element_by_xpath("//button[@type='submit']").click()

        #Wait for the page to load
        # time.sleep(2)

        # for i in range(6):
        #     try:
        #         #Check if the page is alright
        #         if damageControl(driver):
        #             break
        #     except:
        #         pass
        #     if i == 5:
        #         print("Error in {}: Could not login to linkedin",format(__name__))
        #         driver.close()
        #         return None


        #Dump the cookies for future use
        pickle.dump(driver.get_cookies() , open("cookies.pkl","wb"))
    
    else:

        #Get the page
        driver.get('https://www.linkedin.com')

        #Load the cookies
        for cookie in cookies:
            driver.add_cookie(cookie)

        #Try and get the page again
        driver.get('https://www.linkedin.com')

        #Check if verification persists
        if not damageControl(driver):
            #call init driver again
            return init_driver(username,password,cookies=None,proxy=proxy)
    return driver

'''
This function will scrape the url of all relevant data and return dictionary of data.
The structure of dict is as follows

profile: {
    name,
    intro,
    intro-education,
    intro-work,
    intro-location,
    about,
    education: [
        institution,
        degree,
        time_period
    ],
    experience: [
        position: [
            title,
            position_type,
            duration,
            description
        ]
        company/institute,
        total_duration,
        location
    ],
    skills: [skillname]
    certifications: [
        name,
        issuer
    ]
}
'''

def scrape_profile(url,driver):
    try:
        driver.get(url)
    except:
        return None

    #initialize prime return variable
    profile_dict = {}

    if usemultiprocessing:
        time.sleep(buffertime_mt//2)
    else:
        time.sleep(buffertime_st//2)
    #Scroll a while to get the full profile
    try:
        #try scrolling to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except:
        pass
    if usemultiprocessing:
        time.sleep(buffertime_mt//2)
    else:
        time.sleep(buffertime_st//2)
    #Get the page soup
    soup = bs(driver.page_source, 'html.parser')
    try:
        profile = soup.find(id='profile-content').find(id='main')
    except:
        return None

    #Get the top section data, let us say its in 3 different groups
    left_panel = profile.find('div',{'class': 'pv-text-details__left-panel'})
    right_panel = profile.find('ul',{'class': 'pv-text-details__right-panel'})
    loc_panel = profile.find('div',{'class': 'pb2 pv-text-details__left-panel'})
    
    #Name usually always exists else we got a bad url
    try:
        profile_dict['name'] = left_panel.find('h1').get_text().strip()
    except:
        print("User {} not found".format(url))
        return
    
    #Get the intro
    try:
        profile_dict['intro'] = left_panel.find('div',{'class': 'text-body-medium break-words'}).get_text().strip() # get the description
    except:
        profile_dict['intro'] = "N/A"
    try:
        profile_dict['intro-education'] = right_panel.find('div',{'aria-label': 'Education'}).get_text().strip() # get the education
    except:
        profile_dict['intro-education'] = 'Not Available'
    try:
        profile_dict['intro-work'] = right_panel.find('div',{'aria-label': 'Current company'}).get_text().strip() # get the education
    except:
        profile_dict['intro-work'] = 'Not Available'
    try:
        profile_dict['intro-location'] = loc_panel.find('span',{'class': 'text-body-small inline t-black--light break-words'}).get_text().strip() # get the location
    except:
        profile_dict['intro-location'] = 'Not Available'

    #Get the about section
    try:
        about = profile.find('div',{'id':'about'}).parent
        profile_dict['about'] = about.find('div',{'class': 'inline-show-more-text inline-show-more-text--is-collapsed'}).get_text().strip()
    except:
        profile_dict['about'] = 'Not Available'
    
    #Get the education section
    try:
        education = profile.find('div',{'id':'education'}).parent
        profile_dict['education'] = []
        for li in education.find('ul').find_all('li',recursive=False):
            edu = {}
            edu['institute'] = li.find('span',{'class':'mr1 hoverable-link-text t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
            edu['degree'] = li.find('span',{'class':'t-14 t-normal'}).find('span',{'aria-hidden':'true'}).get_text().strip()
            edu['time_period'] = li.find('span',{'class':'t-14 t-normal t-black--light'}).find('span',{'aria-hidden':'true'}).get_text().strip()
            profile_dict['education'].append(edu)
    except:
        pass
    
    #Get the experience section
    try:
        experience = profile.find('div',{'id':'experience'}).parent
        profile_dict['experience'] = []
        for li in experience.find('ul').find_all('li',recursive=False):
            exp = {}
            try:
                exp['position'] = {}
                exp['position']['title'] = li.find('span',{'class':'mr1 t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                subtitle = li.find('span',{'class':'t-14 t-normal'}).find('span',{'aria-hidden':'true'}).get_text().strip().split(' · ')

                exp['company/institute'] = subtitle[0]
                try:
                    exp['position']['position_type'] = subtitle[1]
                except:
                    exp['position']['position_type'] = 'Not Available'
                time_n_place = li.find_all('span',{'class':'t-14 t-normal t-black--light'})
                exp['total_duration'] = time_n_place[0].find('span',{'aria-hidden':'true'}).get_text().strip().split(' · ')[0]
                try:
                    exp['location'] = time_n_place[1].find('span',{'aria-hidden':'true'}).get_text().strip()
                except:
                    exp['location'] = 'Not Available'
                try:
                    exp['position']['description'] = li.find('div',{'class':'pvs-list__outer-container'}).get_text().strip()
                except:
                    pass
            except:
                exp['company/institute'] = li.find('span',{'class':'mr1 hoverable-link-text t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                exp['total_duration'] = li.find('span',{'class':'t-14 t-normal'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                try:
                    exp['location'] = li.find('span',{'class':'t-14 t-normal t-black--light'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                except:
                    pass
                exp['position'] = []
                for li2 in li.find('ul',{'class':'pvs-list'}).find_all('li',recursive=False):
                    position = {}
                    position['title'] = li2.find('span',{'class':'mr1 hoverable-link-text t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                    try:
                        position['position_type'] = li2.find('span',{'class':'t-14 t-normal'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                    except:
                        position['position_type'] = 'Not Available'
                    time_n_place = li.find_all('span',{'class':'t-14 t-normal t-black--light'})
                    try:
                        position['duration'] = time_n_place[0].find('span',{'aria-hidden':'true'}).get_text().strip().split(' · ')[0]
                    except:
                        position['duration'] = 'Not Available'
                    try:
                        exp['description'] = li2.find('div',{'class':'pvs-list__outer-container'}).get_text().strip()
                    except:
                        pass
                    exp['position'].append(position)
            profile_dict['experience'].append(exp)
    except:
        pass
    
    #Get the reccommendations section
    try:
        reccomendations = profile.find('div',{'id':'recommendations'}).parent
        profile_dict['recommendations'] = []

        for li in reccomendations.find('ul').find_all('li',recursive=False):
                recc = {}
                recc['giver'] = li.find('div',{'class':'display-flex flex-column full-width align-self-center'}).find('span',{'class':'mr1 hoverable-link-text t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                recc['desc'] = li.find('div',{'class':'pvs-list__outer-container'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                profile_dict['recommendations'].append(recc)
    except:
        pass

    #Get the awards section
    try:
        awards = profile.find('div',{'id':'honors_and_awards'}).parent
        profile_dict['awards'] = []
        for li in awards.find('ul').find_all('li',recursive=False):
            award = {}
            award['title'] = li.find('div',{'class':'display-flex align-items-center'}).find('span',{'aria-hidden':'true'}).get_text().strip()
            issuer_n_date = li.find('span',{'class':'t-14 t-normal'}).find('span',{'aria-hidden':'true'}).get_text().strip().replace('Issued by ','').split(' · ')
            award['issuer'] = issuer_n_date[0]
            award['date'] = issuer_n_date[1]
            profile_dict['awards'].append(award)
    except:
        pass
    #Get the certifications section
    try:
        certifications = profile.find('div',{'id':'licenses_and_certifications'}).parent
        profile_dict['licenses_and_certifications'] = []
        for li in certifications.find('ul').find_all('li',recursive=False):
            cert = {}
            try:
                try:
                    cert['name'] = li.find('span',{'class':'mr1 hoverable-link-text t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                except:
                    cert['name'] = li.find('span',{'class':'mr1 t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                cert['issuer'] = li.find('span',{'class':'t-14 t-normal'}).find('span',{'aria-hidden':'true'}).get_text().strip()
                profile_dict['licenses_and_certifications'].append(cert)
            except:
                pass
    except:
        pass

    #Get the skills section
    try:
        skills = profile.find('div',{'id':'skills'}).parent
        profile_dict['skills'] = []
        for li in skills.find('ul').find_all('li',recursive=False):
            skill = li.find('span',{'class':'mr1 t-bold'}).find('span',{'aria-hidden':'true'}).get_text().strip()
            profile_dict['skills'].append(skill)
    except:
        pass

    return profile_dict