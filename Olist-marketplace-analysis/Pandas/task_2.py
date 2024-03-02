
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd

def task_2(translation, products, items):
    # creating a dataframe with additional translations to add them
    translation_to_add = pd.DataFrame(
            [['portateis_cozinha_e_preparadores_de_alimentos', 'portable kitchen and food preparers'], 
                ['pc_gamer', 'PC Gamer']],
        columns=translation.columns)
    # supplementing the dataframe with translations, so that I can join everything I need at once
    translation_full = pd.concat([translation, translation_to_add], ignore_index=True)
    # combine products and category translations
    translation_full_products = pd.merge(products, translation_full, how='left', on='product_category_name')
    # merging the last dataset and the aitems
    items_translation_full_products = pd.merge(items, translation_full_products, how='inner', on='product_id')
    # group by seller_id and product_category_name_english, count the number of orders, 
    # sort by order count within a category
    grouped = items_translation_full_products.groupby(['seller_id', 
                                                       'product_category_name_english']
                                                       ).agg({"order_item_id": "count"}).reset_index().sort_values('order_item_id', ascending=False)
    # determine the most popular category for each seller_id
    res = grouped.groupby('seller_id').agg({'product_category_name_english': 'first'}).reset_index()
    # renaming it according to the assignment
    res = res.rename({'product_category_name_english': 'category'}, axis=1)

    return res
