
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd

def task_1(translation, items, products):
    # creating a dataframe with additional translations to add them
    translation_to_add = pd.DataFrame(
            [['portateis_cozinha_e_preparadores_de_alimentos', 'portable kitchen and food preparers'], 
             ['pc_gamer', 'PC Gamer']],
        columns=translation.columns)
    # supplementing the dataframe with translations, so that I can join everything I need at once
    translation_full = pd.concat([translation, translation_to_add], ignore_index=True)
    # checking that there are 2 more categories in the translations
    assert translation_full.shape[0] == translation.shape[0] + 2

    # counting the average price of products
    items_price = items.groupby('product_id').agg({'price': 'mean'}).reset_index()
    # join aggregate info on products and aitems
    products_and_items = pd.merge(products, items_price, how='inner', on='product_id')
    # add translation. LEFT JOIN, because the product_category_name field is NULL
    products_items_and_translation = pd.merge(products_and_items, translation_full, how='left', on='product_category_name')
    # final aggregations
    res = products_items_and_translation.groupby('product_category_name_english').agg({'product_id': 'nunique', 'price': 'mean'}).reset_index()
    # rename as required
    res = res.rename({'product_category_name_english': 'category',
                      'product_id': 'products'}, axis=1)
    
    return res
