from email.mime import base
import pandas as pd
from api.utils import *
import numpy as np
import time
import dateutil.relativedelta
import glob
from datetime import datetime

import config

def get_n_articles(n_items_requested: int, base_url: str, params: dict, sleep_frequency: int) -> list:
    """Scrapes Guardian API for the number of items requested, and returns a list, each element of which is a lists of dicts.
    Will call perform_query to do the actual API call

    Args:
        n_items_requested (int): number of items to be returned
        base_url (str): which API endpoint to use
        params (dict): args that will be passed to Guardian API
        sleep_frequency (int): sleep for 1 second after these many API calls

    Returns:
        list: each element of this list contains info from one API call.
    """
    dict_list = []
    num_of_iterations = n_items_requested // config.PAGE_SIZE

    for n in np.arange(1, num_of_iterations+1):
        if n % sleep_frequency == 0:
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
    file_name = f"\\monthly\\articles_{start_date}_to_{to_date}.pkl"
    file_location = config.DATA_PATH + file_name

    df = pd.DataFrame(articles)
    df.to_pickle(file_location)

def scrape(starting_month: str, ending_month: str, articles_per_month: int, base_url: str, base_params: dict):
    """This is the user-facing function. User only needs to specify certain properties for how they want the article scraping to go,
    and this function will handle all the logic.

    Args:
        starting_month (str): beginning of range you want to scrape articles from. Inclusive. In YYYY-MM format. Example is '2018-11'
        ending_month (str): End of range you want to scrape articles from. Exclusive. In YYYY-MM format. Example is '2019-03'
        articles_per_month (int): number of articles per month that you want to scrape
        base_url (str): which API endpoint do you want to hit
        base_params (dict): common args for the API endpoint. These will be applied to each API call
    """
    starting_month_dt = datetime.fromisoformat(starting_month + "-01").date()
    ending_month_dt = datetime.fromisoformat(ending_month + "-01").date()

    difference = dateutil.relativedelta.relativedelta(ending_month_dt, starting_month_dt)
    num_of_months = (difference.years * 12) + difference.months
    
    start_of_range = starting_month_dt
    for m in np.arange(num_of_months):
        end_of_range = get_end_of_current_month(start_of_range)

        base_params['from-date'] = convert_datetime_to_string_yyyymmdd(start_of_range)
        base_params['to-date'] = convert_datetime_to_string_yyyymmdd(end_of_range)

        print("Current time range: ", base_params['from-date'], base_params['to-date'])
        current_month_articles = get_n_articles(articles_per_month, base_url, base_params, sleep_frequency=5)
        flattened = flatten_dict_list(current_month_articles)
        store_scraping_results(flattened, base_params['from-date'], base_params['to-date'])

        start_of_range = get_start_of_next_month(end_of_range)

def combine_pickles_into_master_dataframe():
    """After scraping is done and the individual pickle files have been created, this will combine all of them
    into one pickle object, which can be read using Pandas.

    Stores the master dataframe as a pickle
    """
    pickle_files = glob.glob(config.DATA_PATH + "\\monthly\\*.pkl")
    contents = [pd.read_pickle(file) for file in pickle_files]

    # for file in pickle_files:
    #     current_file = pd.read_pickle(file)
    #     contents.append(current_file)

    combined = pd.concat(contents, ignore_index=True)
    file_location = config.DATA_PATH + f"\\combined\\guardian_articles.pkl"

    combined.to_pickle(file_location)