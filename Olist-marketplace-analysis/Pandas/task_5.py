
# important! all dependencies that you use (if you add new ones) in this class must be explicitly duplicated in this cell
import numpy as np
import pandas as pd
from dateutil.parser import parse
import datetime as dt

def task_5(reviews):
    # make a copy of the dataset so I don't have to change the original dataset
    reviews_copy = reviews.copy()
    # set the date format YYYYY-mm-dd
    format = '%Y-%m-%d'
    # setting the right boundaries on the dates
    date_start = parse('2017-04-01', dayfirst=False)
    date_finish = parse('2018-04-30', dayfirst=False)
    # date parsing: add a column with date in datetime format
    reviews_copy['date_datetime'] = reviews_copy['review_creation_date'].apply(lambda date: parse(date, dayfirst=False))
    # filter only the period we need from date_start to date_finish
    pre_need_reviews = reviews_copy[date_start <= reviews_copy['date_datetime']]
    need_reviews = pre_need_reviews[pre_need_reviews['date_datetime'] <= date_finish]
    # translate datetime into a string in the required format 
    need_reviews['date'] = need_reviews['date_datetime'].apply(lambda date: dt.datetime.strftime(date, format))
    # aggregate by day, average CSAT, rename the column
    res = need_reviews.groupby('date').agg({'review_score': 'mean'}).reset_index()
    res = res.rename({'review_score': 'csat'}, axis=1)

    return res
