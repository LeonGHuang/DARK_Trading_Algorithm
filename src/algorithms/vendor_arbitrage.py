import src.database.scripts.sql as sql 

import os
import subprocess
import requests
from datetime import datetime, timedelta, timezone
import numpy as np
import aiohttp
import asyncio
import time 
from dotenv import load_dotenv

load_dotenv("/home/leon/projs/dark/.env/api.env", override=True)

def sql_item():
        conn = sql.connect_pod()
        cursor = conn.cursor()
        query = """
        SELECT id, name, rarity, vendor_price FROM item_data
	WHERE item_type NOT IN ('armor', 'weapon', 'accessory', 'utility')
	AND rarity != 'artifact'
	AND name NOT IN ('Lifeleaf', 'Wardweed', 'Phantom Flower', 'Saltvine', 'Lyre', 'Drum')
	AND name NOT ILIKE '%Key%'
	AND name NOT ILIKE '%Ingot%'
	AND name NOT ILIKE '%Ore%'
	AND id NOT ILIKE '%heart%'
	AND id NOT ILIKE '%stag%'
	AND is_tradable = true
	AND vendor_price > 299
	ORDER BY vendor_price DESC;
        """
        cursor.execute(query)
        return cursor.fetchall()


async def fetch(session, conn_limit, id, name, rarity, vendor_price):
	async with conn_limit:
		from_date = ( datetime.now(timezone.utc) - timedelta(minutes=30) ).replace(tzinfo=None).isoformat()
		url = f"https://api.darkerdb.com/v2/market?key={os.getenv("vendor_arbitrage_key")}&item_id={id}&from={from_date}&limit=50&sold=0"
		# print(url)
		response = await session.get(url)
		output = await response.json()
		response.release()
		

		items                   = [(listing['price_per_unit'], listing['quantity']) for listing in output['body']]
		undercut_items          = list(filter(lambda x: x[0] < vendor_price, items))
		extractable_value       = round(sum((vendor_price - x[0]) * x[1] for x in undercut_items))
		average_undercut_price  = int(np.mean([x[0] for x in undercut_items])) if undercut_items else 0
		average_margin          = (vendor_price - average_undercut_price) if average_undercut_price else 0
		undercut_quantity       = round(sum([x[1] for x in undercut_items]))

		return (name, extractable_value, vendor_price, average_margin, undercut_quantity, undercut_items)


async def main():
	header = [('name', 'extractable', 'vendor_price', 'avg_margin', 'quantity', 'listings')]
	sem = asyncio.Semaphore(25)
	start_time = time.perf_counter()
	target_items = sql_item()
	async with aiohttp.ClientSession() as session:
		task = [
		fetch(session, sem, id, name, rarity, vendor_price)
		for id, name, rarity, vendor_price in target_items
		]
		rows = await asyncio.gather(*task)
	end_time = time.perf_counter()
	print(f'{len(target_items)} fetch took {end_time - start_time}s')
	return header + list(rows)


if __name__ == "__main__":
	subprocess.run("clear")
	rows = asyncio.run(main())
	rows[1:] = filter(lambda x: x[1], rows[1:])
	rows[1:] = sorted(rows[1:], key=lambda x: x[1], reverse=True)
	for x in rows:
		print(f"{x[0]:<32} {x[1]:>15} {x[2]:>15} {x[3]:>15} {x[4]:>15}")
