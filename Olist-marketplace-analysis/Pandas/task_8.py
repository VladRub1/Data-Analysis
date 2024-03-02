
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd

def task_8(orders, items, sellers, customers):
    # merge sellers, items, orders and customers
    sellers_items = pd.merge(sellers, items, 'inner', 'seller_id')
    orders_sellers_items = pd.merge(orders, sellers_items, 'inner', 'order_id')
    data = pd.merge(customers, orders_sellers_items, 'inner', on='customer_id')
    # count the number of unique orders from the sellers
    sellers_data = data.groupby('seller_id').agg({"order_id": "nunique"}).reset_index()
    # take sellers with more than 100 orders
    seller_id_needed = sellers_data[sellers_data['order_id'] > 100]
    # taking info on the right sellers
    sellers_needed = sellers[sellers['seller_id'].isin(seller_id_needed['seller_id'].values)]
    # merge the right sellers and delivered orders
    sellers_needed_items = pd.merge(sellers_needed, items, 'inner', 'seller_id')
    orders_delivered = orders[orders['order_status'] == 'delivered']
    orders_sellers_needed_items = pd.merge(orders_delivered, sellers_needed_items, 'inner', 'order_id')
    # add customer info
    data_needed = pd.merge(customers, orders_sellers_needed_items, 'inner', on='customer_id')
    # make a flag: the sender and the customer are from different states
    data_needed['is_other_state'] = (data_needed['seller_state'] != data_needed['customer_state']).astype(int)

    # count the proportion of orders with different states of shipper and customer
    res = data_needed.drop_duplicates('order_id').groupby('seller_id').agg({"is_other_state": "mean"}).reset_index()
    res = res.rename({'is_other_state': 'share'}, axis=1).sort_values('share', ascending=False)
    res = res.iloc[:10].reset_index()

    return res
