import sqlite3
from datetime import datetime

def item_name(item):
    conn = sqlite3.connect("dark.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT name FROM items WHERE name = '{item}'")
    check = cursor.fetchall() != []
    
    if check == True:
        None
    else: 
        raise SyntaxError('item name is invalid')
        

def datetimecker(start,end):
    try:
        start_check = datetime.strptime(start,"%Y-%m-%dT%H:%M:%SZ")
    except: 
        raise SyntaxError('start time invalid')
    try:
        end_check = datetime.strptime(end,"%Y-%m-%dT%H:%M:%SZ")
    except:
        raise SyntaxError('end time is invalid')