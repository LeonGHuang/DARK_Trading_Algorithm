import requests
import os
import subprocess
from dotenv import load_dotenv
from src.database.scripts.sql import connect_pod

load_dotenv("/home/leon/projs/dark/.env/api.env")

def url():
        url = f"https://api.darkerdb.com/v2/market?key={os.getenv("general")}"
        print(url)
        return url


def market_col(cursor):
        query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'market'
        ORDER BY ordinal_position;
        """
        cursor.execute(query)
        col = [col[0] for col in cursor.fetchall()]
        # print(col)
        return col


def fetch_market(cursor):
        fetch = requests.get(url()).json()['body']
        # print(fetch)
        rows = []
        for item in fetch:
                item_data = tuple(item.get(col) for col in market_col(cursor))
                # print(item_data)
                rows.append(item_data)
        print(rows)


# table entry here here

if __name__=="__main__":
        subprocess.run('clear')

        conn = connect_pod()
        cursor = conn.cursor()

        # market_col(cursor)
        fetch_market(cursor)


        conn.close()