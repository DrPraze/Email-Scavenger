# -*- coding: utf-8 -*-

# !pip install lxml
# !pip install bs4

import requests
import re
import pandas as pd
from bs4 import BeautifulSoup


# Search word
WORD = "facebook.com"
# (Optionally) For searching inside the site: 
INSITE = "site:"
# Searching inside the site
SEARCH_WORD = INSITE + WORD

# URL, headers and params for searching
url = "https://www.google.com/search"
headers = {"User-Agent": "link_scraper"}
# If you only search word then use WORD instead of SEARCH_WORD
params = {"q": SEARCH_WORD}

# Get html page and a text from it
html_doc = requests.get(url, params=params, headers=headers)
text = html_doc.text

# Create soup from the text
soup = BeautifulSoup(text, "lxml")

# Find a desirable link
HREF = "https://www." + WORD + "/"

# Iterate links through the soup
link_list = []
for link in soup.findAll("a", href=re.compile(HREF)):
    link_list.append(link)

# Clean the links
url_list = []
for url in link_list:
    url = re.sub(r"&amp.+", "", str(url))
    url = re.sub(r'<a href="\/url\?q=', "", url)
    url_list.append(url)

links_df = pd.DataFrame(url_list)
links_df.to_csv(
    f"{WORD}_links.csv", index=False, header=False, encoding="utf-8"
)
