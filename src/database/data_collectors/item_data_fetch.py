import requests
import os
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv(".env/api.env")


def url(cursor=None):
	if cursor:
		return f"https://api.darkerdb.com/v2/items?key={os.getenv("general")}&limit=50&cursor={cursor}"

	else:
		return f"https://api.darkerdb.com/v2/items?key={os.getenv("general")}&limit=50"


def item_data_fetch():
	with requests.Session() as ses:
		body_list = []
		inital_fetch = ses.get(url()).json()

		body_list.extend(inital_fetch["body"])
		next_cursor = inital_fetch["pagination"]['next']

		count = inital_fetch["pagination"]["count"]
		total = inital_fetch['pagination']['total']

		while next_cursor != None:
			print(f'item featch: {count} / {total}', end = '\r')
			fetch = ses.get(url(next_cursor)).json()
			body_list.extend(fetch['body'])
			next_cursor = fetch["pagination"]['next']

			count += int(fetch['pagination']['count'])
	return body_list
