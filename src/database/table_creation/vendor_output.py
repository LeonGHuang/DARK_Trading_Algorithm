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
                merchant_id TEXT,
                item_id TEXT,
                name TEXT
                )
        """
        cursor.execute(query)

def table_entry(cursor, rows):
        query = """
        INSERT INTO vendor_craftout (
                merchant_id,
                item_id,
                name
        )
        VALUES (%s, %s, %s)
        """
        cursor.executemany(query, rows)


def url(merchant_id):
        url = f'https://api.darkerdb.com/v2/merchants/{merchant_id}?key={os.getenv("general")}'
        print(url)
        return url

def merchant_list(cursor):
        query = """
        SELECT id FROM vendor_info
        WHERE 'craft' = ANY(service_types);
        """
        cursor.execute(query)
        merchant_ids = cursor.fetchall()
        return merchant_ids

def fetch_data(cursor):
        body_list = []
        for merchant in merchant_list(cursor):
                craft = requests.get(url(merchant[0])).json()['body']['craft']
                sql_rows = [(merchant[0], item.get('item_id'), item.get('name')) for item in craft]
                body_list.extend(sql_rows)
        return body_list
 

if __name__=="__main__":
        subprocess.run('clear')

        conn = sql.connect_pod()
        cursor = conn.cursor()

        table_deletion(cursor)
        table_creation(cursor)
        rows = fetch_data(cursor)
        table_entry(cursor, rows)

        conn.commit()