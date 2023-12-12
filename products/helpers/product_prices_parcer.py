# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json

import requests
from bs4 import BeautifulSoup

PAGE_URL = 'https://index.minfin.com.ua/ua/'
PRODUCT_CATEGORIES_PAGE = 'markets/wares/prods/'
PRODUCTS_CATEGORIES_LIST_selector = '#idx-content ul[type]'
PRODUCT_ITEM_selector = 'li'
PRODUCT_CATEGORY = 'a'
PRODUCT_LIST_selector = 'div>a'

PRODUCT_PRICE_TABLE = '.prodsview table'

TABLE_ROW = 'tr'
TABLE_HEADER = 'th'
TABLE_COLUMN = 'td'
TABLE_HEADER_PRODUCT_NAME = 'a'

HEAD_ROW = 'wp-head'
INNER_ROW = 'wp-inner'
FOOTER_ROW = 'wp-foot'

def parce_page():
    response = requests.get(PAGE_URL + PRODUCT_CATEGORIES_PAGE)
    soup = BeautifulSoup(response.text, 'lxml')
    categories_list = soup.select(PRODUCTS_CATEGORIES_LIST_selector)
    categories = categories_list[0].select(PRODUCT_ITEM_selector)
    categories.reverse()
    product_list = []
    for category in categories:
        category_name = get_category_name(category)
        products = get_category_products(category)
        for product in products:
            product_page = open_product_page(product)
            products_list = parce_product_page(product_page)
            for p in products_list:
                print(p)
                p['category'] = category_name
            product_list.extend(products_list)

    return product_list

    # write_to_file(product_list)



def get_category_name(category):
    return category.findChild(PRODUCT_CATEGORY).text


def get_category_products(category):
    return category.select(PRODUCT_LIST_selector)


def open_product_page(product):
    product_url = product.get('href')
    response = requests.get(PAGE_URL + product_url)
    return BeautifulSoup(response.text, 'lxml')


def get_product_name(product):
    product_url = product.get('href')
    response = requests.get(PAGE_URL + product_url)
    return BeautifulSoup(response.text, 'lxml')


def parce_product_page(product_page):
    product_table = product_page.select(PRODUCT_PRICE_TABLE)[0]
    tables_rows = product_table.select(TABLE_ROW)
    products_map = {}

    current_unit = ''
    current_weight = ''
    current_product = ''
    for row in tables_rows:
        first_column = row.findChild()
        classes = first_column.get('class')
        if classes is None:
            row_type = HEAD_ROW
        else:
            row_type = classes[0]
        products_count = 0
        if row_type == HEAD_ROW:
            for index, child in enumerate(row.children):
                if index == 0:
                    current_product = child.text
                    if products_map.get(current_product) is None:
                        products_map[current_product] = {
                            'average': [],
                            'shops': []
                        }
                if index == 1:
                    characteristic = child.text.split('\xa0')
                    current_weight = characteristic[0]
                    current_unit = characteristic[1]
        if row_type == INNER_ROW:
            shop_name = ''
            shop_price = ''
            for index, child in enumerate(row.children):
                if index == 0:
                    shop_name = child.text
                if index == 1:
                    shop_price = child.select('big')[0].text
            shop = {
                'shop_name': shop_name,
                'shop_price': shop_price,
                'unit': current_unit,
                'weight': current_weight
            }
            products_map.get(current_product)['shops'].append(shop)
        if row_type == FOOTER_ROW:
            shop_price = row.select('th big')[0].text
            products_map.get(current_product)['average'].append({'unit': current_unit, 'weight': current_weight, 'price': shop_price})
    print(products_map.get(current_product))
    products_list1 = []
    for key in products_map:
        products_list1.append({
            'name': key,
            'average': products_map.get(key).get('average'),
            'shops': products_map.get(key).get('shops')
        })
    return products_list1

def write_to_file(product_list):
    print('write_to_file')
    with open('products_price.json', 'w') as fp:
        fp.write(json.dumps(product_list, ensure_ascii=False))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parce_page()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
