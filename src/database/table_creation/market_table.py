import src.database.scripts.sql as sql
import os

def drop_table(cursor):
        query = f"""
                DROP TABLE IF EXISTS history
                """
        cursor.execute(query)

def create_table(cursor):
        query = f"""
                CREATE TABLE IF NOT EXISTS market (
                id BIGINT PRIMARY KEY,
                cursor BIGINT,
                item_id TEXT,
                archetype TEXT,
                name TEXT,
                slot_TYPE TEXT,
                item_type TEXT,
                rarity TEXT,
                price INT,
                price_per_unit INT,
                quantity INT,
                listing_state TEXT,
                state_source TEXT,
                has_cancelled BOOLEAN,
                has_expired BOOLEAN,
                has_sold BOOLEAN,
                attributes JSONB,
                sockets JSONB,
                loot_state TEXT,
                created_at TIMESTAMPTZ,
                last_seen_at TIMESTAMPTZ,
                expires_at TIMESTAMPTZ,
                found_by TEXT, 
                )
                """
        cursor.execute(query)

def main():
        os.system('clear')
        conn = sql.connect_pod()
        cursor = conn.cursor()

        drop_table(cursor)
        create_table(cursor)

        conn.commit()

if __name__=="__main__":
        main()
