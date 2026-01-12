# local
from sqlSrcipts import sql_engine
from sqlSrcipts import sql_connect
# standard
import os
# third
import pandas as pd
import requests 
from http import HTTPStatus
from sqlalchemy import create_engine

# fetching to pd
with requests.Session() as ses:
    page = '1'
    limit = '50'
    url = f"https://api.darkerdb.com/v1/items?key={os.getenv("dark_api_key")}&condense=true&limit={limit}&page={page}"
    test = ses.get(url)

    if test.status_code == 200:
        list = []
        byte_counter = 0
        data = {'pagination':'next'}

        while 'next' in data['pagination']:
            req = ses.get(url)
            data = req.json()
            list.extend(data['body'])
            # print(f'page {data['pagination']['page']} is done')
            page = str(int(page) + 1)
            byte_counter += len(req.content) # 8 bits in a byte
            try: url = data['pagination']['next']
            except: break

        df = pd.json_normalize(list, sep=',')        

        print(f'get-requests = {page}'
              f'\nbytes = {byte_counter}')
        
    else: print(test.status_code)   

# commiting to sql
df.to_sql('itemdata', con=sql_engine(), if_exists='replace', index=False)

conn = sql_connect()

cursor = conn.cursor()
cursor.execute('ALTER TABLE itemdata ADD CONSTRAINT itemdata_pkey PRIMARY KEY (id)')
cursor.close()

conn.commit()
conn.close()


print('sql commit complete')