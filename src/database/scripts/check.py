from src.database import sql
import sys
import requests
import datetime

from http import HTTPStatus

def itemdata(value, column):
    try:
        conn = sql.connect()
        cursor = conn.cursor()

        query = f'''
            SELECT 1 FROM itemdata
            WHERE {column} = %s
            '''
        cursor.execute(query,(name,))
        
        result = cursor.fetchone()
        if result == None: return sys.exit(f'{name} not in database')
    finally: conn.close()


def time(start, end):
    if start > end:
        sys.exit(f'start is later than end')
    for x in [start,end]:
        try:
            datetime.datetime.strptime(x,"%Y-%m-%dT%H:%M:%SZ")
        except:
            sys.exit(f"{x} is incorret format")


    code = requests.get(url).status_code
    if code == 200: 
        pass
    else:
        sys.exit(f'Status Code {code}: {HTTPStatus(code).phrase} | {HTTPStatus(code).description}')