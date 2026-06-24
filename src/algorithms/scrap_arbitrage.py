import src.database.scripts.sql as sql 

import requests
from datetime import datetime, timedelta, timezone
import numpy as np
import aiohttp
import asyncio
import subprocess


class sql_fetch():
        def __init__(self):
                self.conn = sql.connect_pc()
                self.cursor = self.conn.cursor()

        def __exit__(self):
                self.conn.close()
                
        def __del__(self):
                self.conn.close()

        def scrap(self, rarity):
                query = f"""
                SELECT * FROM scraping
                WHERE rarity = '{rarity}'
                ORDER BY id
                """
                self.cursor.execute(query)
                return self.cursor.fetchall()

        def items(self, rarity):
                query = f"""
                SELECT 
                        i.id, 
                        i.inventory_width * i.inventory_height AS size
                FROM item_data AS i
                WHERE type IN ('Armor', 'Weapon')
                        AND i.rarity = '{rarity}'
                        AND i.inventory_width * i.inventory_height > 2
                        AND REPLACE(i.name, '\u2019', '''') NOT IN (SELECT name FROM recipes)
                ORDER BY id
                """
                self.cursor.execute(query)
                
                return self.cursor.fetchall()


async def fetch_price(ses, sem_limit, item_id):
        async with sem_limit:
                from_date = (datetime.now(timezone.utc) - timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
                url = f"https://api.darkerdb.com/v1/market?item_id={item_id.replace('\'', "'")}&limit=50&sold=0"
                # print(url)
                response =  await ses.get(url)
                data_body = (await response.json())['body']
                price_list = [x['price_per_unit'] for x in data_body]
        return price_list

async def scrap_prices(ses, sem_limit, sql_con, rarity):
        scrap_id, rarity, scraping_cost = sql_con.scrap(rarity)[0]
        scrap_price = await fetch_price(ses, sem_limit, scrap_id)

        scrap_price = int(np.percentile(scrap_price, 20)) if scrap_price else 99999
        listing_fee = scrap_price * 0.05
        processing_cost = listing_fee + scraping_cost
        # print(scrap_id, rarity, scrap_price, processing_cost)
        return scrap_id, scrap_price, processing_cost

async def item_prices(ses, sem_limit, item_id, size):
        price_list = await fetch_price(ses, sem_limit, item_id)

        price_list = sorted(price_list)
        item_cost = int(np.percentile(price_list, 10)) if price_list else 99999
        price_per_slot = round(item_cost / size)
        # print(item_id, price_per_slot, item_cost, price_list)
        return [item_id, price_per_slot, item_cost, price_list, size]

async def filter_prices(price_data, scrap_price, processing_cost):
        for i,x in enumerate(price_data): 
                price_data[i][1] = x[1] + processing_cost
        price_data = list(filter(lambda x: x[1] < scrap_price * 1.5, price_data))
        return price_data

async def main(rarity):
        sql_con = sql_fetch()
        sem_limit = asyncio.Semaphore(50)

        header = [('item_id', 'price_per_slot', 'item_cost', 'listings', 'size')]
        async with aiohttp.ClientSession() as ses:
                scrap_id, scrap_price, processing_cost = await scrap_prices(ses, sem_limit, sql_con, rarity)
                tasks = [item_prices(ses, sem_limit, item_id, size)
                        for item_id, size in sql_con.items(rarity)]
                price_data = await asyncio.gather(*tasks)
                rows = await filter_prices(price_data, scrap_price, processing_cost)
        return rarity, scrap_price, header + rows



def printing():
        rarity, scrap_price, output = asyncio.run(main("Epic"))
        subprocess.run("clear")
        print(f"{rarity} Scrap selling at {scrap_price} Gold")
        output[1:] = sorted(output[1:], key=lambda x: (x[1]), reverse=False)
        for x in output:
                print(f"{x[0]:<25} {x[4]:>5} {x[1]:>16} {x[2]:>10} {x[3][0:9]}")
printing()


