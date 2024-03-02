
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd

def task_3(orders, customers, items):
    # take only orders that have been delivered
    delivered_orders = orders[orders['order_status'] == 'delivered']
    # merge delivered orders with aitems
    delivered_orders_items = pd.merge(delivered_orders, items, 'inner', 'order_id')
    # merge past dataset with clients
    delivered_orders_items_customers = pd.merge(delivered_orders_items, customers)
    # group info by state 
    grouped_data = delivered_orders_items_customers.groupby('customer_state').agg({"price": "sum", "freight_value": "sum"}).reset_index()
    # get the total amount of orders: item price + shipping
    grouped_data['total_amt'] = grouped_data['price'] + grouped_data['freight_value']
    # get a share of every state
    grouped_data['perc'] =  grouped_data['total_amt'] / grouped_data['total_amt'].sum()
    # rename it and take only the columns I need
    res = grouped_data.rename({'customer_state': 'state'}, axis=1)
    res = res[['state', 'perc']]

    return res
