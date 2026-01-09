from dotenv import load_dotenv # sends var in ignore text files into environment variable
import os # point to the environment variable without revealing them
import psycopg2 # used to connect to sql on pi

load_dotenv('/home/leon/projs/dark/gitignore/sql.env', override=True)

try:
    conn = psycopg2.connect(
        host=os.getenv('sqlHOST'),
        port=os.getenv('sqlPORT'),
        database=os.getenv('sqlDATABASE'),
        user=os.getenv('sqlUSER'),
        password=os.getenv('sqlPASSWORD')
        )
    cursor = conn.cursor()
    print('connection successful')

except:
    print('connection to sql has failed')