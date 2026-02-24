from src.database import sql
import sys
import requests
import datetime

from http import HTTPStatus

def name(name):
    conn = sql.connect()
    cursor = conn.cursor()

    query = f'''
        SELECT 1 FROM itemdata
        WHERE name = %s
        '''
    cursor.execute(query,(name,))
    
    result = cursor.fetchone()
    if result == None:
        return sys.exit(f'{name} not in database')


def item_id(item_id):
    conn = sql.connect()
    cursor = conn.cursor()

    query = f'''
        SELECT 1 FROM itemdata
        WHERE id = %s
        '''
    cursor.execute(query,(item_id,))
    
    result = cursor.fetchone()
    if result == None:
        return sys.exit(f'{item_id} not in database')

def archetype(archetype):
    conn = sql.connect()
    cursor = conn.cursor()

    query = f'''
        SELECT 1 FROM archetype
        WHERE id = %s
        '''
    cursor.execute(query,(archetype,))
    
    result = cursor.fetchone()
    if result == None:
        return sys.exit(f'{archetype} not in database')


def time(start, end):
    if start > end:
        sys.exit(f'start is later than end')
    for x in [start,end]:
        try:
            datetime.datetime.strptime(x,"%Y-%m-%dT%H:%M:%SZ")
        except:
            sys.exit(f"{x} is incorret format")


def url(url):
    code = requests.get(url).status_code
    if code == 200: 
        pass
    else:
        sys.exit(f'Status Code {code}: {HTTPStatus(code).phrase} | {HTTPStatus(code).description}')