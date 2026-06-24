import sys
import subprocess
from datetime import datetime, timedelta, timezone
import time
import itertools

import catppuccin
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import aiohttp
import asyncio

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


async def fetch_darker(ses, name, rarity, /, hours=24):
        db = darkerdb()
        page_count = itertools.count(1,1)
        price_list = []
        stop = asyncio.Event()
            
        async def worker():
                while stop.is_set() == False:
                        page_num = next(page_count)
                        if page_num > 20: stop.set() #!HH page pagination is now limited to 1000 listings, switch to cursor pagination when fixed
                        url = db.market(name, rarity, hours=hours, page=page_num)
                        fetch = await ses.get(url) # sends requests, and waits for header
                        fetch = await fetch.json() # waits for body and deserialise it
                        fetch_body = fetch['body']
                        price_list.extend((x['created_at'],x['price_per_unit'],x['has_sold']) for x in fetch_body)
                        if len(fetch_body) <50: stop.set() #! doesnt work right now as page pagination return page 21 for any page > 21

        await asyncio.gather(*[worker() for _ in range(5)])
        return (price_list)


# ! maybe use a different method, maybe sliding avg
def process_data(data):
        prices = np.array([x[1] for x in data])
        q1, q3 = np.percentile(prices, [25, 75])
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        return [x for x in data if lo <= x[1] <= hi]


def groupby_hour(data):
        df = pd.DataFrame(data)
        df[0] = pd.to_datetime(df[0])
        df = df.set_index(df[0])
        hourly = df.resample('h')[1].mean()
        # print(hourly)
        return hourly


def graph(name, rarity, data):
        plt.style.use("mocha")

        fig, ax = plt.subplots()
        ax.plot(data.index, data.values)
        ax.set_title(f'Daily Prices: {name} ({rarity})')
        ax.set_xlabel('Hour (UTC)')
        ax.set_ylabel('Price')
        
        ax.xaxis.set_major_locator(mdates.DayLocator(interval = 1))
        ax.xaxis.set_minor_locator(mdates.HourLocator(byhour = range(0, 24, 6)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d')) 
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M')) 
        ax.tick_params('x', which='major', rotation = 0, labelsize = '8', pad=7)
        ax.tick_params('x', which='minor', rotation = 0, labelsize = '7', pad=9)
   
        plt.show()


def plot_by_day(name, rarity, data):
        df = pd.DataFrame(data, columns=['created_at', 'price_per_unit', 'has_sold'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date'] = df['created_at'].dt.date
        df['hour'] = df['created_at'].dt.hour

        grouped = df.groupby(['date', 'hour'])['price_per_unit'].mean().unstack(level=0)
        print(grouped)

        plt.style.use('mocha')
        fig, ax = plt.subplots()
        ax.plot(grouped)

        ax.set_title(f'Daily Prices: {name} ({rarity})')
        ax.set_xlabel('Hour (UTC)')
        ax.set_ylabel('Unit Price')

        ax.set_xticks(range(0, 24, 6))
        ax.set_xlim(0, 23)
        ax.ticklabel_format(style='plain', axis='y')

        ax.margins(0,.1)
        ax.legend(
        [f"{d.strftime('%a'):>3} {d.strftime('%d'):>2}" for d in grouped.columns],
        prop={'family': 'monospace'}
        )
        plt.show()


async def main(name, rarity):
        subprocess.run('clear')
        start_time = time.perf_counter()
        async with aiohttp.ClientSession() as ses:
                data = await fetch_darker(ses, name, rarity, hours=999)
        end_time = time.perf_counter()
        print(f'fetch time: {end_time - start_time}s')
        
        process = process_data(data)
        hourly = groupby_hour(process)
        plot_by_day(name, rarity, process)
        # graph(name, rarity, hourly)
        # return hourly   
asyncio.run(main("Scraps", "Epic"))


# def main(name, rarity):
#         subprocess.run('clear')
#         data = fetch_darker(name, rarity, hours=72)
#         process = process_data(data)
#         hourly = groupby_hour(process)
#         graph(name, rarity, hourly)
#         # return hourly   
# main("Spectral Hilt", "Epic")