import requests
from bs4 import BeautifulSoup

base_url = "https://www.apartments.com/portland-or/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}

r = requests.get(base_url, headers=headers)
c = r.content

soup = BeautifulSoup(c, "html.parser")

print(soup)
