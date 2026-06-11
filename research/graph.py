import sys
import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import src.database.scripts.sql as sql


class darkerdb:
    def __init__(self):
        conn = sql.connect_pc()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT id FROM item_data")
        self.item_ids = [x[0] for x in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT name FROM item_data")
        self.names = [x[0] for x in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT rarity FROM item_data")
        self.rarities = [x[0] for x in cursor.fetchall()]

        cursor.close()
        conn.close()

    def _para_check(self, **kwargs):
        for key, val in kwargs.items():
            if val not in getattr(self, key):
                sys.exit(f"\n{key} does not contain {val}\nensure key is pural and val is singular")

    def market(self, name, rarity, /, hours=24, page=1):
        self._para_check(names = name, rarities = rarity)
        from_date = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%d")
        url =   f"https://api.darkerdb.com/v1/market?item={name.replace('\'', "’")}&rarity={rarity}"\
                f"&from={from_date}&limit=50&page={page}"
        # print(f"{url}")
        return url
        
        
def fetch_darker(name, rarity, /, hours=24):
    db = darkerdb()
    with requests.Session() as ses:
        page_num = 1
        price_list = []
        while True:
            if page_num > 21: break #! page pagination is now limited to 1000 listings, switch to cursor pagination when fixed
            url = db.market(name, rarity, hours=hours, page=page_num)
            fetch_body = ses.get(url).json()['body']
            price_list.extend((x['created_at'],x['price_per_unit'],x['has_sold']) for x in fetch_body)
            print(url, end='\r')
            if len(fetch_body) <50: break
            page_num += 1
        return (price_list)


# ! maybe use a different method
def process_data(data):
    prices = np.array([x[1] for x in data])
    q1, q3 = np.percentile(prices, [25, 75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [x for x in data if lo <= x[1] <= hi]

def groupby_hour(data):
    df = pd.DataFrame(data)
    df[0] = pd.to_datetime(df[0])
    hourly_price = df.groupby(pd.Grouper(key=0, freq='h'))[1].mean()
    return hourly_price 

def graph(name, rarity, data):
    fig, ax = plt.subplots()
    ax.plot(data.index, data.values)
    ax.set_title(f'Daily Prices: {name} ({rarity})')
    ax.set_xlabel('Hour (UTC)')
    ax.set_ylabel('Price')
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d')) 
    ax.tick_params('x', which='major', rotation = 35, labelsize = '10')
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M')) 
    ax.tick_params('x', which='minor', rotation = 35, labelsize='7')

    plt.show()

def main(name, rarity):
    data = fetch_darker(name, rarity, hours=72)
    process = process_data(data)
    hourly = groupby_hour(process)
    graph(name, rarity, hourly)
    # return hourly   

e = main("Potion of Protection", "Epic")
e


# %%
# if __name__ == "__main__":
#     name, rarity = "Spectral Hilt", "Epic"
#     os.system("clear")
#     output = fetch_darker(name, rarity, hours=24)
#     output = sorted(output, key=lambda x: x[0])
#     for x in output:
#         print(f'{x[0]} {x[1]:>6} {x[2]}')
#     os.system(f"echo {name} {rarity}")



