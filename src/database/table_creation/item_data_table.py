import src.database.scripts.sql as sql
from src.database.data_collectors.item_data_fetch import item_data_fetchdd

def drop_table(cursor):
        query = f"""
                DROP TABLE IF EXISTS item_data
                """
        cursor.execute(query)

def create_table(cursor):
        query = f"""
                CREATE TABLE IF NOT EXISTS item_data(
                id TEXT PRIMARY KEY,
                archetype TEXT,
                slug TEXT,
                name TEXT,
                flavour TEXT,
                icon TEXT,
                icon_url TEXT,
                rarity TEXT,
                patch TEXT,
                patch_name TEXT,
                season TEXT,
                season_label TEXT,
                is_new BOOLEAN,
                is_changed BOOLEAN,
                item_type TEXT,
                slot_type TEXT,
                armor_type TEXT,
                is_droppable BOOLEAN,
                is_tradable BOOLEAN,
                max_stack_size INT,
                inventory_width INT,
                inventory_height INT,
                gear_score INT,
                experience INT,
                vendor_price INT,
                wearing_delay_time INT,
                required_class TEXT[],
                origin_id TEXT,
                num_primary_attributes INT,
                num_secondary_attributes INT
                ) 
                """
        cursor.execute(query)


def main():
        conn = sql.connect_pod()
        cursor = conn.cursor()

        drop_table(cursor)
        create_table(cursor)

        conn.commit()

main()