# Imports
import requests
from bs4 import BeautifulSoup
from time import sleep
import datetime
import re

# Selenium Scraping imports
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

# Set Variables
_SLEEP_TIME = 5
_STARTING_LINK = 'https://www.metaldesignz.com/jump-rings/'
_LINK_FILE_PATH = '../../product_page_listings/metal_designz/metal_designz_products.csv'


# Define a logging function to log function outputs
def log(msg: str) -> None:
    now = datetime.datetime.now()
    print(f"Logged {now}: {msg}")

    
#########################
### Get Product Pages ###
#########################


# Helper function that gets the product links from a category page
def get_product_links(soup: BeautifulSoup) -> None:
    product_grid = soup.find('ul', {'class': 'productGrid'})
    products = product_grid.find_all('li', {'class': 'product'})

    for product in products:
        link_tag = product.find('a', {'class': 'card-figure__link'})
        link = link_tag['href']
        yield link


# Get link to next page if applicable
def get_next_page(soup: BeautifulSoup) -> str:
    next_page = None
    pagination = soup.find('nav', {'class': 'pagination'})
    link_tag = pagination.find('a', {'aria-label': 'Next'})

    if link_tag:
        next_page = link_tag['href']
    
    return next_page


# From the starting link find all product pages
def get_product_pages(url: str = _STARTING_LINK) -> None:

    # Get page and create a parsable object
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get links to category pages
    sidebar = soup.find('aside', {'class': 'page-sidebar'})
    category_sidebar = sidebar.find(lambda tag: tag.name == 'div' and tag.find('h2', string='Jump Rings') is not None)
    category_links = set(map(lambda tag: tag['href'], category_sidebar.find_all('a')))

    # Iterate through top level links
    for num, link in enumerate(category_links):
        print(f"Checking cateogry: {num} -  {link}")
        sleep(5)

        # Get first page of category
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the product links from the page
        yield from get_product_links(soup)

        # Get link to the next page
        next_page = get_next_page(soup)

        # Itterate through remaining pages if applicable
        while next_page:
            print(f'Found New Page: {next_page}')
            sleep(5)

            # Get new page            
            response = requests.get(next_page)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Print product links
            yield from get_product_links(soup)
                
            # Get next page if applicable
            next_page = get_next_page(soup)


###########################
### Parse Product Pages ###
###########################


# Define a function that converts unclean strings into clean numbers
def get_number(string):
    return float(''.join([i for i in string if (i.isdigit() or i == '.')]))


# Define a function that returns info about the products on a page given a url and a webdriver
def parse_page(url: str, driver: webdriver) -> dict:
    # Get the page and wait a bit for it to load
    driver.get(url)
    sleep(4)


    # Define output dictionary
    out = {
        "time_accessed ":       str(datetime.datetime.now()),
        "sku":                  None,
        "product_name":         None,
        "material":             None,
        "price":                None,
        "currency":             "CAD",
        "wire_diameter_in":     None,
        "wire_diameter_mm":     None,
        "wire_diameter_gauge":  None,
        "internal_diameter_in": None,
        "internal_diameter_mm": None,
        "aspect_ratio":         None,
        "color":                None,
        "bags_in_stock":        None,
        "rings_per_bag":        None,
    }


    # Get product name
    out['product_name'] = driver.find_element(By.CSS_SELECTOR, 'h1.productView-title').text


    # Get material
    breadcrumbs = driver.find_element(By.CSS_SELECTOR, 'nav[aria-label=Breadcrumb]')
    out['material'] = breadcrumbs.find_elements(By.CSS_SELECTOR, 'li')[2].text.strip()

    ## Alternate method for invalid materials
    if out['material'] == 'Square Jump Rings':
        if 'stainless steel' in out['product_name'].lower():
            out['material'] = 'Stainless Steel'
        elif 'copper' in out['product_name'].lower():
            out['material'] = 'copper'
        elif 'bronze' in out['product_name'].lower():
            out['material'] = 'bronze'
        elif 'anodized aluminum' in out['product_name'].lower():
            out['material'] = 'anodized aluminum'


    # Get Wire diameter info
    gauge_match =  re.search(r'\d+ ?g', out['product_name'], re.IGNORECASE)
    if gauge_match:
        gauge = ''.join([i for i in gauge_match.group() if i.isdigit()])
        gauge_info = {
            # Follows stated rule that Metal Designz uses SWG for 14-19 or AWG for 20-24
            # Returns a tuple in the format: (metric, imperial, Gauge & System)
            '12': (0.104, 2.642, '12 SWG'),
            '13': (0.092, 2.337, '13 SWG'),
            '14': (0.080, 2.032, '14 SWG'),
            '15': (0.072, 1.829, '15 SWG'),
            '16': (0.064, 1.626, '16 SWG'),
            '17': (0.056, 1.422, '17 SWG'),
            '18': (0.048, 1.219, '18 SWG'),
            '19': (0.040, 1.016, '19 SWG'),
            '20': (0.0320, 0.812, '20 AWG'),
            '21': (0.0285, 0.723, '21 AWG'),
            '22': (0.0253, 0.644, '22 AWG'),
            '23': (0.0226, 0.573, '23 AWG'),
            '24': (0.0201, 0.511, '24 AWG'),
        }
        out['wire_diameter_in'], out['wire_diameter_mm'], out['wire_diameter_gauge'] = gauge_info[gauge]


    # Get Ring Inner Diameter
    id_in_match = re.search(r'\d+\/\d+"', out['product_name'], re.IGNORECASE)
    if id_in_match:
        numerator, denominator = id_in_match.group().strip('"').split('/')
        id_in = float(numerator) / float(denominator)
        id_mm = id_in * 25.4
        out['internal_diameter_in'] = id_in
        out['internal_diameter_mm'] = id_mm


    # Get Aspect Ratio
    if out['internal_diameter_in'] and out['wire_diameter_in']:
        out['aspect_ratio'] = out['internal_diameter_in'] / out['wire_diameter_in']


    # Parse options
    option_div = driver.find_element(By.CSS_SELECTOR, 'div[data-product-option-change]')
    selects = option_div.find_elements(By.CSS_SELECTOR, 'Select')
    labels = option_div.find_elements(By.CSS_SELECTOR, 'label')

    ## Set default options types
    qty_select = None
    color_select = None
    radio_options = None

    # set selects properly
    if len(selects) == 0:
        radio_option_divs = driver.find_elements(By.CSS_SELECTOR, 'div[data-product-attribute=set-radio].form-field')
        if len(radio_option_divs) > 0:
            radio_options = radio_option_divs[0]
    elif len(selects) == 1:
        if 'colour' in labels[0].text.lower() or 'matte' in labels[0].text.lower() or 'color' in labels[0].text.lower():
            color_select = Select(selects[0])
        else:
            qty_select = Select(selects[0])
    else:
        if 'colour' in labels[0].text.lower() or 'matte' in labels[0].text.lower() or 'color' in labels[0].text.lower():
            color_select = Select(selects[0])
            qty_select = Select(selects[1])
        else:
            color_select = Select(selects[1])
            qty_select = Select(selects[0])

    
    # Go through option types
    ## If a qty select exists start with that
    if qty_select:
        for index in range(1, len(qty_select.options)):
            qty_select.select_by_index(index)
            sleep(2)


            # Get Selected Quantity
            option_text = qty_select.first_selected_option.text
            qty_part = option_text.lower().split('of')[1]
            out['rings_per_bag'] = int(''.join([i for i in qty_part if i.isdigit()]))



            # Get SKU
            out['sku'] =  driver.find_element(By.CSS_SELECTOR, 'dd[data-product-sku]').text
            if out['sku'] == '':
                material_codes = {
                    "Anodized Aluminum": "AA"
                }
                out['sku'] = f"{material_codes[out['material']]}{gauge}{numerator}{denominator}-{out['rings_per_bag']}"


            # Get price
            price_section = driver.find_element(By.CSS_SELECTOR, 'div.productView-price')
            price_text = price_section.find_element(By.CSS_SELECTOR, 'span[data-product-price-without-tax]').text
            out['price'] = get_number(price_text)


            # Handle colors if applicable
            if color_select:
                for index in range(1, len(color_select.options)):
                    color_select.select_by_index(index)
                    sleep(2)
                    out['color'] = color_select.first_selected_option.text
                    yield out
            else:
                yield out
    

    ## Handle case with only color select
    elif color_select:
        for index in range(1, len(color_select.options)):
            color_select.select_by_index(index)
            sleep(2)


            # Get SKU
            out['sku'] =  driver.find_element(By.CSS_SELECTOR, 'dd[data-product-sku]').text
            if out['sku'] == '':
                material_codes = {
                    "Anodized Aluminum": "AA"
                }
                out['sku'] = f"{material_codes[out['material']]}{gauge}{numerator}{denominator}-{out['rings_per_bag']}"


            # Get price
            price_section = driver.find_element(By.CSS_SELECTOR, 'div.productView-price')
            price_text = price_section.find_element(By.CSS_SELECTOR, 'span[data-product-price-without-tax]').text
            out['price'] = get_number(price_text)

    
            # Get Color
            out['color'] = color_select.first_selected_option.text
            yield out
    

    ## Handle case with radio options
    elif radio_options:
        for option in radio_options.find_elements(By.CSS_SELECTOR,"label.form-label")[1:]:
            option.click()
            sleep(2)


            # Get SKU
            out['sku'] =  driver.find_element(By.CSS_SELECTOR, 'dd[data-product-sku]').text


            # Price
            price_section = driver.find_element(By.CSS_SELECTOR, 'div.productView-price')
            price_text = price_section.find_element(By.CSS_SELECTOR, 'span[data-product-price-without-tax]').text
            out['price'] = get_number(price_text)


            # Wire Gauge
            match = re.search('\d+\.\d+mm', option.text, re.IGNORECASE)
            if match:
                out['wire_diameter_mm'] = get_number(match.group())
                out['wire_diameter_in'] = out['wire_diameter_mm']/25.4
                

            # Inner Diameter
            match = re.search('\d+\/\d+"', option.text, re.IGNORECASE)
            if match:
                numerator, denominator = match.group().strip('"').split('/')
                out['internal_diameter_in'] = float(numerator) / float(denominator)
                out['internal_diameter_mm'] = out['internal_diameter_in'] * 25.4

            
            # Aspect ratio
            if out['internal_diameter_in'] and out['wire_diameter_in']:
                out['aspect_ratio'] = out['internal_diameter_in'] / out['wire_diameter_in']


            yield out

    
    ## Handle case with no options
    else:
        # Get price
        price_section = driver.find_element(By.CSS_SELECTOR, 'div.productView-price')
        price_text = price_section.find_element(By.CSS_SELECTOR, 'span[data-product-price-without-tax]').text
        out['price'] = get_number(price_text)


        # Get SKU
        out['sku'] =  driver.find_element(By.CSS_SELECTOR, 'dd[data-product-sku]').text
        if out['sku'] == '':
            material_codes = {
                "Anodized Aluminum": "AA"
            }
            out['sku'] = f"{material_codes[out['material']]}{gauge}{numerator}{denominator}-{out['rings_per_bag']}"


        # Get qty
        qty_match = re.search(r'\d+ rings', out['product_name'], re.IGNORECASE)
        if qty_match:
            out['rings_per_bag'] = int(''.join([i for i in qty_match.group() if i.isdigit()]))


        yield out


# Testing function if this is run as a function.
if __name__ == '__main__':

    options = Options()
    options.add_argument('--headless=new')
    chrome_path = ChromeDriverManager(version='114.0.5735.90').install()
    chrome_service = Service(chrome_path)


    with webdriver.Chrome(options=options, service=chrome_service) as driver:
        for product_page in get_product_pages():
            sleep(2)
            for product in parse_page(product_page, driver):
                log(f"found: {product}")