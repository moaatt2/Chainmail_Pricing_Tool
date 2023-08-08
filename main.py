# General imports
import time
import json
from mysql.connector import MySQLConnection, Error


# Import modules
import scraping_modules.ring_lord.ring_lord as ring_lord


# Selenium Scraping imports
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


# This helper function is to convert missing values to NULL
def n2n(obj, q=False):
    if obj and not q:
        return obj
    elif obj and q:
        return f"'{obj}'"
    else:
        return 'NULL'


# Write a helper function for adding a product to 
def add_product(product: dict) -> str:
    # Write insert query
    query = f"""INSERT INTO 
    scraped_product_info
    VALUES (
        '{product['time_accessed']}',
        '{product['url']}',
        {n2n(product['sku'], True)},
        {n2n(product['product_name'], True)},
        {n2n(product['material'], True)},
        {n2n(product['price'])},
        {n2n(product['currency'], True)},
        {n2n(product['wire_diameter_in'])},
        {n2n(product['wire_diameter_mm'])},
        {n2n(product['wire_diameter_gauge'], True)},
        {n2n(product['internal_diameter_in'])},
        {n2n(product['internal_diameter_mm'])},
        {n2n(product['aspect_ratio'])},
        {n2n(product['color'], True)},
        {n2n(product['bags_in_stock'])},
        {n2n(product['rings_per_bag'])}
    );"""

    print(query)

    # Connect to database
    with open('envs.json', 'r') as json_file:
        envs = json.loads(json_file.read())
        db_creds = envs['db_creds']
    conn = MySQLConnection(**db_creds)

    # Run Query
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()

    # Close connection
    cursor.close()
    conn.close()


# Start driver
options = Options()
options.add_argument('--headless=new')
chrome_path = ChromeDriverManager(version='114.0.5735.90').install()
chrome_service = Service(chrome_path)
with webdriver.Chrome(options=options, service=chrome_service) as driver:

    # Parse Ring Lord Pages
    for page_link in ring_lord.get_product_pages():
        time.sleep(2)
        for product in ring_lord.parse_page(page_link, driver):
            add_product(product)