import os # point to the environment variable without revealing them
from sqlalchemy import create_engine
from dotenv import load_dotenv # sends var in ignore text files into environment variable
import psycopg2 # used to connect to sql on pi


def sqlalchemy_engine():
    load_dotenv('/home/leon/projs/dark/gitignore/sql.env', override=True)
    sql_engine = create_engine(f"postgresql+psycopg2://{os.getenv('sqlUSER')}:{os.getenv('sqlPASSWORD')}@{os.getenv('sqlHOST')}:{os.getenv('sqlPORT')}/{os.getenv('sqlDATABASE')}").connect()
    return sql_engine


def psycopg2_connect():
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
        return('connection successful')

    except:
        return('connection to sql has failed')
