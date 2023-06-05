import pandas as pd
from functions import filter_df, clean_taiwan_prod_quantity

cf_spain_df = pd.read_csv('Data/carrefour_spain_fresh_products_20230605.csv')
cf_taiwan_df = pd.read_csv('Data/carrefour_tw_fresh_products_20230605.csv')
cf_taiwan_df.rename(columns={'product_name': 'name'}, inplace=True)
# Clean
cf_taiwan_df = cf_taiwan_df.drop(['product_category', 'product_brand', 'product_quantity'], axis=1)
# Categories
spain_categories = cf_spain_df['category'].unique().tolist()
taiwan_categories = cf_taiwan_df['category'].unique().tolist()

# Subcategories
spain_subcategories = cf_spain_df['subcategory'].unique().tolist()
taiwan_subcategories = cf_taiwan_df['subcategory'].unique().tolist()

#

spanish_products = [('Manzana', 'Frutas'),
                    ('Pechuga de pollo', 'Carnicería'),
                    ('Salmón', 'Pescadería'),
                    ('Lechuga', 'Verduras y hortalizas'),
                    ('Tomate', 'Verduras y hortalizas'),
                    ('Plátano', 'Frutas'),
                    ('Zanahoria', 'Verduras y hortalizas'),
                    ('Queso', 'Charcutería y Quesos al Corte')]

taiwan_products = [('Apple', 'Vegetables'),
                   ('Chicken Breast', 'Meat / Soup'),
                   ('Salmon', 'Seafood'),
                   ('Lettuce', 'Vegetables'),
                   ('Tomato', 'Vegetables'),
                   ('Banana', 'Desserts'),
                   ('Carrot', 'Vegetables'),
                   ('Cheese', 'Appetizers')]

sp_en_cat_translations = {
    'Carnicería': 'Butcher',
    'Pescadería': 'Fishmonger',
    'Frutas': 'Fruits',
    'Verduras y hortalizas': 'Vegetables',
    'Panadería Tradicional': 'Traditional Bakery',
    'Charcutería': 'Delicatessen',
    'Charcutería y Quesos al Corte': 'Delicatessen and Cut Cheeses',
    'Quesos': 'Cheeses',
    'Platos Preparados Cocinados': 'Prepared Cooked Dishes'
}

taiwan_selection_df = pd.DataFrame(columns=cf_taiwan_df.columns)

for i in taiwan_products:
    x_df = filter_df(cf_taiwan_df, i[0], i[1])
    x_df['category'] = i[0]
    x_df['country'] = 'Taiwan'
    taiwan_selection_df = pd.concat([taiwan_selection_df, x_df])
taiwan_selection_df['product_variant'] = taiwan_selection_df['product_variant'].apply(clean_taiwan_prod_quantity)
taiwan_selection_df.rename(columns={'category': 'category',
                                    'product_id': 'id',
                                    'product_variant': 'measure_unit',
                                    'product_price': 'price'}, inplace=True)
taiwan_selection_df['price'] = taiwan_selection_df['price'] * 0.03
spain_selection_df = pd.DataFrame(columns=cf_spain_df.columns)
spain_selection_df.rename(columns={'category': 'category2'}, inplace=True)
spain_selection_df.rename(columns={'product_name': 'category'}, inplace=True)

for i in spanish_products:
    x_df = filter_df(cf_spain_df, i[0], i[1])
    x_df['product_name'] = taiwan_products[spanish_products.index(i)][0]
    x_df['category'] = sp_en_cat_translations[i[1]]
    x_df.rename(columns={'category': 'category2'}, inplace=True)
    x_df.rename(columns={'product_name': 'category'}, inplace=True)
    x_df['country'] = 'Spain'
    spain_selection_df = pd.concat([spain_selection_df, x_df])

df_final = pd.concat([spain_selection_df, taiwan_selection_df], ignore_index=True)
df_final.to_csv('Data/final.csv', index=False)

spain_selection_df.to_csv('Data/spain_selection.csv', index=False)
taiwan_selection_df.to_csv('Data/taiwan_selection.csv', index=False)