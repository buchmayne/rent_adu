from requests import get
from bs4 import BeautifulSoup

portland_apartments_url = "https://www.apartments.com/portland-or/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}


def scrape_unique_links_from_results_page(url, headers):
    """
    TO DO: add doc string
    """
    response = get(url, headers=headers)
    content = response.content

    soup = BeautifulSoup(content, "html.parser")

    links = [link["href"] for link in soup.find_all("a", class_="property-link")]
    unique_links = list(set(links))

    return unique_links


def get_total_pages_of_results(base_url, headers):
    """
    TO DO: add doc string
    """
    response = get(base_url, headers=headers)
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    page_range_string = soup.find("span", class_="pageRange").text

    return page_range_string
