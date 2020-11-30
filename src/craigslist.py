from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import math
from datetime import date
from sqlalchemy import create_engine
import boto3
from io import BytesIO

# Parameters
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}

# filter out the non-portland results
portland_url_mask = "https://portland."
portland_url_slice = 17
listings_per_page = 120

# (ADU)-"this is not adu"-"this is not an adu unit"|("accessory dwelling unit")|("In-law")|("granny flat")|("backyard cottage")|
adu_search_url = "https://portland.craigslist.org/search/apa?query=%28ADU%29-%22this+is+not+adu%22-%22this+is+not+an+adu+unit%22%7C%28%22accessory+dwelling+unit%22%29%7C%28%22In-law%22%29%7C%28%22granny+flat%22%29%7C%28%22backyard+cottage%22%29%7C&availabilityMode=0&sale_date=all+dates"


# Functions
def get_page_count_of_results(search_results_soup, listings_per_page):
    """Returns the total number of pages of search results

    Parameters
    -----------
    search_results_soup : bs4.BeautifulSoup
        The BeautifulSoup object of the search results
    listings_per_page : int
        The maximum number of results shown on a single page of results

    Returns
    -------
    total_pages : int
        The total number of search results pages on craigslist for the search
    """
    total_results = int(search_results_soup.find("span", class_="totalcount").text)
    total_pages = math.ceil(total_results / listings_per_page)
    return total_pages


def get_list_of_all_urls_to_scrape(base_url, headers, listings_per_page):
    """Gets the URLs for each page of results needed to be scraped

    Parameters
    ----------
    base_url : str
        The URL of the first page of search results
    headers : dict
        The headers for the get request
    listings_per_page : int
        The maximum number of results shown per page of results

    Returns
    -------
    urls_to_scrape : list
        List containing the url for each page of results that need to be scraped
    """
    search_results = get(url=base_url, headers=headers)
    search_results_soup = BeautifulSoup(search_results.content, "html.parser")

    total_pages = get_page_count_of_results(
        search_results_soup=search_results_soup, listings_per_page=listings_per_page
    )

    urls_to_scrape = [base_url]
    if total_pages == 1:
        return urls_to_scrape
    else:
        for page_number in list(range(1, total_pages)):
            new_url = base_url + "&s={}".format(120 * page_number)
            urls_to_scrape.append(new_url)
    return urls_to_scrape


def scrape_craigslist_search_result(result):
    """Scrape data from an individual listing

    Parameters
    ----------
    results : bs4.Tag
        The bs4.Tag object containing the data for an individual post

    Returns:
    out_df : pd.DataFrame (dim = 1 x 5)
        DataFrame with one row and five columns [link, date, price, housing_info, neighborhood]
        containing the data from the individual search result
    """
    listing_link = result.a["href"]

    if result.find("span", class_="result-price") is not None:
        listing_price = result.find("span", class_="result-price").contents[0]
    else:
        listing_price = None

    if result.find("span", class_="housing") is not None:
        listing_housing = result.find("span", class_="housing").contents[0]
    else:
        listing_housing = None

    if result.find("span", class_="result-hood") is not None:
        listing_nbhd = result.find("span", class_="result-hood").contents[0]
    else:
        listing_nbhd = None

    out_df = pd.DataFrame(
        {
            "link": [listing_link],
            "date": [date.today().strftime("%m/%d/%y")],
            "price": [listing_price],
            "housing_info": [listing_housing],
            "neighborhood": [listing_nbhd],
        }
    )
    return out_df


def get_listings_data_from_results_page(
    url, headers, portland_url_slice, portland_url_mask
):
    """Scrape listings data from the results page and subset on local listings.
    Since craigslist returns results for nearby areas it is necessary to subset
    the data to only keep the local results. This requires a filter based on the url
    string.

    Parameters
    ----------
    url : str
        URL of the page to be scraped
    headers : dict
        Headers for get request
    portland_url_slice : int
        The number of characters in the portland_url_mask to subset the url string by
    portland_url_mask : str
        The prefix of a string that is unique to local results only

    Returns
    ------
    listings_data : pd.DataFrame
        Data from the listings
    """
    search_results = get(url=url, headers=headers)
    search_results_soup = BeautifulSoup(search_results.content, "html.parser")
    results = search_results_soup.find_all("li", class_="result-row")

    listings_data = pd.concat(
        [scrape_craigslist_search_result(result) for result in results], axis=0
    )

    listings_data = listings_data[
        listings_data["link"].str[:portland_url_slice] == portland_url_mask
    ].reset_index(drop=True)

    return listings_data


def scrape_urls(urls_to_scrape, headers, portland_url_slice, portland_url_mask):
    """Scrape urls and aggregate all listings data into single dataframe

    Parameters
    ----------
    urls_to_scrape : list
        List of the URLs of the pages to be scraped
    headers : dict
        Headers for get request
    portland_url_slice : int
        The number of characters in the portland_url_mask to subset the url string by
    portland_url_mask : str
        The prefix of a string that is unique to local results only

    Returns
    ------
    listings_data : pd.DataFrame
        Data from the listings
    """
    all_pages_listing_results = pd.concat(
        [
            get_listings_data_from_results_page(
                url=url,
                headers=headers,
                portland_url_slice=portland_url_slice,
                portland_url_mask=portland_url_mask,
            )
            for url in urls_to_scrape
        ],
        axis=0,
    )

    return all_pages_listing_results


def scrapeCraigslist():
    # scrape craigslist for ADU listings
    urls_to_scrape = get_list_of_all_urls_to_scrape(
        base_url=adu_search_url,
        headers=headers,
        listings_per_page=listings_per_page,
    )

    listings_data = scrape_urls(
        urls_to_scrape=urls_to_scrape,
        headers=headers,
        portland_url_slice=portland_url_slice,
        portland_url_mask=portland_url_mask,
    )

    # get connection string to aws rds from s3 bucket
    session = boto3.Session()
    s3_client = session.client("s3")
    f = BytesIO()
    s3_client.download_fileobj(
        "rent-adu-credentials-bucket", "connection_string.txt", f
    )
    connection_string = f.getvalue().decode("UTF-8")

    # connect to db and write data to database
    engine = create_engine(connection_string)
    listings_data.to_sql("cl_adu_rent", con=engine, if_exists="append", index=False)
