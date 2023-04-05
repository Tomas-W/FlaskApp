from flasktest import BASE_PATH, PUBG_API_KEY


# ------------------------------------------------------------- #
# ------------------------- PUBG ------------------------------ #
PUBG_PLAYER_ID_URL = "https://api.pubg.com/shards/steam/players?filter[playerNames]="
PUBG_SEASONS_URL = "https://api.pubg.com/shards/steam/seasons"
PUBG_API_HEADER = {
    "Authorization": f"Bearer {PUBG_API_KEY}",
    "Accept": "application/vnd.api+json",
}
TIMEOUT = 3  # API time before timeout
PUBG_STATS_LIST = ["damageDealt", "kills", "assists", "headshotKills", "roundMostKills",
                   "rideDistance", "top10s", "roundsPlayed", "wins"]
PUBG_DATAFRAME_PATH = f"{BASE_PATH}\\flasktest\\static\\data\\api\\pubg\\"
PUBG_DATA_PATH = f"{BASE_PATH}\\flasktest\\static\\data\\api\\pubg\\"
PUBG_IMAGE_PATH = f"{BASE_PATH}\\flasktest\\static\\images\\api\\pubg\\"
PUBG_IMAGE_PATH_RELATIVE = f"../static/images/api/pubg/"
PUBG_BAR_FONT = {
    "family": "Arial",
    "size": 19,
    "color": "rgb(34, 40, 49)",
}
PUBG_BAR_COLOR = "rgb(34, 40, 49)"
PUBG_BAR_BG_COLOR = "rgb(57, 62, 70)"
NR_OF_BARS = 6  # nr of bars created in the charts


# ------------------------------------------------------------ #
# ------------------------- CPI ------------------------------ #
CPI_DATA_FOLDER = f"{BASE_PATH}\\flasktest\\static\\data\\api\\cpi\\"
CPI_IMAGE_PATH = f"{BASE_PATH}\\flasktest\\static\\images\\api\\cpi\\"
CPI_IMAGE_PATH_RELATIVE = f"../static/images/api/cpi/"
CPI_CATEGORIES = ["appearance", "appliances", "fixed", "food", "luxury", "snacks"]
CPI_GRAPH_FONT = {
    "family": "Arial",
    "size": 24,
    "color": "#D2D8E4",
}
CPI_BG_COLOR = "#D2D8E4"
CPI_APPEARANCE = [('clothing_women', 'Clothing F'), ('clothing_men', 'Clothing M'),
                  ('clothing_kids', 'Clothing K'), ('shoes', 'Shoes'), ('bedding', 'Bedding'),
                  ('furniture', 'Furniture'), ('lighting', 'Lighting'), ('carpets', 'Carpets'),
                  ('plants_flowers', 'Plants&Flowers')]

CPI_APPLIANCES = [('small_appliances', 'Small App'), ('heating_cooling', 'Heating&Cooling'),
                  ('fridge_freezer', 'Fridge&Freezer'), ('washers_dryer_dish', 'Washer&Dryer'),
                  ('cooking_utils', 'Cooking'), ('tv_audio', 'TV&Audio'),
                  ('sound_music', 'Sound&Music'), ('cameras', 'Cameras'),
                  ('computing', 'Computing')]

CPI_FIXED = [('energy', 'Energy'), ('water', 'Water'), ('fuel', 'Fuel'),
             ('transport', 'Transport'), ('sports_utils', 'Sports Utils'), ('pets', 'Pets'),
             ('tv_subscriptions', 'TV Subscriptions'), ('sports_recreation', 'Sports&Rec'),
             ('literature', 'Literature')]

CPI_FOOD = [('oil_fat', 'Oil&Fat'), ('pasta_couscous', 'Pasta&Couscous'), ('rice', 'Rice'),
            ('bread', 'Bread'), ('milk_cheese_egg', 'Dairy'), ('meat', 'Meat'), ('fish', 'Fish'),
            ('vegetables', 'Vegetables'), ('baby_food', 'Baby food')]

CPI_LUXURY = [('dining_dancing', 'Dining&Dancing'), ('jewelry', 'Jewelry'),
              ('watches', 'Watches'), ('hotel_motel', 'Hotel&Motel'),
              ('flights_intern', 'Flights Intern'), ('new_cars', 'New Cars'),
              ('movie_theatre', 'Movie&Theatre'), ('alcohol', 'Alcohol'), ('tobacco', 'Tobacco')]

CPI_SNACKS = [('chocolate', 'Chocolate'), ('chips', 'Chips'), ('fastfood', 'Fastfood'),
              ('bakery', 'Bakery'), ('soda', 'Soda'), ('icecream', 'Icecream'), ('candy', 'Candy'),
              ('ready_meal', 'Ready Meal'), ('pizza', 'Pizza')]