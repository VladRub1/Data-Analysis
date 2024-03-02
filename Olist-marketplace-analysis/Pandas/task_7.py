
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd

def task_7(orders):
    # I make a copy of the dataset so I don't have to change the original dataset
    orders_copy = orders.copy()
    # fill NaN 2999-12-31
    orders_copy['order_delivered_customer_date'] = orders_copy['order_delivered_customer_date'].fillna('2999-12-31')

    return orders_copy
