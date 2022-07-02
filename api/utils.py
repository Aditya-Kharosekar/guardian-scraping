import pandas as pd
import numpy as np

import config
from datetime import datetime
import dateutil.relativedelta
from itertools import compress
import requests
import logging
logging.basicConfig(level=logging.INFO)

def perform_query(base_url: str, params: dict) -> list:
    """
    Basically does one API call.
    Performs the query to the API and returns a list containing the JSON for all non-liveblog articles. Liveblogs are excluded because the
    are fundamentally different from normal news articles and because their body is harder to parse

    Args:
        base_url (str): which API endpoint will be hit (see Guardian docs for options)
        params (dict): Dict of args that will be passed to the Guardian API (see Guardian docs for options). Example: page-size, show-blocks

    Returns:
        list: list of JSON objects, one per non-liveblog article that was retrieved
    """
    params['api-key'] = config.API_KEY
    response = requests.get(
        url=base_url,
        params = params
    )
    try:
        assert response.status_code == 200

        results = response.json()['response']['results']

        to_be_removed = ['liveblog', 'crossword']
        is_not_liveblog_mask = [r['type'] not in to_be_removed for r in results]
        articles = list(compress(results, is_not_liveblog_mask))

        return articles
    except:
        logging.info("Page number: ", params['page'] + "." + 
        "API call did not return a status code of 200. Most probably, there are no more articles to gather" + 
        "for the provided criteria")

def create_article_dicts(articles: list) -> list:
    """For each article, extracts required key-value pairs from its JSON object, and stores them into a dict. 
    Returns a list of such dicts, one for each article

    Args:
        articles (list): JSON objects containing data about articles retrieved from API

    Returns:
        list: list of dictionaries. Each element in list contains information about one article. Will be used to create dataframe later
    """
    if not articles:
        logging.info('No articles in this batch')
        return []
    
    dict_list = []
    for article in articles:
        current_dict = {}

        try:

            #would ideally like to parametrize the keys that I'm extracting but not sure how to programmatically handle nested keys
            current_dict['id'] = article['id']
            current_dict['sectionName'] = article['sectionName']
            current_dict['webTitle'] = article['webTitle']
            current_dict['webUrl'] = article['webUrl']
            current_dict['bodyContent'] = article['blocks']['body'][0]['bodyTextSummary']
            current_dict['webPublicationDate'] = article['webPublicationDate']
        
            dict_list.append(current_dict)
        except:
            print(article)
    
    return dict_list

def get_end_of_current_month(current_date: datetime.date) -> datetime.date:
    """Used when specifying from-date and to-date. Returns a datetime.date object for the last day of the specified month

    Args:
        current_month (datetime.date):
    """
    return (current_date.replace(day=1) + dateutil.relativedelta.relativedelta(months=+1, seconds=-1)).date()

def get_start_of_next_month(current_date: datetime.date) -> datetime.date:
    """Used when specifying from-date and to-date. Returns a datetime.date object for the first day of the next month

    Args:
        current_month (datetime.date): 
    """
    return current_date.replace(day=1) + dateutil.relativedelta.relativedelta(months=+1)

def convert_datetime_to_string_yyyymmdd(current_date: datetime.date) -> str:
    """Returns the current_date in YYYY-MM-DD string format

    Args:
        current_date (datetime.date):
    """
    return current_date.strftime('%Y-%m-%d')