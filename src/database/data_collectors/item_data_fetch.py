# %%
import requests
import os
import pandas as pd

# %%
def url(page):
    url = f"https://api.darkerdb.com/v1/items?key={os.getenv("dark_api_key")}&limit=50&page={page}"
    return url

# %%
def item_data_fetch():
    with requests.Session() as ses:
        body_list = []
        num_pages = ses.get(url('1')).json()['pagination']['num_pages']
        for page in range(1,num_pages + 1):
            req = ses.get(url(page))
            body_list.extend(req.json()['body'])
            print(f'page = {page}/{num_pages}', end="\r")
    return body_list


