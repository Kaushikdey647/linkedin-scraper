from bs4 import BeautifulSoup as bs
import pandas as pd

def split(lists, process_count):
    k, m = divmod(len(lists), process_count)
    return (lists[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(process_count))

def name_from_url(url):
    arr = url.split('/')
    while "" in arr:
        arr.remove("")
    return arr[-1]

def is_valid_profile(driver,url):
    try:
        driver.get(url)
        soup = bs(driver.page_source, 'html.parser')
        if soup.find(id='profile-content').find(id='main') == None:
            return False
        else:
            return True
    except:
        return False

def is_verification(soup):
    if 'Verification' in  soup.find('title').get_text():
        return True
    else:
        return False

def return_list(dat):
    url_col = '' #Find the column that stores the url

    for column in dat.columns:
        try:
            str = dat[column][0]
            if str[:25] == 'https://www.linkedin.com/' or str[:24] == 'http://www.linkedin.com/':
                url_col = column
                break
        except:
            pass
    try:
        return list(dat[url_col])
    except:
        return None

def return_list_head(dat):
    url_col = '' #Find the column that stores the url

    for column in dat.columns:
        try:
            str = dat[column][0]
            if str[:25] == 'https://www.linkedin.com/' or str[:24] == 'http://www.linkedin.com/':
                url_col = column
                break
        except:
            pass
    try:
        return url_col
    except:
        return None