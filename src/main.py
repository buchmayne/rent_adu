from sqlalchemy import create_engine
import credentials as creds
import craigslist as cl


if __name__ == "__main__":
    urls_to_scrape = cl.get_list_of_all_urls_to_scrape(
        base_url=cl.adu_search_url,
        headers=cl.headers,
        listings_per_page=cl.listings_per_page,
    )

    listings_data = cl.scrape_urls(
        urls_to_scrape=urls_to_scrape,
        headers=cl.headers,
        portland_url_slice=cl.portland_url_slice,
        portland_url_mask=cl.portland_url_mask,
    )

    connection_string = "postgres://{}:{}@{}:{}/{}".format(
        creds.aws_user,
        creds.aws_password,
        creds.aws_host,
        creds.aws_port,
        creds.aws_database,
    )

    engine = create_engine(connection_string)
    listings_data.to_sql(
        "craigslist_adu_rent", con=engine, if_exists="append", index=False
    )
