
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd

def task_4(items, orders, customers):
    # merge orders and items
    orders_items = pd.merge(orders, items, 'inner', 'order_id')
    # aggregate info, get sum of price, shipping cost, number of items in the order
    grouped_ord = orders_items.groupby('order_id').agg({'price': 'sum', 'freight_value': 'sum', 'order_item_id': 'count'}).reset_index()
    # counting the average price
    price_mean = grouped_ord['price'].mean()
    # calculating the average shipping cost
    freight_value_mean = grouped_ord['freight_value'].mean()
    # calculate the average number of items in an order
    order_item_id_mean = grouped_ord['order_item_id'].mean()
    
    # combining orders and customers
    orders_customers = pd.merge(orders, customers, 'inner', 'customer_id')
    # group by customer_unique_id, count the number of unique customer_id
    customers_data = orders_customers.groupby('customer_unique_id').agg({'customer_id': 'nunique'}).reset_index()
    # calculate the average number of purchases per user
    customer_id_mean = customers_data['customer_id'].mean()

    return price_mean, freight_value_mean, order_item_id_mean, customer_id_mean
