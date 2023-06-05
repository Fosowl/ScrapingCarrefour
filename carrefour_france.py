import os
import sys
import requests
import argparse
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import csv
import pandas as pd

website = "https://www.carrefour.fr"
exclude_words = ["plat", "bébé", "Plat", "Salade", "INNOVATION", "Kit", "Croquettes", "Pizza", "Nouilles", "Nems", "Soupe", "halal", "Taboulé", "Box", "Chips", "Kebab", "Poires", "Raisins"]

parser = argparse.ArgumentParser(
                    prog='scraper',
                    description='scraping french carrefour using selenium')
parser.add_argument('--url', type=str) 
parser.add_argument('--categorie', type=str) 

args = parser.parse_args()

headers = {
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
}

def clean_price(s):
    if s is None: return None
    match = re.search(r'\d+\.\d+', s)
    if match:
         return float(match.group())
    return s

def find_price(trunk):
    i = 0
    while i < len(trunk):
        if '€' in trunk[i] and "/" not in trunk[i]:
            return trunk[i-1]
        i += 1
    return None

def find_price_per_kg(trunk):
    i = 0
    while i < len(trunk):
        if '€' in trunk[i] and "/" in trunk[i]:
            return trunk[i]
        i += 1
    return None

def find_name(trunk):
    for chunk in trunk:
        has_euros = False
        has_cap = False
        for word in chunk.split(" "):
            if '€' in word:
                has_euros = True
            if word.isupper():
                has_cap = True
        if has_euros == False and has_cap == True:
            return chunk
    return "Unknown"

def save_to_csv(data, csv_path):
    frame = pd.DataFrame(data=data)
    with open(csv_path, 'a') as f:
        frame.to_csv(f, header=False)

def check_exclusion(name):
    for word in exclude_words:
        if word in name:
            return True
    return False

def search_parser(elements, categorie):
    names = []
    prices = []
    prices_kg = []

    for e in elements:
        trunk = e.text.split('\n')
        name = find_name(trunk)
        price = clean_price(find_price(trunk))
        price_per_kg = clean_price(find_price_per_kg(trunk))

        if check_exclusion(name) == True:
            continue
        if name and price and price_per_kg:
            names.append(name)
            prices.append(price)
            prices_kg.append(price_per_kg)
        #print(f"name <{name}>, price <{price}> price per kg <{price_per_kg}>")
    categ = [categorie]*len(names)
    data = {'name': names, 'prices': prices, 'prices_per_kg': prices_kg, 'categorie': categ}
    return data

def check_end(pagination) -> bool:
    if len(pagination) == 0:
        return True
    if "SUIVANTS" in pagination[0].text == False:
        return True
    return False

def main():
    url = args.url
    print("using chrome...")
    options = webdriver.ChromeOptions()
    #options.add_argument('headless')
    driver = webdriver.Chrome(options=options) 
    driver.set_window_size(500, 800)
    driver.get(url) 
    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-grid-item"))
        )
        idx = 0
        while idx < 100:
            print("scraping webpage...")
            elements = driver.find_elements(By.CLASS_NAME, 'product-grid-item')
            pagination = driver.find_elements(By.ID, 'data-voir-plus') 
            if check_end(pagination) == True:
                break
            print("parsing...")
            results = search_parser(elements, categorie=args.categorie)
            save_to_csv(results, './france.csv')
            idx += 1
            page = f"{url}?noRedirect=1&page={idx}"
            driver.get(page) 
            print("switched to next page", page)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()

#['Fraîcheur', '2 jrs+', "Filets de poulet jaune CARREFOUR CLASSIC'", '15.35 € / KG', '(53)', '7,67', '€']

#['Eau minérale naturelle OGEU', '6x50cL', '0.70 € / L', '2,10', '€', 'Trouver moins cher']

# ['Pommes Canada grises vrac FILIERE QUALITE CARREFOUR', '1Kg', '2.79 € / KG', 'FRANCE', '2,79', '€']