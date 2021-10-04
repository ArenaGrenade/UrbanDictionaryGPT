from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta
import re
import pandas as pd
from ua_gen import get_random_ua

make_date_url = lambda date, page: f"https://www.urbandictionary.com/yesterday.php?date={date}&page={page}"
make_define_url = lambda termID: f"https://api.urbandictionary.com/v0/define?defid={termID}"

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'referrer': 'https://google.ae',
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Pragma": "no-cache"
}

latest_date = date.today()
current_date = date(2021, 9, 30) # Launch year of Urban Dictionary
# current_date = date(1999, 1, 1) # Launch year of Urban Dictionary
date_delta = timedelta(days=1)

def_id_regex_catcher = re.compile("[^=]+$")

collected_def_ids = set()

while current_date <= latest_date:
    current_page = 1 # For each date we check for a multitude of pages and we stop if we get no results from any page
    
    while True:
        # Make the request for the current page
        headers["user-agent"] = get_random_ua()
        date_url = make_date_url(current_date, current_page)
        date_response = requests.get(date_url, headers)
        print("Making request", date_url, ":", date_response.status_code)
        
        # If the reuqest is valid, parse the html and get the definition ids
        if 200 <= date_response.status_code < 300:
            # Succesfully scraped the page
            page_soup = BeautifulSoup(date_response.content, "html.parser")
            listing_area = page_soup.find(id="columnist") # This is the container that has the ul tag -> li -> a -> href (which has the def ids)
            
            # Break if we do not have a listing area or a ul under listing area
            if listing_area is None or listing_area.ul is None: break
            
            # Grab all the defnition ids on page
            page_def_ids = [def_id_regex_catcher.findall(a_tag.a["href"])[0] for a_tag in listing_area.ul.children]
            
            # Break if we do not have any definitions on page
            if not page_def_ids: break
            
            # Update global definition ids list and update page number
            collected_def_ids.update(page_def_ids)
            current_page += 1
        else: break # If invalid request break
    
    current_date += date_delta
    
collected_def_ids = list(collected_def_ids)

def_ids_df = pd.Series(collected_def_ids)
def_ids_df.to_csv("def_ids.csv", index=False)
