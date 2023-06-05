import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import table


def check_cat(string):
    if string == 'chicken':
        return 'Chicken Breast'
    elif string == 'salmon':
        return 'Salmon'
    elif string == 'apple':
        return 'Apple'
    elif string == 'salad':
        return 'Lettuce'
    elif string == 'tomatoes':
        return 'Tomato'
    elif string == 'carrots':
        return 'Carrot'
    else:
        return string


france = pd.read_csv('Data/france.csv')
sptw = pd.read_csv('Data/final.csv')

france.drop(['index', 'price_per_kg'], axis=1, inplace=True)
france['country'] = 'France'
france['category'] = france['category'].apply(check_cat)
sptw = sptw.loc[:, ['name', 'price', 'category', 'country']]

df = pd.concat([france, sptw])
df['price'] = df['price'].str.replace(',', '.')
df['price'] = df['price'].str.extract('(\d+\.?\d*)').astype(float)
a = df.groupby('country').describe()
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
a.columns = a.columns.map('|'.join).str.strip('|')
print(a)

fig, ax = plt.subplots()

# Create a table plot using the DataFrame
table = ax.table(cellText=a.values, colLabels=a.columns, loc='center')

# Remove axis labels
ax.axis('off')
dpi = 300
# Save the table plot as a PNG image
plt.savefig('output.png', format='png', dpi=dpi, bbox_inches='tight')


b = df.groupby('category').describe()
b['index'] = b.index


fig, ax = plt.subplots()

# Create a table plot using the DataFrame
table = ax.table(cellText=b.values, colLabels=b.columns, loc='center')

# Remove axis labels
ax.axis('off')
dpi = 300
# Save the table plot as a PNG image
plt.savefig('outputb.png', format='png', dpi=dpi, bbox_inches='tight')