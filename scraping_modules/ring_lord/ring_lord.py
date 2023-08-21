# General Imports
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

# import Selenium exceptions
import selenium.common.exceptions as sel_exceptions

# Set Constants
_REQUEST_DELAY_TIME = 5
_PAGE_LOAD_TIME = 5
_OPTION_LOAD_TIME = 5
_STARTING_LINK = 'https://theringlord.com/rings/'


# Define a logging function to log function outputs
def log(msg: str) -> None:
    now = datetime.datetime.now()
    print(f"Logged {now}: {msg}")


#########################
### Get Product Pages ###
#########################


# Define a function to get all the product pages from The Ring Lord's Website
def get_product_pages(url: str = _STARTING_LINK, request_delay_time: int = _REQUEST_DELAY_TIME, links_encountered: set = set()) -> str:
    # Ensure time between pages to scrape responsibly
    sleep(request_delay_time)

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
            yield from get_product_pages(link, request_delay_time, links_encountered)


###########################
### Parse Product Pages ###
###########################


# Define a helper function that cleans up strings
def get_number(string: str) -> float:
    return float(''.join([i for i in string if (i.isdigit() or i == '.')]))


# Define a temporary page parsing function to help with planning
def parse_page(url: str, driver:webdriver.Chrome) -> dict:
    log(f"Parsing: {url}")

        # Get the page and wait for it to load
    driver.get(url)
    sleep(_PAGE_LOAD_TIME)

    # Define the output variable
    out = {
        "time_accessed":       str(datetime.datetime.now()),
        "url":                  url,
        "sku":                  None,
        "product_name":         None,
        "material":             None,
        "price":                None,
        "currency":             None,
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


    # Get Starting Sku for future comparison
    base_sku = driver.find_element(By.XPATH, "//dt[contains(text(), 'SKU:')]/following-sibling::dd").text

    # Get the item title
    title = driver.find_element(By.CSS_SELECTOR, 'h1[class=productView-title]').text
    clean_title = ' '.join([x for x in title.split(' ') if x != ''])
    out["product_name"] = clean_title


    # Get the ring material
    bread_crumb = driver.find_element(By.CSS_SELECTOR, 'nav[aria-label=Breadcrumb]')
    material_link = bread_crumb.find_elements(By.TAG_NAME, 'li')[2]
    material = material_link.find_element(By.TAG_NAME, 'span').text
    out["material"] = material


    # Get wire diameters
    try:
        product_view = driver.find_element(By.CSS_SELECTOR, "div[class=productView]")
        wd_text = product_view.find_element(By.XPATH, "//dt[text()='Wire OD:' or text()='Wire Dia:' or text()='Wire Diameter:']/following-sibling::dd").text
        wds = wd_text.replace('"(', ' ').replace('(', ' (').replace('(', '').replace(')', '').replace('= ', '').replace('  ', ' ').split(' ')
        out["wire_diameter_gauge"] = f"{wds[2]} {wds[3]}" if 3 < len(wds) else None
        out["wire_diameter_in"] = get_number(wds[0])
        out["wire_diameter_mm"] = get_number(wds[1]) if 1 < len(wds) else None
    except sel_exceptions.NoSuchElementException:
        pass


    # Get option type
    option_container = driver.find_element(By.CSS_SELECTOR, "div.productView-options")
    option_type = None
    ## Check if size options
    try: 
        options = option_container.find_elements(By.CSS_SELECTOR, "label[data-product-attribute-value]")
        if len(options) > 0:
            option_type = 'size'
    except sel_exceptions.NoSuchElementException:
        pass
    ## Check if Color options
    try:
        options = option_container.find_elements(By.CSS_SELECTOR, "div.form-option-wrapper")
        if len(options) > 0:
            option_type = 'color'
    except sel_exceptions.NoSuchElementException:
        pass


    # Get quantity per bag
    per_option_qty = False
    try:
        product_view = driver.find_element(By.CSS_SELECTOR, "div[class=productView]")
        qty_text = product_view.find_element(By.XPATH, "//dt[contains(text(), 'Quantity:')]/following-sibling::dd").text
        qty = int(''.join([i for i in qty_text if i.isdigit()]))
        out["rings_per_bag"] = qty
    except ValueError:
        pass
    except sel_exceptions.NoSuchElementException:
        if not option_type:
            pass
        elif option_type == 'color':
            per_option_qty = True
        else:
            try:
                option_container = driver.find_element(By.CSS_SELECTOR, "div.productView-options")
                option = option_container.find_elements(By.CSS_SELECTOR, "label[data-product-attribute-value]")[0]
                per_option_qty = ('~' in option.text)
            except sel_exceptions.NoSuchElementException:
                pass


    # Get Internal Diameter of rings
    per_option_id = False
    try:
        internal_diameter = driver.find_element(By.XPATH, "//dt[contains(text(), 'Actual ID:')]/following-sibling::dd").text
        ids = internal_diameter.split(' ')
        id_in , id_mm = 0, 0
        if len(ids) < 3:
            if 'mm' in internal_diameter:
                id_mm = get_number(ids[0])
                id_in = round(id_mm * 0.0393701, 4)
            else:
                id_in = get_number(ids[0])
                id_mm = round(id_in * 25.4, 4)
        else:
            id_in = get_number(ids[0])
            id_mm = get_number(ids[1])
        out['internal_diameter_in'] = id_in
        out["internal_diameter_mm"] = id_mm
        

        # Add calculation of Aspect Ratio
        try:
            ar = id_in / out["wire_diameter_in"]
            out["aspect_ratio"] = ar
        except NameError:
            pass
        except TypeError:
            pass
    except sel_exceptions.NoSuchElementException:
        if option_type:
            try:
                option_container = driver.find_element(By.CSS_SELECTOR, "div.productView-options")
                option = option_container.find_elements(By.CSS_SELECTOR, "label[data-product-attribute-value]")[0]
                per_option_id = ' ID]' in option.text
            except sel_exceptions.NoSuchElementException:
                pass
        else:
            pass
    

    # Get iterable of options
    options = None
    if option_type == 'color':
        option_container = driver.find_element(By.CSS_SELECTOR, "div.productView-options")
        options = option_container.find_elements(By.CSS_SELECTOR, "div.form-option-wrapper")
    else:
        option_container = driver.find_element(By.CSS_SELECTOR, "div.productView-options")
        options = option_container.find_elements(By.CSS_SELECTOR, "label[data-product-attribute-value]")

    # Iterate through options
    for option in options:
        option.click()
        sleep(_OPTION_LOAD_TIME)

        # Get SKU
        sku = driver.find_element(By.XPATH, "//dt[contains(text(), 'SKU:')]/following-sibling::dd").text
        if sku != base_sku:
            out["sku"] = sku
        else:
            try:
                option_container = driver.find_element(By.CSS_SELECTOR, "div.productView-options")
                option_text = option_container.find_element(By.CSS_SELECTOR, 'span[data-option-value]').text
                sku = option_text.split(' ')[0]
                out["sku"] = sku
            except sel_exceptions.NoSuchElementException:
                sku = option.text.split(' ')[0]
                out["sku"] = sku


        # Get price currency info
        product_view = driver.find_element(By.CSS_SELECTOR, "div[class=productView]")
        price = product_view.find_element(By.CSS_SELECTOR, 'span[data-product-price-without-tax]').text
        currency = driver.find_element(By.CSS_SELECTOR, 'main').get_attribute('data-currency-code')
        out["price"] = get_number(price)
        out["currency"] = currency


        # Get product stock
        stock_text = driver.find_element(By.CSS_SELECTOR, "span[data-product-stock]").text
        if stock_text != '':
            stock = int(stock_text)
            out["bags_in_stock"] = stock
        else:
            oos_message = driver.find_element(By.CSS_SELECTOR, 'p.alertBox-column').text
            if oos_message == 'The selected product combination is currently unavailable':
                out["bags_in_stock"] = 0


        # Get Quantity if available
        if per_option_qty:
            if option_type == 'size':
                text = option.text
                if '~' in text:
                    qty_text = text.split('~')[1]
                    qty = int(''.join([i for i in qty_text if i.isdigit()]))
                    out["rings_per_bag"] = qty
            else:
                try:
                    option_container = driver.find_element(By.CSS_SELECTOR, "div.productView-options")
                    option_text = option_container.find_element(By.CSS_SELECTOR, 'span[data-option-value]').text
                    qty_text = option_text.split('~')[-1]
                    qty = int(''.join([i for i in qty_text if i.isdigit()]))
                    out["rings_per_bag"] = qty
                except ValueError:
                    pass


        # Get Internal Diamater if applicable        
        if per_option_id:
            text = option.text  
            id_in_match = re.search(r'ID ?\d?\.?\d+', text, re.IGNORECASE)
            id_mm_match = re.search(r'\( ?\d*\.?\d* ?mm ?\)', text, re.IGNORECASE)
            id_in = get_number(id_in_match.group()) if id_in_match else None
            id_mm = get_number(id_mm_match.group()) if id_mm_match else None
            out["internal_diameter_in"] = id_in
            out["internal_diameter_mm"] = id_mm

            # Add calculation of Aspect Ratio
            od_in = out["wire_diameter_in"]
            if od_in and id_in:
                ar = id_in / od_in
                out["aspect_ratio"] = ar        


        # Get Option Color if applicable
        if option_type == 'color':
            color = sku.split('-')[-1]
            out["color"] = color
        
        yield out


if __name__ == '__main__':

    options = Options()
    options.add_argument('--headless=new')
    chrome_path = ChromeDriverManager(version='114.0.5735.90').install()
    chrome_service = Service(chrome_path)

    # Start the webdriver
    with webdriver.Chrome(options=options, service=chrome_service) as driver:
        for product_page in get_product_pages():
            sleep(2)
            for product in parse_page(product_page, driver):
                log(f"found: {product}")
