from requests import get
from bs4 import BeautifulSoup
import pandas as pd

# (ADU)-"this is not adu"-"this is not an adu unit"|("accessory dwelling unit")|("In-law")|("granny flat")|("backyard cottage")|
craigslist_search_results = "https://portland.craigslist.org/search/apa?query=%28ADU%29-%22this+is+not+adu%22-%22this+is+not+an+adu+unit%22%7C%28%22accessory+dwelling+unit%22%29%7C%28%22In-law%22%29%7C%28%22granny+flat%22%29%7C%28%22backyard+cottage%22%29%7C&availabilityMode=0&sale_date=all+dates"

search_results = get(url=craigslist_search_results)

search_results_soup = BeautifulSoup(search_results.content, "html.parser")

results = search_results_soup.find_all("li", class_="result-row")


def scrape_craigslist_search_results(result):
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


listings_data = pd.concat(
    [scrape_craigslist_search_results(result) for result in results], axis=0
)

# filter out the non-portland results
portland_url_mask = "https://portland."
portland_url_slice = 17

listings_data = listings_data[
    listings_data["link"].str[:portland_url_slice] == portland_url_mask
].reset_index(drop=True)

if __name__ == "__main__":
    print(listings_data)
