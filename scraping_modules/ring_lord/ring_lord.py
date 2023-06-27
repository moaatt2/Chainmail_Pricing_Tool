# General Imports
import requests
from bs4 import BeautifulSoup
from time import sleep
import datetime

# Set Constants
_SLEEP_TIME = 5
_STARTING_LINK = 'https://theringlord.com/rings/'


# Define a logging function to log function outputs
def log(msg: str) -> None:
    now = datetime.datetime.now()
    print(f"Logged {now}: {msg}")


#########################
### Get Product Pages ###
#########################


# Define a function to get all the product pages from The Ring Lord's Website
def get_product_pages(url: str = _STARTING_LINK, sleep_time: int = _SLEEP_TIME, links_encountered: set = set()) -> str:
    # Ensure time between pages to scrape responsibly
    sleep(sleep_time)

    now = datetime.datetime.now()
    log(f'Checking {url}')

    # Get soup object from URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Determine if page is a product or collection
    sku = soup.find(lambda tag: tag.name == 'dt' and 'SKU:' in tag.text)

    # If page is a product add the url to the file if it is new
    if sku:
        if url not in links_encountered:
            links_encountered.add(url)
            yield url
    
    # Otherwise find all child products
    else:
        products = soup.find_all('li', {'class': 'product'})

        # Get all unique product links
        unique_links = set()
        for product in products:
            for a in product.find_all('a'):
                link = a['href']
                if 'http' in link:
                    unique_links.add(link)
        
        # Parse all product links
        for link in unique_links:
            yield from get_product_pages(link, sleep_time, links_encountered)


###########################
### Parse Product Pages ###
###########################


# Define a temporary page parsing function to help with planning
def parse_page(url: str) -> None:
    log(f"parsing: {url}")


if __name__ == '__main__':
    for product_page in get_product_pages('https://theringlord.com/rings/bright-aluminum/machine-cut-rings/'):
        parse_page(product_page)
