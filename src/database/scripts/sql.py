import os  # variable saved on os
import sys

import psycopg2 
from dotenv import load_dotenv # variable saved on .env files
from sqlalchemy import create_engine


def engine():
    load_dotenv("/home/leon/projs/dark/gitignore/sql.env", override=True)
    sql_engine = create_engine(f"""
        postgresql+psycopg2://{os.getenv('sqlUSER')}:{os.getenv('sqlPASSWORD')}
        @{os.getenv('sqlHOST')}:{os.getenv('sqlPORT')}/{os.getenv('sqlDATABASE')}
        """)
    return sql_engine


# old connection to pi, micro sd card died
def connect():
    load_dotenv("/home/leon/projs/dark/gitignore/sql.env", override=True)
    try:
        conn = psycopg2.connect(
            host = os.getenv("sqlHOST"),
            port = os.getenv("sqlPORT"),
            database = os.getenv("sqlDATABASE"),
            user = os.getenv("sqlUSER"),
            password = os.getenv("sqlPASSWORD"),
        )
        return conn
    except:
        return sys.exit("connection to sql has failed")


def connect_pc():
    load_dotenv("/home/leon/projs/dark/gitignore/sql.env", override=True)
    try:
        conn = psycopg2.connect(
            host = os.getenv("pc_HOST"),
            port = os.getenv("pc_PORT"),
            database = os.getenv("pc_DATABASE"),
            user = os.getenv("pc_USER"),
            password = os.getenv("pc_PASSWORD"),
        )
        return conn
    except:
        return sys.exit("connection to sql has failed")


def connect_pod():
    load_dotenv("/home/leon/projs/dark/.env/sql.env", override=True)
    try:
        conn = psycopg2.connect(
            host = os.getenv("pod_host"),
            port = os.getenv("pod_port"),
            database = os.getenv("pod_database"),
            user = os.getenv("pod_user"),
            password = os.getenv("pod_password"),
        )
        return conn
    except:
        return sys.exit("connection to postgres has failed")