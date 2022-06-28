import scraper #Obviously to scrape the data
import utils
import phrasegen
import config
from creds import creds
import ascii
from damagecontrol import damageControl,identifyPage

#THIRD PARTY LIBRARIES
from tqdm import tqdm
import random
import os
import sys
import time
import pandas as pd
from selenium import webdriver


# ASSISTING MODULES

def process_csv(file, driver):
    #Take in input dataframe
    inp_df = pd.read_csv(file)

    url_col = utils.return_list_head(inp_df)

    print('Got the links from the CSV Files... working on it...')
    datalist = []

    #Processing the URLs
    url_count = 0

    for i in tqdm(inp_df.index,desc='Processing URLs'):

        #Get the Profile URL
        url = inp_df[url_col][i]

        #Convert the data in csv to dictionary
        data = inp_df.iloc[i].to_dict()
        
        #See if the data is already in the database
        try:
            if data['processed'] == True:
                continue
        except:
            pass
        #Scrape the data
        profile = scraper.scrape_profile(url,driver)

        #Check if the profile is valid
        if profile == None:
            if identifyPage(driver) == 404:
                data['processed'] = True
                continue
            else:
                damageControl(driver)
                profile = scraper.scrape_profile(url,driver)
                if profile == None:
                    print('Unexpected behaviour occured, saving your progress, please try again')
                    break
                
        
        data['name'] = profile['name']
        
        data['location'] = profile['intro-location']

        data['processed'] = True

        for n in range(3):
            trait,compliment = phrasegen.create_template(profile)
            data['trait-{}'.format(n+1)] = trait
            data['compliment-line-{}'.format(n+1)] = compliment
        datalist.append(data)

        #Sleep for a non deterministic moment
        time.sleep(random.randint(2,6))

        url_count += 1
        if url_count == config.max:
            break
    #Out with the datalist
    out_df = pd.DataFrame(datalist)

    #Save the dataframe to a csv
    pd.merge(inp_df,out_df,on=url_col,how='outer').to_csv(file[:-4]+'_processed.csv',index=False)


def process_param(param,driver,str):
    if(str == 'url'):
        #Get the Profile URL
        
        profile = scraper.scrape_profile(param,driver)
        
        if(profile == None):
            damageControl(driver)
        txt,keys = phrasegen.create_template(profile)
        #Show some profile data:
        print('Name: ', profile['name'])
        print('Location: ', profile['intro-location'],'\nSkills: ', profile['skills'])
        print('Line:', txt)

    elif(str == 'csv'):
        process_csv(param,driver)



## MAIN APPLICATION


#Clear the Terminal for some action
os.system('clear')

argn = len(sys.argv)

if(argn == 1):
    print("ERROR: No Arguments Passed")
else:
    print(ascii.banner , '\n')

    print('Let\'s get you started, initializing the scraper...\n')

    #Initialize the scraper
    cred = random.choice(creds)
    driver = scraper.init_driver(cred['username'],cred['password'])

    for param in sys.argv[1:]:
        if param[:25] == 'https://www.linkedin.com/' or param[:24] == 'http://www.linkedin.com/':
            process_param(param,driver,'url')
        elif param[-4:] == '.csv':
            process_param(param,driver,'csv')
        else:
            print("ERROR: Invalid Argument",param)

    driver.close()
    print('\nDone!')