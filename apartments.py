from requests import get
from bs4 import BeautifulSoup

portland_apartments_url = "https://www.apartments.com/portland-or/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}

response = get(portland_apartments_url, headers=headers)
content = response.content

soup = BeautifulSoup(content, "html.parser")

links = [link["href"] for link in soup.find_all("a", class_="property-link")]
unique_links = list(set(links))

unique_links
