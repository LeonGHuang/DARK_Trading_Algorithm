
from datetime import datetime, timedelta, timezone

import os
import sys
import subprocess
import numpy as np
import asyncio
import aiohttp

import src.database.scripts.sql as sql 


class recipe_fetch():
        def __init__(self):
                self.conn = sql.connect_pc()

        def __enter__(self):
                return self

        def __exit__(self, exc_type, exc_val, exc_tb):
                self.conn.close()

        def __del__(self):
                self.conn.close()

        def id_range(self):
                cursor = self.conn.cursor()
                # ! ensure python string uses PYTHON ENCODING SYNTAX
                # ! SQL's U&\2019 will activate python octal with \{3 digit number} and output \201 = 129
                # ! just look at syntax highlighting 
                query = f""" 
                SELECT r.recipe_id
                FROM recipes AS r
                LEFT JOIN item_data AS i
                ON (r.name, r.rarity) = (replace(i.name, '\u2019', ''''), i.rarity)
                WHERE type IN ('Misc', 'Weapon')
                OR utility_type = 'Drink' 
                OR i.name IN ('Campfire Kit', 'Intricate Wooden Figurine','Fangs of Death Necklace','Charm of Fortune')
                ORDER BY r.recipe_id
                """ 
                cursor.execute(query)
                return cursor.fetchall()

        def craftable(self, recipe_id):
                cursor = self.conn.cursor()
                query = f"""
                SELECT r.amount, r.rarity, i.name 
                FROM recipes AS r
                LEFT JOIN item_data as i
                ON r.name = replace(i.name, '\u2019', '''')
                        AND r.rarity = i.rarity
                WHERE recipe_id = {recipe_id}
                """
                cursor.execute(query)
                return cursor.fetchall() 

        def ingredients(self, recipe_id):
                cursor = self.conn.cursor()
                query = f"""
                SELECT i.amount, i.rarity, d.name
                FROM ingredients AS i
                LEFT JOIN item_data AS d
                ON i.name = replace(d.name, '\u2019', '''')
                        AND i.rarity = d.rarity
                WHERE recipe_id = {recipe_id}
                """
                cursor.execute(query)
                return cursor.fetchall()


class darkerdb():
        def __init__(self, hour):
                self.from_date = (datetime.now(timezone.utc) - timedelta(hours=hour)).strftime("%Y-%m-%dT%H:%M:%SZ")
                self.cache = {}   
                self.count = 0

        async def _api_fetch(self, session, rarity, name):
<<<<<<< HEAD
                url = f"https://api.darkerdb.com/v1/market?item={name}&rarity={rarity}&from={self.from_date}&limit=50&has_sold=1"
=======
                url = f"https://api.darkerdb.com/v1/market?key={os.getenv('crafting_arbitrage_key')}&item={name}&rarity={rarity}&from={self.from_date}&limit=50&has_sold=1"
>>>>>>> e980b41 (feat: switched to os library to source keys from the new api env file)
                response = await session.get(url)
                output = await response.json()
                response.release()
                body_data = output['body']
                price_per_unit = [x['price_per_unit'] for x in body_data]
                return price_per_unit

        async def _price_fetch(self, session, rarity, name):
                self.count += 0 
                key = (name, rarity)
                if key not in self.cache:
                        self.cache[key] = asyncio.create_task(self._api_fetch(session, rarity, name))
                return await self.cache[key]

        async def r_fetch(self, session, amount, rarity, name):
                price_per_unit = await self._price_fetch(session, rarity, name)
                
                q_sold = len(price_per_unit)
                r_avg = int(np.percentile(price_per_unit,15) * amount) if price_per_unit else 0
                return name, rarity, r_avg, q_sold

        async def i_fetch(self, session, amount, rarity, name):
                price_per_unit = await self._price_fetch(session, rarity, name)

                if name == 'Gold Coin': i_avg = amount
                elif price_per_unit: i_avg = int(np.percentile(price_per_unit,16) * amount)  
                else: i_avg = 0

                return amount, name, i_avg


def _listing_fee(r_avg):
        five_percent = r_avg * 0.05
        if five_percent < 15: return 15
        else: return five_percent


async def process_fetch(session, r, db, sem_limit, recipe_id):
        async with sem_limit:
                r_task = [
                db.r_fetch(session, r_amount, r_rarity, r_name) 
                for r_amount, r_rarity, r_name in r.craftable(recipe_id)
                ]
                i_task = [
                db.i_fetch(session, i_amount, i_rarity, i_name)
                for i_amount, i_rarity, i_name in r.ingredients(recipe_id)
                ]
                r_results = await asyncio.gather(*r_task)
                i_results = await asyncio.gather(*i_task)

        rarity = r_results[0][1]        
        name = r_results[0][0]
        r_avg = r_results[0][2]
        i_avg = sum(ingredient[2] for ingredient in i_results)
        net = round(r_avg - i_avg - _listing_fee(r_avg))
        q_sold = r_results[0][3]
        return(recipe_id, rarity, name, net, r_avg, i_avg, q_sold, i_results)


async def main(hour):
        header = [('id', 'rarity', 'name', 'net', 'r_avg', 'i_avg', 'q_sold', 'ingredients / rarity / price')]
        r = recipe_fetch()
        db = darkerdb(hour)
        sem = asyncio.Semaphore(30)
        async with aiohttp.ClientSession() as session:
                task = [process_fetch(session, r, db, sem, recipe_id[0]) for recipe_id in r.id_range()]
                return header + await asyncio.gather(*task)
                # await asyncio.gather(*task)
                # return len(db.cache), db.count


if __name__ == '__main__': 
        subprocess.run('clear')
        output = asyncio.run(main(3))
        output[1:] = filter(lambda x: x[6]>0, output[1:])
        output[1:] = sorted(output[1:], key=lambda x: x[3], reverse=True)
        for x in output:
                print(f"{x[0]:<4} {x[1]:<10} {x[2]:<35} {(x[3]):>8} {x[4]:>8} {x[5]:>8} {x[6]:>8}")
                # print(f"{x[0]:<4} {x[1]:<10} {x[2]:<35} {(x[3]):>8} {x[4]:>8} {x[5]:>8} {x[6]:>8} {x[7]}") #debugging code
            