import pandas as pd
from api.utils import create_article_dicts, perform_query
import numpy as np
import time

import config

def scrape(n_items_requested: int, base_url: str, params: dict) -> list: #TODO: rename this function. scrape is too broad
    """Scrapes Guardian API for the number of items requested, and returns a list, each element of which is a lists of dicts

    Args:
        n_items_requested (int): number of items to be returned
        base_url (str): which API endpoint to use
        params (dict): args that will be passed to Guardian API

    Returns:
        list: each element of this list contains info from one API call.
    """
    dict_list = []
    num_of_iterations = n_items_requested // config.PAGE_SIZE

    for n in np.arange(1, num_of_iterations+1):
        if n % 5 == 0:
            time.sleep(1)
        params['page'] = n
        query_jsons = perform_query(base_url, params)
        article_dicts = create_article_dicts(query_jsons)
        dict_list.append(article_dicts)

    #TODO: handle case where page size does not perfectly divide n_items_requested

    return dict_list

def flatten_dict_list(dict_list: list) -> list:
    """Flattens the list of lists that contain info about each article. This will make converting into a pandas DataFrame easier

    Args:
        dict_list (list): a list of lists. Each element is a list of dicts and corresponds to the results returned by one API call

    Returns:
        list: flattened_list. Each element in list will be a dict for an article
    """

    flat_list = []
    for api_response in dict_list: #using a nested loop rather than list comprehension for easier readability
        for article in api_response:
            flat_list.append(article)

    return flat_list

def store_scraping_results(articles: list, start_date: str, to_date: str):
    """Converts the scraped article information into a Pandas dataframe, pickles it, and then stores it.

    Args:
        articles (list): this is the output of flatten_dict_list(). Each element in this list is a dict containing information about one article
        start_date (str): start of time range for info that is present in articles. Used for naming the pickle file
        to_date (str): end of time range for info that is present in articles. Used for naming the pickle file
    """
    file_name = f"\\articles_{start_date}_to_{to_date}.pkl"
    file_location = config.DATA_PATH + file_name

    df = pd.DataFrame(articles)
    df.to_pickle(file_location)

#TODO: wrapper function that calls scrape(), flatten_dict_list(), and store_scraping_results() in a loop. Each iteration of the loop will have different
#values for from-date and to-date

    """
    For each month:
        Create param values for from-date and to-date
        scrape()
        flatten_dict_list()
        store_scraping_results()
    """

#TODO: function to combine all pickled dataframes into one dataframe.
