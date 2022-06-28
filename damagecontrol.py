from bs4 import BeautifulSoup as bs
import time
import scraper
import pickle
import random
import creds
def identifyPage(driver,soup = None):
    if soup == None:
        soup = bs(driver.page_source, 'html.parser')
    try:
        if '429' in soup.find('div',{'class':'error-code'}).get_text():
            return 429
        elif '404' in soup.find('div',{'class':'error-code'}).get_text():
            return 404
    except:
        pass
    if 'Feed' in driver.title:
        return 201
    elif 'Login' in driver.title:
        return 401
    elif 'Verification' in driver.title:
        return 403
    elif '404' in driver.current_url:
        return 404
    try:
        if soup.find(id='profile-content').find(id='main'):
            return 200
    except:
        pass
    return 0 #Unidentified Error

def damageControl(driver,cred = None,soup = None,target = None):
    '''
    @param driver: chromedriver object
    @param cred: credentials dictionary containing the username and password
    @param soup: bs4 object of the current page
    @param target: target status code, check damage-control.py for more info

    @return: True if the page is the target page, False otherwise
    '''
    if not cred:
        cred = random.choice(creds.creds)

    errcode = identifyPage(driver,soup)
    if errcode == 429:
        print('429 Error: Too Many Requests, Restarting Driver from the cached cookies')
        driver.close()
        time.sleep(5)
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            driver = scraper.init_driver(cred['username'],cred['password'], cookies=cookies)
        except:
            print('Error: Could not load cookies, Restarting Driver from manual login')
            driver = scraper.init_driver(cred['username'],cred['password'], cookies=None)
        
    elif errcode == 403:
        input('Verification Error: Please complete the verification and press any key to continue')
    
    elif errcode == 401:
        #Manually Login
        if not cred:
            cred = creds.creds[0]
        driver.find_element_by_id("username").send_keys(cred.username)
        driver.find_element_by_id("password").send_keys(cred.password)
        driver.find_element_by_xpath("//button[@type='submit']").click()

        return  damageControl(driver,cred,soup,target)

    elif errcode == 404:
        print('404 Error: Page Not Found')
        return False

    #Check error code again
    errcode = identifyPage(driver)

    #Check if the page is the target page
    if not target:
        if errcode//100 == 2: #Default good pages
            return True
        else:
            return False
    else:
        if errcode == target:
            return True
        else:
            return False
