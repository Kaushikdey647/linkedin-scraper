from creds import username, password
import scraper
import tkinter as tk
from tkinter import filedialog
import json
from tqdm import tqdm
import time
import pickle
root = tk.Tk()
root.withdraw()

print("LinkedIn Profile Scraper Application")

print("Initializing driver with your credentials please wait...")
try:
    cookies = pickle.load(open("cookies.pkl", "rb"))
    driver = scraper.init_driver(username, password, cookies=cookies)
except:
    driver = scraper.init_driver(username, password)
print("Please select the file containing the list of urls")

#File containing the list of urls
file_path = None
while not file_path:
    try:
        file_path = filedialog.askopenfilename()
    except:
        print("Error: Could not open file")

print("Please select the folder to save the data to")
result_path = None
while not result_path:
    try:
        result_path = filedialog.askdirectory()
    except:
        print("Error: Could not open folder")

print("scraping data from url")

# Iterate through the files and scrape the data
for line in tqdm(open(file_path,'r'),desc="Scraping data"):
    url = line.strip()
    #scrape the data
    data = scraper.scrape_profile(url, driver)
    #First Try With Cookies
    if not data:
        driver.close()
        driver = scraper.init_driver(username, password, cookies, proxy=None)
        time.sleep(5)
        data = scraper.scrape_profile(url, driver)
    #Second Try Without Cookies
    if not data:
        driver.close()
        driver = scraper.init_driver(username, password, cookies=None, proxy=None)
        time.sleep(5)
        data = scraper.scrape_profile(url, driver)
    #Save to respective files
    with open(result_path+"/"+url.split('/')[-1]+".json", 'w') as f:
        json.dump(data, f)

print('Done')