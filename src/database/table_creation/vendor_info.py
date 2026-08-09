import requests
from dotenv import load_dotenv
import os
import src.database.scripts.sql as sql

load_dotenv("/home/leon/projs/dark/.env/api.env")

def url():
        url = f'https://api.darkerdb.com/v2/merchants?key={os.getenv("general")}&limit=50'
        return url

def table_creation(cursor):
        query = """
        CREATE TABLE IF NOT EXISTS vendor_info (
        id TEXT PRIMARY KEY,
        name TEXT,
        icon TEXT,
        icon_url TEXT,
        display_order INT,
        service_types TEXT[],
        num_buy INT,
        num_craft INT,
        num_sell_back INT,
        patch TEXT,
        patch_name TEXT,
        season TEXT,
        season_label TEXT,
        patch_changed TEXT,
        patch_changed_name TEXT,
        is_new BOOLEAN,
        is_changed BOOLEAN
        )        
        """
        cursor.execute(query)

def table_entry(cursor):

        merchant_info = requests.get(url()).json()['body']

        cols =  list(merchant_info[0].keys())
        placeholders = ", ".join(["%s"] * len(cols))
        rows = [tuple(item.get(col) for col in cols) for item in merchant_info]

        query = f"""
        INSERT INTO vendor_info ({", ".join(cols)})
        VALUES ({placeholders})
        ON CONFLICT
        """

        cursor.executemany(query, rows)

if __name__=="__main__":
        # print(fetch[0].values())
        conn = sql.connect_pod()
        cursor = conn.cursor() 

        table_creation(cursor)
        table_entry(cursor)

        conn.commit()
