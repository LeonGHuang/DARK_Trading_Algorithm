import os
import requests
import pandas as pd
from src.sqlSrcipts import sql_connect


def build_params(name, start, end, limit=50, page=1, condense=True, has_sold=True, api_key=None):
    return {
        "key": api_key,
        "item": name,
        "limit": str(limit),
        "page": str(page),
        "condense": str(condense).lower(),
        "has_sold": str(has_sold).lower(),
        "from": start,
        "to": end,
    }


def fetch_all(name, start, end, limit=50, api_key=None):
    base_url = "https://api.darkerdb.com/v1/market"
    session = requests.Session()
    all_items = []
    page = 1

    while True:
        params = build_params(name, start, end, limit=limit, page=page, api_key=api_key)
        resp = session.get(base_url, params=params)
        resp.raise_for_status()
        payload = resp.json()

        body = payload.get("body") or []
        all_items.extend(body)

        pagination = payload.get("pagination", {})
        # stop if count is zero or no more items returned
        if pagination.get("count", 0) == 0 or not body:
            break
        page += 1

    return all_items


def df_from_items(items):
    if not items:
        return pd.DataFrame()
    df = pd.json_normalize(items, sep=",")
    return df


def upsert_to_db(df, table_name="test"):
    if df.empty:
        return

    cols = [
        "id",
        "cursor",
        "item_id",
        "item",
        "price",
        "price_per_unit",
        "created_at",
        "expires_at",
        "sold_at",
    ]

    # keep only the columns we know about and in that order
    df = df.reindex(columns=[c for c in cols if c in df.columns])

    conn = sql_connect()
    cursor = conn.cursor()

    # create table (simple schema) - adjust types as needed for your DB
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            id bigint,
            cursor bigint PRIMARY KEY,
            item_id text,
            item text,
            price bigint,
            price_per_unit bigint,
            created_at text,
            expires_at text,
            sold_at text
        );
    """)

    insert_cols = list(df.columns)
    placeholders = ", ".join(["%s"] * len(insert_cols))
    insert_sql = f"INSERT INTO {table_name} ({', '.join(insert_cols)}) VALUES ({placeholders})"

    import numpy as np

    records = df.where(pd.notnull(df), None).to_records(index=False)

    def _to_py(v):
        # convert numpy scalar types to native Python types for DB adapters
        if v is None:
            return None
        if isinstance(v, (np.integer,)):
            return int(v)
        if isinstance(v, (np.floating,)):
            return float(v)
        if isinstance(v, (np.bool_,)):
            return bool(v)
        # bytes/bytearray handling
        if isinstance(v, (bytes, bytearray)):
            return bytes(v)
        return v

    values = [tuple(_to_py(x) for x in r) for r in records]

    if values:
        cursor.executemany(insert_sql, values)

    conn.commit()
    conn.close()


def main():
    name = os.getenv("ITEM_NAME", "Gold Coin Chest")
    start = os.getenv("START", "2026-01-14")
    end = os.getenv("END", "2026-01-15")
    api_key = os.getenv("dark_api_key")

    items = fetch_all(name, start, end, limit=50, api_key=api_key)
    df = df_from_items(items)

    print(f"Fetched {len(items)} items")

    upsert_to_db(df, table_name="test")


if __name__ == "__main__":
    main()
