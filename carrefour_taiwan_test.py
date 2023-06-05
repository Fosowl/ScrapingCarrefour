from bs4 import BeautifulSoup
import requests
from functions import carrefourtw_dict_to_csv
# Categories
url = "https://online.carrefour.com.tw/en/fresh--goods?start=3312#"
html = requests.get(url).text
soup = BeautifulSoup(html, 'html.parser')

categories_html = soup.find(class_="commodity-classification")

main_categories_html = categories_html.find_all("p")
main_categories = {}

for i in main_categories_html:
    if i.text != "Product category":
        main_categories[i.text] = []

main_categories_keys = list(main_categories.keys())
subcategories_html = categories_html.find_all("ul")

for i in range(len(subcategories_html)):
    for j in subcategories_html[i].find_all("a"):
        main_categories[main_categories_keys[i]].append({'name': j.text, 'link': j.attrs['href']})

#
base_url = "https://online.carrefour.com.tw"

products_dict = {}
for i in main_categories:
    products_dict[i] = {}
    for j in main_categories[i]:
        products_dict[i][j["name"]] = []
        j_link = base_url + j['link']
        j_html0 = requests.get(j_link).text
        j_html0_soup = BeautifulSoup(j_html0, 'html.parser')
        j_result_count = int(j_html0_soup.find(class_="resultCount number").text)

        for x in j_html0_soup.find_all(class_="hot-recommend-item line"):
            x_dict = {}
            x0 = x.find(class_="gtm-product-alink")
            x_dict["product_id"] = x0.attrs["data-pid"]
            x_dict["product_name"] = x0.attrs["data-name"]
            x_dict["product_category"] = x0.attrs["data-category"]
            x_dict["product_brand"] = x0.attrs["data-brand"]
            x_dict["product_quantity"] = x0.attrs["data-quantity"]
            x_dict["product_variant"] = x0.attrs["data-variant"]
            x_dict["product_price"] = x0.attrs["data-baseprice"]
            products_dict[i][j["name"]].append(x_dict)
        if j_result_count > 24:
            for y in range(int(j_result_count/24)):
                y_link = j_link + "?start={}#".format((y+1)*24)
                y_html = requests.get(y_link).text
                y_html_soup = BeautifulSoup(y_html, 'html.parser')

                for z in y_html_soup.find_all(class_="hot-recommend-item line"):
                    z_dict = {}
                    z0 = z.find(class_="gtm-product-alink")
                    z_dict["product_id"] = z0.attrs["data-pid"]
                    z_dict["product_name"] = z0.attrs["data-name"]
                    z_dict["product_category"] = z0.attrs["data-category"]
                    z_dict["product_brand"] = z0.attrs["data-brand"]
                    z_dict["product_quantity"] = z0.attrs["data-quantity"]
                    z_dict["product_variant"] = z0.attrs["data-variant"]
                    z_dict["product_price"] = z0.attrs["data-baseprice"]
                    products_dict[i][j["name"]].append(z_dict)
        else:
            pass

carrefourtw_dict_to_csv(products_dict, file_path='Data/carrefour_tw_fresh_products.csv')
