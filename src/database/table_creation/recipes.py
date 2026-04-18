#%%
import src.database.scripts.sql as sql
from src.database.scrappers.recipes_fetch import recipes_parser

#%%
def drop_recipes_table():
    query = "DROP TABLE IF EXISTS season_8.recipes"
    cursor.execute(query)

def create_recipes_table():
    query = """
        CREATE TABLE IF NOT EXISTS recipes(
        recipe_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        item_id TEXT,
        amount INT,
        rarity TEXT,
        name TEXT,
        merchant TEXT,
        affinity INT
        )"""
    cursor.execute(query)

def item_id_from_db(name, rarity):
    query = f"""
    SELECT id FROM item_data
    WHERE name = '{name}'
    AND rarity = '{rarity}'
    """
    cursor.execute(query)
    item_id = cursor.fetchone()
    return item_id

# %%

def name_rairty_fetch():
    sql_index = []
    recipes = recipes_parser()
    for merchant in recipes.merchant_range():
        for row in recipes.row_range(merchant):
            recipes.row_target(merchant,row)
            amount, rarity, name = recipes.item()
            sql_index.append((name,rarity))
    return sql_index

name_rairty_fetch()


#%%
conn = sql.connect_pc()
cursor = conn.cursor()

item_id_from_db('Adventure Boots', 'Poor')

conn.commit()
conn.close()
# %%
