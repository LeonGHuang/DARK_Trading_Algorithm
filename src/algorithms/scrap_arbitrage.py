import src.database.scripts.sql as sql 

import requests
from datetime import datetime, timedelta, timezone
import numpy as np
import aiohttp
import asyncio


def fetch_cost(cursor):
    query = f"""
    SELECT * FROM scraping
    ORDER BY id
    """
    cursor.execute(query)
    return cursor.fetchall()
    
def fetch_items(cursor):
    query = f"""
    SELECT 
        i.id, 
        i.rarity, 
        i.inventory_width * i.inventory_height AS size,
        s.cost_per_slot
    FROM item_data AS i
    LEFT JOIN scraping AS s
    ON i.rarity = s.rarity
    WHERE type IN ('Armor', 'Weapon')
    AND i.rarity NOT IN ('Poor', 'Common','Artifact')
    AND i.rarity = 'Epic'
    AND i.name NOT ILIKE ALL (SELECT name FROM recipes)
    ORDER BY id
    """
    cursor.execute(query)
    return cursor.fetchall()
    
async def fetch_price(ses, sem_limit, item_id):
    async with sem_limit:
        from_date = (datetime.now(timezone.utc) - timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.darkerdb.com/v1/market?item_id={item_id.replace('\'', "'")}&from={from_date}&limit=50&sold=0"
        response =  await ses.get(url)
        data_body = (await response.json())['body']
        price_list = [x['price_per_unit'] for x in data_body]
        return price_list





async def item_prices(cursor, ses, sem_limit, item_id, rarity, size, cost_per_slot):
    price_list = await fetch_price(ses, sem_limit, item_id)
    item_cost = int(np.percentile(price_list, 30)) if price_list else 99999
    price_per_slot = round(item_cost / size)
    total_cost_per_slot = price_per_slot + cost_per_slot
    return item_id, rarity, total_cost_per_slot, price_per_slot, item_cost, cost_per_slot


async def scrap_prices(cursor, ses, sem_limit):
    async def fetch_with_rarity(item_id, rarity):
        prices = await fetch_price(ses, sem_limit, item_id)
        return rarity, int(np.mean(prices))

    tasks = [fetch_with_rarity(item_id, rarity) for item_id, rarity, cost_per_slot in fetch_cost(cursor)]
    scrap_prices = await asyncio.gather(*tasks)
    return scrap_prices




async def main():
    conn = sql.connect_pc()
    cursor = conn.cursor()

    sem_limit = asyncio.Semaphore(50)

    header = [('item_id', 'rarity', 'total_cost_per_slot', 'price_per_slot', 'item_cost', 'cost_per_slot')]
    async with aiohttp.ClientSession() as ses:
        
        tasks = [
            item_prices(cursor, ses, sem_limit, item_id, rarity, size, scraping_cost)
            for item_id, rarity, size, scraping_cost in fetch_items(cursor)
            ]
        rows = await asyncio.gather(*tasks)

    return header + rows

        # e = await scrap_prices(cursor, ses, sem_limit)
        # return e


output = await main()


def printing():
    output[1:] = sorted(output[1:], key=lambda x: (x[2]), reverse=False)
    for row in output:
        print(f"{row[1]:<15} {row[0]:<35} {row[2]:>15} {row[3]:>15} {row[4]:>15} {row[5]:>15}")

printing()




