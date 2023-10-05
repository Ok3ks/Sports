from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By 
import time 
import re
import pandas as pd

WEBSITE = 'https://www.theaa.com/cars'
POST_CODE = "RM13 8LG"

def browser_init(website = WEBSITE,postcode = POST_CODE):
    browser = webdriver.Safari()
    browser.get(website)

    entry = browser.find_element(By.ID , "begin_search_fullpostcode")
    entry.send_keys(postcode)

    search = browser.find_element(By.NAME, "begin_search[submit]")
    search.click()

    return browser

def extract_car_href(browser_obj):
    soup = BeautifulSoup(browser_obj.page_source, 'html.parser')
    boxes = soup.find_all('div', class_="view-vehicle")

    links = (box.find('a', href=True)['href'] for box in boxes)
    return links

def extract_data(browser, link):
    temp = []
    link = 'https://www.theaa.com' + link   #prepends base website_url
    print(link)
    browser.get(link)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    
    try: 
        no_of_reviews = soup.find('div', itemprop = "reviewCount").get("content")
        price = soup.find("strong", {"class": "total-price new-transport--bold"}).get_text()
        rating = soup.find('div', itemprop="ratingValue").get("content")
        location = soup.h3.get_text()
        SalesTitle = soup.find("span", {"class": "make"}).get_text() +" " + soup.find("span", {"class": "model"}).get_text()
    
    except AttributeError:
        no_of_reviews,price,rating,location,SalesTitle = None,None,None,None,None
    
    temp.append(SalesTitle)
    temp.append(price)
    temp.append(no_of_reviews)
    temp.append(rating)
    temp.append(location)

    page = soup.find_all('li', class_="vd-spec") 

    for i in page:
        text = re.sub('[\n]', '', i.get_text())
        text = text.split(':')
        #title = text[0]
        value = text[1]
        #bf[title] = bf.get(title, [])
        temp.append(value)
    return temp

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(prog='ProgramName', description="Scraps data from a website") 
    parser.add_argument('--count', type= int, help='number of entries to scrap')   #inbuilt validation
    parser.add_argument('--postcode', help='region or area to check')
    args = parser.parse_args()

    data = []
    count = args.count
    POST_CODE = args.postcode
    print("Extracting {} entries of cars around {}".format(count, POST_CODE))
    
    #add tests which validate inputs
    #add arguments for POST_CODE, and number of entries to scrap as count
    
    browser = browser_init(website=WEBSITE, postcode=POST_CODE)
    BASE_CAR_URL = browser.current_url
    queue = extract_car_href(browser)    #generators 

    page= 1
    while count > 0:
        for link in queue:
            data.append(extract_data(browser, link))    #writing to db? or batch write #modify for entry into DB
            count -= 1

        #check to load next page 
        page += 1
        next_page = BASE_CAR_URL + f"&page={page}"
        next_page = browser.get(next_page)
        queue = extract_car_href(browser)
        time.sleep(5)

    filepath = 'cars_data.csv'
    df = pd.DataFrame(data, columns= ['SalesTitle', 'price', 'no_of_reviews', 'rating', 'location', 'Mileage', 'Year', 'Fuel type', 'Transmission', 'Body type', 'Colour', 'Doors', 'Engine size', 'CO2 Emissions'])
    df.to_csv(filepath)

    print("Done, File saved to {}".format(filepath))