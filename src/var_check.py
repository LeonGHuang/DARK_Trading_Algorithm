from sqlSrcipts import sql_connect
import sys
import requests
import datetime

from http import HTTPStatus

def name_check(name):
    from sqlSrcipts import sql_connect
    conn = sql_connect()
    cursor = conn.cursor()

    try: 
        cursor.execute(f'''
                        SELECT 1
                        FROM itemdata
                        WHERE name = '{name}'
                        ''')
        conn.close()
    except: 
        conn.close()
        sys.exit(f'{name} is not in database')
        
def time_check(start, end):
    if start > end:
        sys.exit(f'start is later than end')
    for x in [start,end]:
        try:
            datetime.datetime.strptime(x,"%Y-%m-%dT%H:%M:%SZ")
        except:
            sys.exit(f"{x} is incorret format")

def url_check(url):
    code = requests.get(url).status_code
    if code == 200: 
        pass
    else:
        sys.exit(f'Status Code {code}: {HTTPStatus(code).phrase} | {HTTPStatus(code).description}')