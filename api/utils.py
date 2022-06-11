import pandas as pd
import numpy as np

import config
from itertools import compress
import requests
import logging
logging.basicConfig(level=logging.INFO)

def perform_query(base_url: str, params: dict) -> list:
    """Performs the query to the API and returns a list containing the JSON for all non-liveblog articles. Liveblogs are excluded because the
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
    assert response.status_code == 200

    results = response.json()['response']['results']
    is_not_liveblog_mask = [r['type'] != 'liveblog' for r in results]
    articles = list(compress(results, is_not_liveblog_mask))
    return articles

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
        return None
    
    dict_list = []
    for article in articles:
        current_dict = {}

        #would ideally like to parametrize the keys that I'm extracting but not sure how to programmatically handle nested keys
        current_dict['id'] = article['id']
        current_dict['sectionName'] = article['sectionName']
        current_dict['webTitle'] = article['webTitle']
        current_dict['webUrl'] = article['webUrl']
        current_dict['bodyContent'] = article['blocks']['body'][0]['bodyTextSummary']
        current_dict['webPublicationDate'] = article['webPublicationDate']
        
        dict_list.append(current_dict)
    
    return dict_list
