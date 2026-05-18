import src.database.scripts.sql as sql 

import requests
from datetime import datetime, timedelta, timezone
import numpy as np

class recipe_fetch():
    def __init__(self):
        self.conn = sql.connect_pc()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        self.conn = None

    def __del__(self):
        if self.conn:
            self.conn.close()


    def id_range(self):
        cursor = self.conn.cursor()
        query = """
        SELECT recipe_id FROM recipes
        WHERE name LIKE '%Charm%'
        OR name LIKE '%Vial%'
        OR name LIKE '%Ingot%'
        OR name LIKE '%Powder%'
        OR name LIKE '%Vial%'
        OR name LIKE '%Ghostdust%'
        OR name LIKE '%Gold Coin%'
        OR name LIKE '%Potion%'
        OR name LIKE '%Fangs%'
        OR name LIKE '%Campfire%'
        OR name LIKE '%Woodsman%'
        OR name LIKE '%Intricate%'
        OR name LIKE '%LockPicks%'
        """
        # query = """
        # SELECT recipe_id FROM recipes
        # """
        cursor.execute(query)
        return cursor.fetchall()

    def craftable(self, recipe_id):
        cursor = self.conn.cursor()
        query = f"""
        SELECT amount, rarity, name FROM recipes
        WHERE recipe_id = {recipe_id}
        """
        cursor.execute(query)
        return cursor.fetchall() 

    def ingredients(self, recipe_id):
        cursor = self.conn.cursor()
        query = f"""
        SELECT amount, rarity, name FROM ingredients
        WHERE recipe_id = {recipe_id}
        """
        cursor.execute(query)
        return cursor.fetchall()


class darkerdb():

    def __init__(self):
        self.ses = requests.Session()

    def price_fetch(self, name, rarity):
        from_date = (datetime.now(timezone.utc) - timedelta(minutes=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.darkerdb.com/v1/market?item={name.replace('\'', "’")}&rarity={rarity}&from={from_date}&limit=50"

        fetch = self.ses.get(url, timeout=10)
        price = tuple(item['price_per_unit'] for item in fetch.json()['body'])
        return (price)


#working
def main():
    with recipe_fetch() as r:
        total, count = len(r.id_range()), 0
        db = darkerdb()
        output = [('recipe_id', 'rarity', 'name', 'net', 'r_avg', 'i_avg', 'q_sold')]    
        for item in r.id_range():
            print(f"progress: {total} / {(count := count + 1)}", end='\r')
            r_avg, i_avg = 0, 0
            
            for r_amount, r_rarity, r_name in r.craftable(item[0]):
                price_list = db.price_fetch(r_name, r_rarity)
                q_sold = len(price_list)
                if price_list == (): pass
                else: r_avg += round(np.nanmean(price_list)) * r_amount

            for i_amount, i_rarity, i_name in r.ingredients(item[0]):
                if i_name != 'Gold Coin':
                    price_list = db.price_fetch(i_name, i_rarity)
                    if not price_list: pass
                    else: i_avg += round(np.nanmean(price_list)) * i_amount
                else:
                    i_avg += i_amount

            output.append((item[0], r_rarity, r_name, r_avg-i_avg, r_avg, i_avg, q_sold))
            # print(f"{item[0]} {r_rarity:<10}  {r_name:<35} net:{(r_avg-i_avg):>6}  r:{r_avg:>4}  i:{i_avg:>5}  q:{amount_sold:>5}")
    return output


if __name__ == '__main__':
    output = main()
    output[1:] = sorted(output[1:], key=lambda x: x[3], reverse=True)
    for x in output:
        print(f"{x[0]:<10} {x[1]:<10} {x[2]:<35} {(x[3]):>8} {x[4]:>8} {x[5]:>8} {x[6]:>8}")

