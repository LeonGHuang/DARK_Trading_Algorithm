import requests
from bs4 import BeautifulSoup

#new the wiki pagew as changed

class merchant_recipes:

    merchant_list = ['Alchemist', 'Armourer', 'Goldsmith', 'Leathersmith', 'Tailor', 'Weaponsmith', 'Woodsman']
    rarity_map = {
        "rarity1":"Poor",
        "rarity2":"Common",
        "rarity3":"Uncommon",
        "rarity4":"Rare",
        "rarity5":"Epic",
        "rarity6":"Legendary",
        "rarity7":"Unique"
        }



    def __init__(self, merchant):
        url = f"https://darkanddarker.wiki.spellsandguns.com/{merchant}"
        self.soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        
    def row_range(self):
        return range(1, len(self.soup.tbody.find_all('tr')))

    def row_target(self, row_num):
        row = self.soup.tbody.find_all('tr')[row_num]
        self.col = row.find_all('td')



    def item(self):
        rarity = self.rarity_map[self.col[0].div.div['class'][0]]
        name = self.col[0].a['title']        
        amount = self.col[0].span.contents[0]
        return amount, rarity, name

    def ingredients(self):
        ingredients = []
        for ingredient in self.col[1].find_all('div')[1::2]:
            rarity = self.rarity_map[ingredient['class'][0]]
            name = ingredient.a['title']
            amount = ingredient.span.contents[0]
            ingredients.append((amount, rarity, name))
        return ingredients

    def vendor(self):
        merchcant = self.col[2].a.contents[0]
        try: 
            if self.col[3].contents[0] == '?':
                affinity = 0
            else: affinity = self.col[3].contents[0]

        except: affinity = '0'
        return merchcant, affinity