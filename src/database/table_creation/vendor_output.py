import requests
from dotenv import load_dotenv
import os
import src.database.scripts.sql as sql
import subprocess

load_dotenv("/home/leon/projs/dark/.env/api.env")

def table_deletion(cursor):
        query = """
        DROP TABLE IF EXISTS vendor_craftout
        """
        cursor.execute(query)

def table_creation(cursor):
        query = """
        CREATE TABLE IF NOT EXISTS vendor_craftout(
                item_id TEXT,
                name TEXT
                )
        """
        cursor.execute(query)

def table_entry(cursor, rows):
        query = """
        INSERT INTO vendor_craftout (
                item_id,
                name
        )
        VALUES (%s, %s)
        """
        cursor.executemany(query, rows)


def url():
        url = f'https://api.darkerdb.com/v2/merchants/id.merchant.alchemist?key={os.getenv("general")}'
        print(url)
        return url


def fetch_data():
        fetch_data = requests.get(url()).json()['body']['craft']
        sql_rows = [(item.get('item_id'), item.get('name')) for item in fetch_data]
        # print(sql_rows)
        return sql_rows
 

if __name__=="__main__":
        subprocess.run('clear')

        conn = sql.connect_pod()
        cursor = conn.cursor()

        table_deletion(cursor)
        table_creation(cursor)
        table_entry(cursor, fetch_data())

        conn.commit()