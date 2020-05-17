
import requests
from bs4 import BeautifulSoup

url = "https://finance.yahoo.com/quote/AAPL/"
page = requests.get(url)
page_content = page.content
soup = BeautifulSoup(page.content, "html.parser")
table = soup.find_all("table", {'class': "W(100%)"})
for t in table:
    rows = t.find_all("tr")
    for row in rows:
        print(row.get_text())
import pdb; pdb.set_trace()