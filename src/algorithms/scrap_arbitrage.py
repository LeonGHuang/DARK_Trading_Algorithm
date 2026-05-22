import src.database.scripts.sql as sql 

import requests
from datetime import datetime, timedelta, timezone
import numpy as np
import aiohttp
import asyncio


def fetch_cost(cursor):
    query = f"""
    SELECT * FROM scraping
    """
    cursor.execute(query)
    return cursor.fetchall()
    

def fetch_items(cursor, rarity):
    query = f"""
    SELECT id, rarity, inventory_width, inventory_height
    FROM item_data
    WHERE type IN ('Armor', 'Weapon')
    AND rarity = '{rarity}'
    """
    cursor.execute(query)
    data = cursor.fetchall()
    slots = [(x[0], x[1], (x[2] * (x[3]))) for x in data] 
    return slots


async def fetch_price(ses, sem_limit, item_id):
    async with sem_limit:
        from_date = (datetime.now(timezone.utc) - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.darkerdb.com/v1/market?id={item_id}&from={from_date}&limit=50&sold=1"
        response =  await ses.get(url)
        data_body = (await response.json())['body']
        price_list = [x['price_per_unit'] for x in data_body]
        return price_list


async def process_data(cursor, ses, sem_limit, item_id, rarity, size, cost_per_slot):
    price_list = await fetch_price(ses, sem_limit, item_id)
    item_cost = int(np.percentile(price_list, 10)) if price_list else 0
    scrap_cost = cost_per_slot * size
    total_cost = item_cost + scrap_cost
    return item_id, rarity, size, total_cost, item_cost, scrap_cost


async def filter_scrap():
    d

    
async def main():
    conn = sql.connect_pc()
    cursor = conn.cursor()

    sem_limit = asyncio.Semaphore(50)

    header = [('item_id', 'rarity', 'size', 'total_cost', 'item_cost', 'scrap_cost')]
    async with aiohttp.ClientSession() as ses:
        tasks = [
            process_data(cursor, ses, sem_limit, rarity, item_id, size, cost_per_slot)
            for scrap_id, rarity, cost_per_slot in fetch_cost(cursor) 
            for item_id, item_rarity, size in fetch_items(cursor, rarity)
            ]
        rows = await asyncio.gather(*tasks)

    return header + rows

output = await main()
# output[1:] = sorted(output[1:], key=lambda x: (x[3]), reverse=True)
for row in output:
    print(f"{row[0]:<10} {row[1]:<30} {row[2]:>15} {row[3]:>15} {row[4]:>15} {row[5]:>15}")

