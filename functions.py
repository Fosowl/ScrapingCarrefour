import csv
from datetime import date
import requests
import re


def check_duplicates(product_list, product_name_label):
    unique_items_label = set()
    duplicated_items = list()
    unique_items = list()
    for item in product_list:
        if item[product_name_label] not in unique_items_label:
            unique_items_label.add(item[product_name_label])
            unique_items.append(item)
        else:
            duplicated_items.append(item)
    return unique_items


def carrefourtw_dict_to_csv(dictionary, file_path):
    product_list = list()
    current_date = date.today()
    file_path_2 = file_path[:-4] + '_' + str(current_date).replace('-', '') + ".csv"
    for cat in dictionary:
        for subcat in dictionary[cat]:
            for item in dictionary[cat][subcat]:
                item["category"] = cat
                item["subcategory"] = subcat
                item["datetime"] = current_date
                product_list.append(item)
    fieldnames = list(product_list[0].keys())
    cleaned_list = check_duplicates(product_list, 'product_id')
    with open(file_path_2, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for x in cleaned_list:
            writer.writerow(x)


def carrefoursp_dict_to_csv(product_list, file_path):
    current_date = date.today()
    file_path_2 = file_path[:-4] + '_' + str(current_date).replace('-', '') + ".csv"

    with open(file_path_2, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(product_list[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for x in product_list:
            writer.writerow(x)


def filter_df(df, name, category=None, subcategory=None):
    df_name_filtered = df[df['name'].str.contains(name, case=False)]
    if df_name_filtered.empty:
        raise ValueError("Name {} not found.".format(name))
    df_final = None
    if category and subcategory:
        df_category_filtered = df_name_filtered[df_name_filtered['category'].str.contains(category, case=False)]
        df_final = df_category_filtered[df_category_filtered['subcategory'].str.contains(subcategory, case=False)]
        if df_category_filtered.empty:
            raise ValueError("Category {} not found.".format(category))
        elif df_final.empty:
            raise ValueError("Subcategory not found.")
    elif category:
        df_final = df_name_filtered[df_name_filtered['category'].str.contains(category, case=False)]
        if df_final.empty:
            raise ValueError("Category {} not found.".format(category))
    else:
        df_final = df_name_filtered[df_name_filtered['subcategory'].str.contains(subcategory, case=False)]
        if df_final.empty:
            raise ValueError("Category {} not found.".format(category))
    if 'df_final' in locals():
        return df_final
    else:
        return df_name_filtered


def scrap_eggs_sp(headers):
    url = 'https://www.carrefour.es/cloud-api/plp-food-papi/v1/supermercado/la-despensa/huevos/cat20021/c'
    json = requests.get(url, headers=headers)


def clean_taiwan_prod_quantity(string):
    numeric_values = re.findall(r'\d+', string)
    numeric_values = [int(value) for value in numeric_values]
    # Total quantity in grams
    total_quantity = 1
    for i in numeric_values:
        total_quantity *= i
    return str(total_quantity)

