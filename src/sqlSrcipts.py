import os  # point to the environment variable without revealing them

import psycopg2  # used to connect to sql on pi
from dotenv import (
    load_dotenv,  # sends var in ignore text files into environment variable
)
from sqlalchemy import create_engine


def sql_engine():
    load_dotenv("/home/leon/projs/dark/gitignore/sql.env", override=True)
    sql_engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('sqlUSER')}:{os.getenv('sqlPASSWORD')}@{os.getenv('sqlHOST')}:{os.getenv('sqlPORT')}/{os.getenv('sqlDATABASE')}"
    )
    return sql_engine


def sql_connect():
    load_dotenv("/home/leon/projs/dark/gitignore/sql.env", override=True)
    try:
        conn = psycopg2.connect(
            host=os.getenv("sqlHOST"),
            port=os.getenv("sqlPORT"),
            database=os.getenv("sqlDATABASE"),
            user=os.getenv("sqlUSER"),
            password=os.getenv("sqlPASSWORD"),
        )
        print("connection to sql successful")
        return conn

    except:
        return print("connection to sql has failed")
