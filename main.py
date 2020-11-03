from sqlalchemy import create_engine
import pandas as pd

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
