from datetime import datetime
from sqlSrcipts import sql_connect

def name_check(name):
    from sqlSrcipts import sql_connect
    conn = sql_connect()
    cursor = conn.cursor()

    try: cursor.execute(f'''
        SELECT 1
        FROM itemdata
        WHERE name = '{name}'
        ''')
    except: return(print(f'{name} is not in database'))
    conn.close()
        
def time_check(start, end):
    for x in [start,end]:
        try: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
        except:print(f"{x} has incorret format")