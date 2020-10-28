from requests import get
from bs4 import BeautifulSoup

craigslist_search_results = "https://portland.craigslist.org/search/apa?query=%28ADU%7C%22accessory+dwelling+unit%22%7C%22In-law%22%7C%22granny+flat%22%7C%22backyard+cottage%22%29&availabilityMode=0&sale_date=all+dates"

r = get(url=craigslist_search_results)

soup = BeautifulSoup(r.content, "html.parser")

results = soup.find_all("div", class_="result-info")

if __name__ == "__main__":
    print(type(results))
