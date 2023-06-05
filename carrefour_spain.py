import requests
from time import sleep
from datetime import date
from seleniumwire import webdriver
from functions import carrefoursp_dict_to_csv, check_duplicates
url_carrefour_base = "https://www.carrefour.es/cloud-api/plp-food-papi/v1"
url_carrefour_fresh_products = "https://www.carrefour.es/cloud-api/plp-food-papi/v1/supermercado/productos-frescos/cat20002/c"
url_carrefour_categories_api = "https://www.carrefour.es/api/unified_menu/005704/json/"
url_carrefour_supermercado = "https://www.carrefour.es/supermercado"
url_carrefour_food_api = "https://www.carrefour.es/cloud-api/plp-food-papi/v1"
url_carrefour_non_food_api = "https://www.carrefour.es/cloud-api/plp-nonfood-papi/v1"

current_date = date.today()
# Selenium
options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe' #Only for server
driver = webdriver.Firefox(options=options)#, executable_path=r'/usr/local/bin/geckodriver')
driver.get(url_carrefour_categories_api)
headers = {}
for request in driver.requests:
    if request.url == url_carrefour_categories_api:
        for i in request.headers:
            headers[i] = request.headers[i]
    else:
        continue
driver.close()
categories_json_request = requests.get(url_carrefour_fresh_products, headers=headers)

if categories_json_request.status_code not in range(200, 400):
    raise Exception("Invalid http response.\n ERROR CODE {}".format(categories_json_request.status_code))


categories_json = categories_json_request.json()

# Scraping
categories = {}
for cat in categories_json['child_links']['items']:
    if cat['id'] in ['cat21078000']:
        pass
    else:
        categories[cat['display_name']] = []
        cat_url = url_carrefour_base + cat['url']
        subcategories_json_request = requests.get(cat_url, headers=headers)

        if subcategories_json_request.status_code not in range(200, 400):
            raise Exception("Invalid http response.\n ERROR CODE {}".format(subcategories_json_request.status_code))

        subcategories_json = subcategories_json_request.json()

        for subcategory in subcategories_json['child_links']['items']:
            categories[cat['display_name']].append({'name': subcategory['display_name'], 'url': subcategory['url']})

products_list = []
for cat in categories:
    for subcategories in categories[cat]:
        subcategory_url = url_carrefour_base + subcategories['url']
        subcategories_json_request = requests.get(subcategory_url, headers=headers)

        if subcategories_json_request.status_code not in range(200, 400):
            raise Exception("Invalid http response.\n ERROR CODE {}".format(subcategories_json_request.status_code))

        subcategories_json = subcategories_json_request.json()

        for product in subcategories_json['results']['items']:
            list_item = dict()
            list_item['name'] = product['name']
            list_item['id'] = product['product_id']
            list_item['category'] = cat
            list_item['subcategory'] = subcategories['name']
            list_item['measure_unit'] = product['measure_unit']
            list_item['price'] = product['price']
            list_item['price_per_unit'] = product['price_per_unit']
            list_item['sell_pack_unit'] = product['sell_pack_unit']
            list_item['datetime'] = current_date
            products_list.append(list_item)

        if subcategories_json['results']['pagination']['page_size'] < subcategories_json['results']['pagination']['total_results']:
            total_results = subcategories_json['results']['pagination']['total_results']
            total_pages = int((total_results/subcategories_json['results']['pagination']['page_size']))

            for page in range(total_pages):
                if page != 0:
                    subcategory_page_url = subcategory_url + "?offset={}".format(page*24)
                    subcategories_page_json_request = requests.get(subcategory_page_url, headers=headers)

                    if subcategories_page_json_request.status_code not in range(200, 400):
                        raise Exception(
                            "Invalid http response.\n ERROR CODE {}".format(subcategories_page_json_request.status_code))

                    subcategories_page_json = subcategories_page_json_request.json()

                    for product in subcategories_page_json['results']['items']:
                        list_item = dict()
                        list_item['name'] = product['name']
                        list_item['id'] = product['product_id']
                        list_item['category'] = cat
                        list_item['subcategory'] = subcategories['name']
                        list_item['measure_unit'] = product['measure_unit']
                        list_item['price'] = product['price']
                        list_item['price_per_unit'] = product['price_per_unit']
                        list_item['sell_pack_unit'] = product['sell_pack_unit']
                        list_item['datetime'] = current_date
                        products_list.append(list_item)

cleaned_product_list = check_duplicates(products_list, 'id')

carrefoursp_dict_to_csv(products_list, file_path='Data/carrefour_spain_fresh_products.csv')
