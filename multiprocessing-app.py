import multiprocessing
from utils import split, name_from_url
from creds import username, password, creds
from config import threads, useproxy, max
import scraper
import tkinter as tk
import time
from tkinter import filedialog
import json
from tqdm import tqdm
import pickle

def uni_process(urls,process_id,result_path,proxy=None):
    #Fetch the cookies
    cookies = pickle.load(open("cookies.pkl", "rb"))
    #Initialize the driver
    driver = scraper.init_driver(creds[process_id]['username'], creds[process_id]['password'], proxy=proxy)
    
    #Start Scraping the data
    for url in tqdm(urls,desc="Process {}".format(process_id)):
        data = scraper.scrape_profile(url, driver)
        #First Try With Cookies
        if not data:
            driver.close()
            driver = scraper.init_driver(username, password, cookies, proxy)
            time.sleep(5)
            data = scraper.scrape_profile(url, driver)
        #Second Try Without Cookies
        if not data:
            driver.close()
            driver = scraper.init_driver(username, password, cookies=None, proxy=proxy)
            time.sleep(5)
            data = scraper.scrape_profile(url, driver)
        #Save to respective files
        result_path_definite = result_path+"/"+name_from_url(url)+".json"

        #Write to the json file
        with open(result_path_definite, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__":
    #Welcome the user
    print("LinkedIn Profile Scraper Application: Multithreaded")

    print("Please Select your list of linkedin URLs")

    #Opens a window to select the path to a file
    file_path = None
    while not file_path:
        try:
            file_path = filedialog.askopenfilename()
        except:
            print("Error: Could not open file")
    
    #Opens a window to select the path to a folder
    print("Please select the folder to save the data to")
    result_path = None
    while not result_path:
        try:
            result_path = filedialog.askdirectory()
        except:
            print("Error: Could not open folder")

    urls = [] #initializing the list of urls

    #Filling it up with the urls
    for line in open(file_path,'r'):
        urls.append(line.strip())

    threads = len(creds)
    
    urls = urls[:max*threads]

    #Splitting the urls into chunks for each process

    url_chunks = list(split(urls,threads))

    #Getting the proxies
    if useproxy: #Check if proxies are enabled
        proxies = []
        for line in open('proxies.txt','r'):
            proxies.append(line.strip())
        
        proxies = proxies[:len(url_chunks)] #Take what you need :)
        #Initializing the processes
    processes = []

    #Starting the processes
    print("Scraping for data")

    for i in range(len(url_chunks)):
        #Append the process to process list
        if useproxy:
            process = multiprocessing.Process(target=uni_process,args=(url_chunks[i],i,result_path,proxies[i]))
        else:
            process = multiprocessing.Process(target=uni_process,args=(url_chunks[i],i,result_path))
        process.start()
        processes.append(process)
        time.sleep(2)
    
    for process in processes:
        process.join()
    
    print("Done")
