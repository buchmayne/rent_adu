from requests import get
from bs4 import BeautifulSoup

craigslist_search_results = "https://portland.craigslist.org/search/apa?query=%28ADU%7C%22accessory+dwelling+unit%22%7C%22In-law%22%7C%22granny+flat%22%7C%22backyard+cottage%22%29&availabilityMode=0&sale_date=all+dates"

search_results = get(url=craigslist_search_results)

search_results_soup = BeautifulSoup(search_results.content, "html.parser")

results_info = search_results_soup.find_all("div", class_="result-info")
listings = [result.a["href"] for result in results_info]

# drop listings from other markets
portland_listings = [
    listing for listing in listings if listing[:17] == "https://portland."
]

if __name__ == "__main__":
    print(portland_listings)
