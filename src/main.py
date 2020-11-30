from sqlalchemy import create_engine
import craigslist as cl
import boto3
from io import BytesIO


def scrapeCraigslist():
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

    # get connection string to aws rds from s3 bucket
    session = boto3.Session()
    s3_client = session.client("s3")
    f = BytesIO()
    s3_client.download_fileobj(
        "rent-adu-credentials-bucket", "connection_string.txt", f
    )
    connection_string = f.getvalue().decode("UTF-8")

    engine = create_engine(connection_string)
    listings_data.to_sql("cl_adu_rent", con=engine, if_exists="append", index=False)
