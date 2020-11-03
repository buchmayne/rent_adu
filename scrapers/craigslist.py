from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import math
from sqlalchemy import create_engine
from credentials import shred_connection_string

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
    """
    TO DO: add doc string
    """
    total_results = int(search_results_soup.find("span", class_="totalcount").text)
    total_pages = math.ceil(total_results / listings_per_page)
    return total_pages


def get_list_of_all_urls_to_scrape(base_url, headers, listings_per_page):
    """
    TO DO: add doc string
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
    """
    TO DO: Add doc string
    """
    listing_link = result.a["href"]
    listing_date = result.time["datetime"]

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
            "date": [listing_date],
            "price": [listing_price],
            "housing_info": [listing_housing],
            "neighborhood": [listing_nbhd],
        }
    )
    return out_df


def get_listings_data_from_results_page(
    url, headers, portland_url_slice, portland_url_mask
):
    """
    TO DO: add doc string
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
    """
    TO DO: add doc string
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


if __name__ == "__main__":
    urls_to_scrape = get_list_of_all_urls_to_scrape(
        base_url=adu_search_url, headers=headers, listings_per_page=listings_per_page
    )

    listings_data = scrape_urls(
        urls_to_scrape=urls_to_scrape,
        headers=headers,
        portland_url_slice=portland_url_slice,
        portland_url_mask=portland_url_mask,
    )

    engine = create_engine(shred_connection_string)
    listings_data.to_sql(
        "craigslist_adu_rent", con=engine, if_exists="append", index=False
    )
