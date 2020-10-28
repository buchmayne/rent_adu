from requests import get
from bs4 import BeautifulSoup

# (ADU)-"this is not adu"-"this is not an adu unit"|("accessory dwelling unit")|("In-law")|("granny flat")|("backyard cottage")|
craigslist_search_results = "https://portland.craigslist.org/search/apa?query=%28ADU%29-%22this+is+not+adu%22-%22this+is+not+an+adu+unit%22%7C%28%22accessory+dwelling+unit%22%29%7C%28%22In-law%22%29%7C%28%22granny+flat%22%29%7C%28%22backyard+cottage%22%29%7C&availabilityMode=0&sale_date=all+dates"

search_results = get(url=craigslist_search_results)

search_results_soup = BeautifulSoup(search_results.content, "html.parser")

results_info = search_results_soup.find_all("div", class_="result-info")
listings = [result.a["href"] for result in results_info]

# drop listings from other markets
portland_listings = [
    listing for listing in listings if listing[:17] == "https://portland."
]
