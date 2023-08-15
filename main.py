# General imports
import time
import json
from mysql.connector import MySQLConnection, Error


# Import modules
import scraping_modules.ring_lord.ring_lord as ring_lord
import scraping_modules.metal_designz.metal_designz as metal_designz


# Selenium Scraping imports
from selenium import webdriver  
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


# This helper function is to convert missing values to NULL
def n2n(obj, data_type):
    if not obj:
        return 'NULL'
    else:
        if data_type=="VARCHAR":
            return f"'{obj}'"
        if data_type == "FLOAT":
            return obj
        if data_type == "INT":
            return obj if obj < 100000 else -1


# Write a helper function for adding a product to 
def add_product(product: dict) -> str:
    # Write insert query
    query = f"""INSERT INTO 
    scraped_product_info
    VALUES (
        {n2n(product['time_accessed'],        "VARCHAR")},
        {n2n(product['url'],                  "VARCHAR")},
        {n2n(product['sku'],                  "VARCHAR")},
        {n2n(product['product_name'],         "VARCHAR")},
        {n2n(product['material'],             "VARCHAR")},
        {n2n(product['price'],                "FLOAT")},
        {n2n(product['currency'],             "VARCHAR")},
        {n2n(product['wire_diameter_in'],     "FLOAT")},
        {n2n(product['wire_diameter_mm'],     "FLOAT")},
        {n2n(product['wire_diameter_gauge'],  "VARCHAR")},
        {n2n(product['internal_diameter_in'], "FLOAT")},
        {n2n(product['internal_diameter_mm'], "FLOAT")},
        {n2n(product['aspect_ratio'],         "FLOAT")},
        {n2n(product['color'],                "VARCHAR")},
        {n2n(product['bags_in_stock'],        "INT")},
        {n2n(product['rings_per_bag'],        "INT")}
    );"""

    try:
        # Connect to database
        with open('envs.json', 'r') as json_file:
            envs = json.loads(json_file.read())
            db_creds = envs['db_creds']
        conn = MySQLConnection(**db_creds)

        # Run Query
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
    
    except Exception as e:
        print(query)
        raise e

    finally:
        # Close connection
        cursor.close()
        conn.close()


# Start driver
options = Options()
options.add_argument('--headless=new')
chrome_path = ChromeDriverManager(version='114.0.5735.90').install()
chrome_service = Service(chrome_path)
with webdriver.Chrome(options=options, service=chrome_service) as driver:
    
    # Parse Metal Designz Pages
    for page_link in metal_designz.get_product_pages():
        time.sleep(2)
        for product in metal_designz.parse_page(page_link, driver):
            add_product(product)

    # Parse Ring Lord Pages
    for page_link in ring_lord.get_product_pages():
        time.sleep(2)
        for product in ring_lord.parse_page(page_link, driver):
            add_product(product)