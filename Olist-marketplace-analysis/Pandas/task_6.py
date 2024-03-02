
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd
from dateutil.parser import parse
import datetime as dt

def task_6(reviews):
    # make a copy of the dataset so I don't have to change the original dataset
    reviews_copy = reviews.copy()

    # parsing of review and response publication dates
    reviews_copy['review_creation_date_datetime'] = reviews_copy['review_creation_date'].apply(lambda date: parse(date, dayfirst=False))
    reviews_copy['review_answer_timestamp_datetime'] = reviews_copy['review_answer_timestamp'].apply(lambda date: parse(date, dayfirst=False))
    # calculate the delta between publication and response
    reviews_copy['delta'] = reviews_copy['review_answer_timestamp_datetime'] - reviews_copy['review_creation_date_datetime']
    # convert delta to number of days
    reviews_copy['delta_days'] = reviews_copy['delta'].apply(lambda date: date.days)
    # aggregate by response day: average CSAT and number of responses
    res = reviews_copy.groupby('delta_days').agg({'review_score': 'mean', 'delta': 'count'}).reset_index()
    # rename the columns
    res = res.rename({'delta_days': 'days', 'review_score': 'csat', 'delta': 'orders'}, axis=1)

    return res
