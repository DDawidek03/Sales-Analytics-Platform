import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import numpy as np
from collections import defaultdict
from data_validation import DataValidator, quick_clean
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
else:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

available_locales = ['pl_PL', 'en_GB', 'de_DE', 'fr_FR', 'es_ES', 'it_IT', 
                    'nl_NL', 'sv_SE', 'de_AT', 'en_US', 'en_CA', 'pt_BR',
                    'ja_JP', 'zh_CN', 'ko_KR', 'en_AU', 'pt_PT', 'cs_CZ',
                    'da_DK', 'fi_FI', 'no_NO', 'tr_TR', 'ar_SA', 'en_IN']
fakers = {locale: Faker(locale) for locale in available_locales}

country_currencies = {
    'Poland': 'PLN',
    'United Kingdom': 'GBP',
    'Germany': 'EUR',
    'France': 'EUR',
    'Spain': 'EUR',
    'Italy': 'EUR',
    'Netherlands': 'EUR',
    'Sweden': 'SEK',
    'Austria': 'EUR',
    'Portugal': 'EUR',
    'Czech Republic': 'CZK',
    'Denmark': 'DKK',
    'Finland': 'EUR',
    'Norway': 'NOK',
    'Turkey': 'TRY',
    'United States': 'USD',
    'Canada': 'CAD',
    'Brazil': 'BRL',
    'Japan': 'JPY',
    'China': 'CNY',
    'South Korea': 'KRW',
    'India': 'INR',
    'Saudi Arabia': 'SAR',
    'Australia': 'AUD'
}

locale_to_country = {
    'pl_PL': 'Poland',
    'en_GB': 'United Kingdom',
    'de_DE': 'Germany',
    'fr_FR': 'France',
    'es_ES': 'Spain',
    'it_IT': 'Italy',
    'nl_NL': 'Netherlands',
    'sv_SE': 'Sweden',
    'de_AT': 'Austria',
    'en_US': 'United States',
    'en_CA': 'Canada',
    'pt_BR': 'Brazil',
    'ja_JP': 'Japan',
    'zh_CN': 'China',
    'ko_KR': 'South Korea',
    'en_AU': 'Australia',
    'pt_PT': 'Portugal',
    'cs_CZ': 'Czech Republic',
    'da_DK': 'Denmark',
    'fi_FI': 'Finland',
    'no_NO': 'Norway',
    'tr_TR': 'Turkey',
    'ar_SA': 'Saudi Arabia',
    'en_IN': 'India'
}

continents = {
    'Poland': 'Europe',
    'United Kingdom': 'Europe',
    'Germany': 'Europe',
    'France': 'Europe',
    'Spain': 'Europe',
    'Italy': 'Europe',
    'Netherlands': 'Europe',
    'Sweden': 'Europe',
    'Austria': 'Europe',
    'Portugal': 'Europe',
    'Czech Republic': 'Europe',
    'Denmark': 'Europe',
    'Finland': 'Europe',
    'Norway': 'Europe',
    'Turkey': 'Europe',
    'United States': 'North America',
    'Canada': 'North America',
    'Brazil': 'South America',
    'Japan': 'Asia',
    'China': 'Asia',
    'South Korea': 'Asia',
    'India': 'Asia',
    'Saudi Arabia': 'Asia',
    'Australia': 'Oceania'
}

country_regions = {
    'Poland': ['Mazowieckie', 'Małopolskie', 'Pomorskie', 'Dolnośląskie', 'Wielkopolskie'],
    'United Kingdom': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
    'Germany': ['Bayern', 'Berlin', 'Hamburg', 'Hessen', 'Nordrhein-Westfalen'],
    'France': ['Île-de-France', 'Provence-Alpes-Côte d\'Azur', 'Auvergne-Rhône-Alpes', 'Occitanie', 'Nouvelle-Aquitaine'],
    'Spain': ['Cataluña', 'Madrid', 'Andalucía', 'Comunidad Valenciana', 'País Vasco'],
    'Italy': ['Lazio', 'Lombardia', 'Campania', 'Veneto', 'Piemonte'],
    'Netherlands': ['Noord-Holland', 'Zuid-Holland', 'Utrecht', 'Noord-Brabant', 'Gelderland'],
    'Sweden': ['Stockholm', 'Västra Götaland', 'Skåne', 'Uppsala', 'Östergötland'],
    'Austria': ['Vienna', 'Styria', 'Upper Austria', 'Tyrol', 'Salzburg'],
    'Portugal': ['Lisboa', 'Porto', 'Algarve', 'Braga', 'Coimbra'],
    'Czech Republic': ['Prague', 'South Moravian', 'Moravian-Silesian', 'Olomouc', 'Plzeň'],
    'Denmark': ['Capital Region', 'Central Denmark', 'North Denmark', 'Zealand', 'Southern Denmark'],
    'Finland': ['Uusimaa', 'Pirkanmaa', 'Southwest Finland', 'North Ostrobothnia', 'Central Finland'],
    'Norway': ['Oslo', 'Viken', 'Rogaland', 'Vestland', 'Trøndelag'],
    'Turkey': ['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya'],
    'United States': ['California', 'Texas', 'New York', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio'],
    'Canada': ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Manitoba'],
    'Brazil': ['São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Bahia', 'Paraná'],
    'Japan': ['Tokyo', 'Osaka', 'Kanagawa', 'Aichi', 'Hokkaido'],
    'China': ['Beijing', 'Shanghai', 'Guangdong', 'Sichuan', 'Jiangsu'],
    'South Korea': ['Seoul', 'Busan', 'Gyeonggi', 'Incheon', 'Daegu'],
    'India': ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal'],
    'Saudi Arabia': ['Riyadh', 'Makkah', 'Eastern Province', 'Madinah', 'Asir'],
    'Australia': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia', 'South Australia']
}

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "sales_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_CATEGORIES = 15
NUM_PRODUCTS = 5000
NUM_PROMOTIONS = 500


START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2024, 12, 31)

fake = Faker()
customer_purchase_history = defaultdict(list)

validator = DataValidator(verbose=True)

print("Rozpoczynam generowanie danych dla SalesDB...")
print("Uzywam modelu wzrostu organicznego - dane beda rozne dla kazdego kraju i roku!")
print("[OK] Modul walidacji danych aktywny\n")

country_market_strength = {}
country_growth_rate = {}
country_volatility = {}  

print("Generowanie Countries...")
countries = []
country_id = 1
for locale, country_name in locale_to_country.items():
    if country_name in ['United States', 'China', 'Germany', 'United Kingdom']:
        market_strength = random.uniform(1.8, 3.5)
        growth_rate = random.uniform(1.4, 2.2)
        volatility = random.uniform(0.3, 0.7)
    elif country_name in ['Japan', 'France', 'Italy', 'Canada', 'Spain']:
        market_strength = random.uniform(1.0, 2.3)
        growth_rate = random.uniform(1.2, 1.9)
        volatility = random.uniform(0.4, 0.8)
    elif country_name in ['Poland', 'Brazil', 'India', 'South Korea']:
        market_strength = random.uniform(0.7, 1.8)
        growth_rate = random.uniform(1.5, 2.5)
        volatility = random.uniform(0.6, 1.2)
    else:
        market_strength = random.uniform(0.3, 1.2)
        growth_rate = random.uniform(0.8, 1.8)
        volatility = random.uniform(0.5, 1.5)       
    
    country_market_strength[country_name] = market_strength
    country_growth_rate[country_name] = growth_rate
    country_volatility[country_name] = volatility
    
    countries.append({
        'CountryID': country_id,
        'CountryName': country_name,
        'Continent': continents[country_name]
    })
    country_id += 1

countries_df = pd.DataFrame(countries)
countries_df.to_csv(os.path.join(OUTPUT_DIR, 'countries.csv'), index=False)
print(f"Wygenerowano {len(countries)} krajów z różnymi poziomami atrakcyjności rynkowej")

print("Generowanie DateDimension...")
dates = []
date_id = 1
current_date = START_DATE
while current_date <= END_DATE:
    dates.append({
        'DateID': date_id,
        'FullDate': current_date.strftime('%Y-%m-%d'),
        'Year': current_date.year,
        'Quarter': (current_date.month - 1) // 3 + 1,
        'Month': current_date.month,
        'MonthName': current_date.strftime('%B'),
        'Day': current_date.day,
        'DayOfWeek': current_date.strftime('%A')
    })
    date_id += 1
    current_date += timedelta(days=1)

dates_df = pd.DataFrame(dates)
dates_df.to_csv(os.path.join(OUTPUT_DIR, 'date_dimension.csv'), index=False)
print(f"Wygenerowano {len(dates)} dat")

print("Generowanie Regions...")
regions = []
region_id = 1
for country_row in countries:
    country_name = country_row['CountryName']
    country_id = country_row['CountryID']
    for region_name in country_regions[country_name]:
        regions.append({
            'RegionID': region_id,
            'RegionName': region_name,
            'CountryID': country_id
        })
        region_id += 1

regions_df = pd.DataFrame(regions)
regions_df.to_csv(os.path.join(OUTPUT_DIR, 'regions.csv'), index=False)
print(f"Wygenerowano {len(regions)} regionów")

print("Generowanie Categories...")

main_categories = [
    {'name': 'Electronics', 'color': '#1f77b4'},
    {'name': 'Clothing', 'color': '#ff7f0e'},
    {'name': 'Home & Garden', 'color': '#2ca02c'},
    {'name': 'Sports & Outdoors', 'color': '#d62728'},
    {'name': 'Books & Media', 'color': '#9467bd'},
    {'name': 'Toys & Games', 'color': '#8c564b'},
    {'name': 'Food & Beverages', 'color': '#e377c2'},
    {'name': 'Health & Beauty', 'color': '#7f7f7f'}
]

categories = []
category_id = 1

for cat_info in main_categories:
    categories.append({
        'CategoryID': category_id,
        'CategoryName': cat_info['name'],
        'ParentCategoryID': None,
        'Description': f'Main category for {cat_info["name"]}'
    })
    category_id += 1

subcategories = {
    'Electronics': ['Computers', 'Phones', 'Audio', 'Smart Home'],
    'Clothing': ['Men', 'Women', 'Kids', 'Shoes'],
    'Home & Garden': ['Furniture', 'Kitchen', 'Decor', 'Tools'],
    'Sports & Outdoors': ['Fitness', 'Camping', 'Cycling'],
    'Books & Media': ['Books', 'Movies', 'Music'],
    'Toys & Games': ['Board Games', 'Video Games', 'Kids Toys'],
    'Food & Beverages': ['Snacks', 'Drinks', 'Organic'],
    'Health & Beauty': ['Cosmetics', 'Personal Care', 'Wellness']
}

for parent_cat in categories[:8]:
    parent_id = parent_cat['CategoryID']
    parent_name = parent_cat['CategoryName']
    if parent_name in subcategories:
        for subcat_name in subcategories[parent_name]:
            categories.append({
                'CategoryID': category_id,
                'CategoryName': subcat_name,
                'ParentCategoryID': parent_id,
                'Description': f'{subcat_name} subcategory of {parent_name}'
            })
            category_id += 1

categories_df = pd.DataFrame(categories)
categories_df.to_csv(os.path.join(OUTPUT_DIR, 'categories.csv'), index=False)
print(f"Wygenerowano {len(categories)} kategorii")

print("Generowanie Sellers z wzrostem w czasie...")
sellers = []
seller_id = 1

years = list(range(START_DATE.year, END_DATE.year + 1))
year_weights = []

for year in years:
    year_progress = (year - START_DATE.year) / len(years)
    weight = 0.15 + (year_progress ** 1.8) * 3.5
    year_weights.append(weight)

total_weight = sum(year_weights)
year_weights = [w / total_weight for w in year_weights]

for region_row in regions:
    region_id = region_row['RegionID']
    country_id = region_row['CountryID']
    country_name = countries_df[countries_df['CountryID'] == country_id].iloc[0]['CountryName']
    market_strength = country_market_strength[country_name]
    
    base_sellers = int(random.uniform(2, 8) * market_strength)
    base_sellers = max(2, base_sellers)
    
    for _ in range(base_sellers):
        year = random.choices(years, weights=year_weights)[0]
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hire_date = datetime(year, month, day)
        
        locale = [loc for loc, c in locale_to_country.items() if c == country_name][0]
        fake = fakers[locale]
        
        seller_type_weights = {
            'individual': 0.6,
            'company': 0.3,
            'premium': 0.1
        }
        seller_type = random.choices(
            list(seller_type_weights.keys()),
            weights=list(seller_type_weights.values())
        )[0]
        
        sellers.append({
            'SellerID': seller_id,
            'FirstName': fake.first_name(),
            'LastName': fake.last_name(),
            'Email': fake.unique.email(),
            'Phone': fake.phone_number()[:20],
            'SellerType': seller_type,
            'RegionID': region_id,
            'HireDate': hire_date.strftime('%Y-%m-%d'),
            'CreatedAt': hire_date.strftime('%Y-%m-%d %H:%M:%S'),
            'UpdatedAt': None
        })
        seller_id += 1

sellers_df = pd.DataFrame(sellers)
sellers_df['SellerID'] = range(1, len(sellers_df) + 1)
sellers_df['HireDate_dt'] = pd.to_datetime(sellers_df['HireDate'])

sellers_df_clean = sellers_df[['SellerID', 'FirstName', 'LastName', 'Email', 'Phone', 'SellerType', 
                                'RegionID', 'HireDate', 'CreatedAt', 'UpdatedAt']].copy()
sellers_df_clean.to_csv(os.path.join(OUTPUT_DIR, 'sellers.csv'), index=False)
print(f"Wygenerowano {len(sellers)} sprzedawców (rozłożonych w czasie wg wzrostu platformy)")
print(f"  → Zakres: od {sellers_df['HireDate'].min()} do {sellers_df['HireDate'].max()}")

print("Generowanie Products...")

realistic_products = {
    'Electronics': [
        {'name': 'MacBook Pro 14" M3', 'brand': 'Apple', 'price_range': (1800, 2500)},
        {'name': 'MacBook Pro 16" M3 Max', 'brand': 'Apple', 'price_range': (2800, 3800)},
        {'name': 'MacBook Pro 16" M3 Pro', 'brand': 'Apple', 'price_range': (2400, 3500)},
        {'name': 'MacBook Air 15" M2', 'brand': 'Apple', 'price_range': (1300, 1700)},
        {'name': 'MacBook Air 13" M2', 'brand': 'Apple', 'price_range': (1200, 1600)},
        {'name': 'MacBook Air 13" M1', 'brand': 'Apple', 'price_range': (1000, 1400)},
        {'name': 'Dell XPS 15 9530', 'brand': 'Dell', 'price_range': (1400, 2000)},
        {'name': 'Dell XPS 17', 'brand': 'Dell', 'price_range': (1800, 2600)},
        {'name': 'Dell XPS 13 Plus', 'brand': 'Dell', 'price_range': (1100, 1600)},
        {'name': 'Dell XPS 13', 'brand': 'Dell', 'price_range': (1000, 1500)},
        {'name': 'Dell Inspiron 16', 'brand': 'Dell', 'price_range': (700, 1100)},
        {'name': 'ThinkPad X1 Carbon Gen 11', 'brand': 'Lenovo', 'price_range': (1300, 1800)},
        {'name': 'ThinkPad X1 Yoga', 'brand': 'Lenovo', 'price_range': (1400, 1900)},
        {'name': 'ThinkPad T14 Gen 4', 'brand': 'Lenovo', 'price_range': (900, 1300)},
        {'name': 'ThinkPad T16', 'brand': 'Lenovo', 'price_range': (1000, 1400)},
        {'name': 'ThinkPad P1 Gen 6', 'brand': 'Lenovo', 'price_range': (1800, 2500)},
        {'name': 'Lenovo Yoga 9i', 'brand': 'Lenovo', 'price_range': (1200, 1700)},
        {'name': 'Lenovo IdeaPad', 'brand': 'Lenovo', 'price_range': (500, 900)},
        {'name': 'HP Spectre x360 14', 'brand': 'HP', 'price_range': (1100, 1500)},
        {'name': 'HP Spectre x360 16', 'brand': 'HP', 'price_range': (1300, 1800)},
        {'name': 'HP EliteBook 840', 'brand': 'HP', 'price_range': (1000, 1400)},
        {'name': 'HP EliteBook 860', 'brand': 'HP', 'price_range': (1100, 1500)},
        {'name': 'HP Envy 17', 'brand': 'HP', 'price_range': (900, 1300)},
        {'name': 'HP Pavilion 15', 'brand': 'HP', 'price_range': (600, 1000)},
        {'name': 'ASUS ZenBook 14', 'brand': 'ASUS', 'price_range': (800, 1200)},
        {'name': 'ASUS ZenBook Pro 15', 'brand': 'ASUS', 'price_range': (1400, 1900)},
        {'name': 'ASUS VivoBook', 'brand': 'ASUS', 'price_range': (500, 900)},
        {'name': 'ASUS ROG Zephyrus', 'brand': 'ASUS', 'price_range': (1600, 2400)},
        {'name': 'Surface Laptop 5 13"', 'brand': 'Microsoft', 'price_range': (1000, 1500)},
        {'name': 'Surface Laptop 5 15"', 'brand': 'Microsoft', 'price_range': (1200, 1700)},
        {'name': 'Surface Laptop Studio', 'brand': 'Microsoft', 'price_range': (1600, 2400)},
        {'name': 'Surface Pro 9', 'brand': 'Microsoft', 'price_range': (1000, 1600)},
        {'name': 'Razer Blade 14', 'brand': 'Razer', 'price_range': (1700, 2400)},
        {'name': 'Razer Blade 15', 'brand': 'Razer', 'price_range': (1800, 2500)},
        {'name': 'Razer Blade 17', 'brand': 'Razer', 'price_range': (2200, 3000)},
        {'name': 'MSI Stealth 14', 'brand': 'MSI', 'price_range': (1300, 1900)},
        {'name': 'MSI Stealth 15', 'brand': 'MSI', 'price_range': (1400, 2000)},
        {'name': 'MSI Stealth 17', 'brand': 'MSI', 'price_range': (1700, 2400)},
        {'name': 'MSI Creator Z17', 'brand': 'MSI', 'price_range': (2000, 2800)},
        {'name': 'Acer Swift 3', 'brand': 'Acer', 'price_range': (600, 1000)},
        {'name': 'Acer Swift 5', 'brand': 'Acer', 'price_range': (800, 1200)},
        {'name': 'Acer Aspire 5', 'brand': 'Acer', 'price_range': (500, 800)},
        {'name': 'Samsung Galaxy Book3 Pro', 'brand': 'Samsung', 'price_range': (1100, 1600)},
        {'name': 'Samsung Galaxy Book3 Ultra', 'brand': 'Samsung', 'price_range': (1800, 2400)},
        {'name': 'LG Gram 17', 'brand': 'LG', 'price_range': (1400, 1900)},
        {'name': 'LG Gram 16', 'brand': 'LG', 'price_range': (1200, 1700)},
        {'name': 'LG Gram 14', 'brand': 'LG', 'price_range': (1000, 1400)},
    ],
    'Computers': [
        {'name': 'Gaming PC RTX 4090', 'brand': 'Custom Build', 'price_range': (2800, 4000)},
        {'name': 'Gaming PC RTX 4080 Super', 'brand': 'Custom Build', 'price_range': (2200, 3200)},
        {'name': 'Gaming PC RTX 4080', 'brand': 'Custom Build', 'price_range': (2000, 2800)},
        {'name': 'Gaming PC RTX 4070 Ti Super', 'brand': 'Custom Build', 'price_range': (1800, 2500)},
        {'name': 'Gaming PC RTX 4070 Ti', 'brand': 'Custom Build', 'price_range': (1600, 2300)},
        {'name': 'Gaming PC RTX 4070 Super', 'brand': 'Custom Build', 'price_range': (1500, 2200)},
        {'name': 'Gaming PC RTX 4070', 'brand': 'Custom Build', 'price_range': (1400, 2000)},
        {'name': 'Gaming PC RTX 4060 Ti', 'brand': 'Custom Build', 'price_range': (1100, 1600)},
        {'name': 'Gaming PC RTX 4060', 'brand': 'Custom Build', 'price_range': (1000, 1500)},
        {'name': 'Gaming PC RTX 3060', 'brand': 'Custom Build', 'price_range': (800, 1200)},
        {'name': 'Gaming PC AMD RX 7900 XTX', 'brand': 'Custom Build', 'price_range': (2200, 3000)},
        {'name': 'Gaming PC AMD RX 7900 XT', 'brand': 'Custom Build', 'price_range': (1900, 2600)},
        {'name': 'Gaming PC AMD RX 7800 XT', 'brand': 'Custom Build', 'price_range': (1500, 2100)},
        {'name': 'Gaming PC AMD RX 7700 XT', 'brand': 'Custom Build', 'price_range': (1300, 1800)},
        {'name': 'iMac 24" M3', 'brand': 'Apple', 'price_range': (1500, 2100)},
        {'name': 'iMac 24" M1', 'brand': 'Apple', 'price_range': (1300, 1800)},
        {'name': 'Mac Studio M2 Max', 'brand': 'Apple', 'price_range': (2000, 2800)},
        {'name': 'Mac Studio M2 Ultra', 'brand': 'Apple', 'price_range': (3500, 5000)},
        {'name': 'Mac Pro M2 Ultra', 'brand': 'Apple', 'price_range': (6500, 9000)},
        {'name': 'Mac Mini M2', 'brand': 'Apple', 'price_range': (600, 900)},
        {'name': 'Mac Mini M2 Pro', 'brand': 'Apple', 'price_range': (1300, 1700)},
        {'name': 'ASUS ROG Strix Desktop', 'brand': 'ASUS', 'price_range': (1200, 1800)},
        {'name': 'ASUS TUF Gaming Desktop', 'brand': 'ASUS', 'price_range': (900, 1400)},
        {'name': 'Alienware Aurora R15', 'brand': 'Dell', 'price_range': (1700, 2500)},
        {'name': 'Alienware Aurora R16', 'brand': 'Dell', 'price_range': (1900, 2800)},
        {'name': 'Dell G15 Gaming Desktop', 'brand': 'Dell', 'price_range': (900, 1400)},
        {'name': 'Dell Inspiron Desktop', 'brand': 'Dell', 'price_range': (500, 800)},
        {'name': 'Dell XPS Desktop', 'brand': 'Dell', 'price_range': (1000, 1600)},
        {'name': 'HP Pavilion Desktop', 'brand': 'HP', 'price_range': (600, 1000)},
        {'name': 'HP Omen 45L', 'brand': 'HP', 'price_range': (1800, 2600)},
        {'name': 'HP Omen 40L', 'brand': 'HP', 'price_range': (1500, 2200)},
        {'name': 'Lenovo Legion Tower 7i', 'brand': 'Lenovo', 'price_range': (1900, 2700)},
        {'name': 'Lenovo Legion Tower 5i', 'brand': 'Lenovo', 'price_range': (1200, 1800)},
        {'name': 'Lenovo IdeaCentre', 'brand': 'Lenovo', 'price_range': (500, 900)},
        {'name': 'Corsair Vengeance i7500', 'brand': 'Corsair', 'price_range': (2200, 3200)},
        {'name': 'NZXT Player Three', 'brand': 'NZXT', 'price_range': (2000, 2800)},
        {'name': 'Acer Predator Orion', 'brand': 'Acer', 'price_range': (1600, 2400)},
    ],
    'Phones': [
        {'name': 'iPhone 15 Pro Max', 'brand': 'Apple', 'price_range': (1200, 1400)},
        {'name': 'iPhone 15 Pro', 'brand': 'Apple', 'price_range': (1000, 1200)},
        {'name': 'iPhone 15 Plus', 'brand': 'Apple', 'price_range': (900, 1100)},
        {'name': 'iPhone 15', 'brand': 'Apple', 'price_range': (800, 1000)},
        {'name': 'iPhone 14 Pro Max', 'brand': 'Apple', 'price_range': (1000, 1200)},
        {'name': 'iPhone 14 Pro', 'brand': 'Apple', 'price_range': (900, 1100)},
        {'name': 'iPhone 14 Plus', 'brand': 'Apple', 'price_range': (800, 1000)},
        {'name': 'iPhone 14', 'brand': 'Apple', 'price_range': (700, 900)},
        {'name': 'iPhone 13 Pro Max', 'brand': 'Apple', 'price_range': (800, 1000)},
        {'name': 'iPhone 13 Pro', 'brand': 'Apple', 'price_range': (700, 900)},
        {'name': 'iPhone 13', 'brand': 'Apple', 'price_range': (600, 800)},
        {'name': 'iPhone 13 mini', 'brand': 'Apple', 'price_range': (500, 700)},
        {'name': 'iPhone SE 2022', 'brand': 'Apple', 'price_range': (400, 550)},
        {'name': 'Samsung Galaxy S24 Ultra', 'brand': 'Samsung', 'price_range': (1200, 1400)},
        {'name': 'Samsung Galaxy S24+', 'brand': 'Samsung', 'price_range': (1000, 1200)},
        {'name': 'Samsung Galaxy S24', 'brand': 'Samsung', 'price_range': (850, 1050)},
        {'name': 'Samsung Galaxy S23 Ultra', 'brand': 'Samsung', 'price_range': (1000, 1200)},
        {'name': 'Samsung Galaxy S23+', 'brand': 'Samsung', 'price_range': (850, 1050)},
        {'name': 'Samsung Galaxy S23', 'brand': 'Samsung', 'price_range': (750, 950)},
        {'name': 'Samsung Galaxy S23 FE', 'brand': 'Samsung', 'price_range': (550, 700)},
        {'name': 'Samsung Galaxy A54 5G', 'brand': 'Samsung', 'price_range': (400, 600)},
        {'name': 'Samsung Galaxy A34 5G', 'brand': 'Samsung', 'price_range': (300, 450)},
        {'name': 'Samsung Galaxy A14', 'brand': 'Samsung', 'price_range': (150, 250)},
        {'name': 'Samsung Galaxy Z Fold 5', 'brand': 'Samsung', 'price_range': (1700, 2000)},
        {'name': 'Samsung Galaxy Z Flip 5', 'brand': 'Samsung', 'price_range': (950, 1150)},
        {'name': 'Google Pixel 8 Pro', 'brand': 'Google', 'price_range': (950, 1150)},
        {'name': 'Google Pixel 8', 'brand': 'Google', 'price_range': (700, 900)},
        {'name': 'Google Pixel 7a', 'brand': 'Google', 'price_range': (450, 600)},
        {'name': 'Google Pixel 7 Pro', 'brand': 'Google', 'price_range': (800, 1000)},
        {'name': 'Google Pixel 7', 'brand': 'Google', 'price_range': (550, 750)},
        {'name': 'OnePlus 12', 'brand': 'OnePlus', 'price_range': (750, 950)},
        {'name': 'OnePlus 12R', 'brand': 'OnePlus', 'price_range': (500, 650)},
        {'name': 'OnePlus 11', 'brand': 'OnePlus', 'price_range': (650, 850)},
        {'name': 'OnePlus Open', 'brand': 'OnePlus', 'price_range': (1600, 1900)},
        {'name': 'OnePlus Nord 3', 'brand': 'OnePlus', 'price_range': (350, 500)},
        {'name': 'Xiaomi 14 Ultra', 'brand': 'Xiaomi', 'price_range': (1100, 1400)},
        {'name': 'Xiaomi 14 Pro', 'brand': 'Xiaomi', 'price_range': (900, 1100)},
        {'name': 'Xiaomi 14', 'brand': 'Xiaomi', 'price_range': (700, 900)},
        {'name': 'Xiaomi 13T Pro', 'brand': 'Xiaomi', 'price_range': (600, 800)},
        {'name': 'Xiaomi 13T', 'brand': 'Xiaomi', 'price_range': (500, 700)},
        {'name': 'Xiaomi Redmi Note 13 Pro+', 'brand': 'Xiaomi', 'price_range': (350, 500)},
        {'name': 'Xiaomi Redmi Note 13 Pro', 'brand': 'Xiaomi', 'price_range': (280, 400)},
        {'name': 'Xiaomi Redmi Note 13', 'brand': 'Xiaomi', 'price_range': (200, 320)},
        {'name': 'Xiaomi Poco X6 Pro', 'brand': 'Xiaomi', 'price_range': (300, 450)},
        {'name': 'Xiaomi Poco F5', 'brand': 'Xiaomi', 'price_range': (350, 500)},
        {'name': 'Motorola Edge 40 Pro', 'brand': 'Motorola', 'price_range': (600, 800)},
        {'name': 'Motorola Edge 40', 'brand': 'Motorola', 'price_range': (500, 700)},
        {'name': 'Motorola Edge 30 Ultra', 'brand': 'Motorola', 'price_range': (700, 900)},
        {'name': 'Motorola Razr 40 Ultra', 'brand': 'Motorola', 'price_range': (950, 1150)},
        {'name': 'Motorola Moto G84', 'brand': 'Motorola', 'price_range': (250, 380)},
        {'name': 'Nokia XR21', 'brand': 'Nokia', 'price_range': (450, 600)},
        {'name': 'Nokia G42', 'brand': 'Nokia', 'price_range': (200, 300)},
        {'name': 'Sony Xperia 1 V', 'brand': 'Sony', 'price_range': (1200, 1500)},
        {'name': 'Sony Xperia 5 V', 'brand': 'Sony', 'price_range': (850, 1050)},
        {'name': 'Sony Xperia 10 V', 'brand': 'Sony', 'price_range': (400, 550)},
        {'name': 'OPPO Find X6 Pro', 'brand': 'OPPO', 'price_range': (900, 1200)},
        {'name': 'OPPO Reno 10 Pro+', 'brand': 'OPPO', 'price_range': (550, 750)},
        {'name': 'Vivo X100 Pro', 'brand': 'Vivo', 'price_range': (950, 1250)},
        {'name': 'Realme GT 5 Pro', 'brand': 'Realme', 'price_range': (550, 750)},
        {'name': 'Nothing Phone (2)', 'brand': 'Nothing', 'price_range': (550, 700)},
    ],
    'Audio': [
        {'name': 'AirPods Pro 2', 'brand': 'Apple', 'price_range': (220, 280)},
        {'name': 'AirPods Pro', 'brand': 'Apple', 'price_range': (180, 240)},
        {'name': 'AirPods Max', 'brand': 'Apple', 'price_range': (500, 600)},
        {'name': 'AirPods 3', 'brand': 'Apple', 'price_range': (150, 200)},
        {'name': 'AirPods 2', 'brand': 'Apple', 'price_range': (100, 150)},
        {'name': 'Sony WH-1000XM5', 'brand': 'Sony', 'price_range': (350, 450)},
        {'name': 'Sony WH-1000XM4', 'brand': 'Sony', 'price_range': (280, 380)},
        {'name': 'Sony WF-1000XM5', 'brand': 'Sony', 'price_range': (280, 350)},
        {'name': 'Sony WF-1000XM4', 'brand': 'Sony', 'price_range': (220, 300)},
        {'name': 'Sony WH-CH720N', 'brand': 'Sony', 'price_range': (120, 180)},
        {'name': 'Sony LinkBuds S', 'brand': 'Sony', 'price_range': (150, 210)},
        {'name': 'Bose QuietComfort Ultra', 'brand': 'Bose', 'price_range': (380, 480)},
        {'name': 'Bose QuietComfort 45', 'brand': 'Bose', 'price_range': (300, 400)},
        {'name': 'Bose QuietComfort Ultra Earbuds', 'brand': 'Bose', 'price_range': (280, 350)},
        {'name': 'Bose QuietComfort Earbuds II', 'brand': 'Bose', 'price_range': (250, 320)},
        {'name': 'Bose Sport Earbuds', 'brand': 'Bose', 'price_range': (150, 200)},
        {'name': 'Bose SoundLink Flex', 'brand': 'Bose', 'price_range': (120, 170)},
        {'name': 'JBL Flip 6', 'brand': 'JBL', 'price_range': (100, 150)},
        {'name': 'JBL Flip 5', 'brand': 'JBL', 'price_range': (80, 130)},
        {'name': 'JBL Charge 5', 'brand': 'JBL', 'price_range': (150, 200)},
        {'name': 'JBL Xtreme 3', 'brand': 'JBL', 'price_range': (300, 400)},
        {'name': 'JBL Xtreme 4', 'brand': 'JBL', 'price_range': (350, 450)},
        {'name': 'JBL Boombox 3', 'brand': 'JBL', 'price_range': (400, 550)},
        {'name': 'JBL PartyBox 310', 'brand': 'JBL', 'price_range': (450, 600)},
        {'name': 'JBL Tune 770NC', 'brand': 'JBL', 'price_range': (100, 150)},
        {'name': 'Sennheiser Momentum 4', 'brand': 'Sennheiser', 'price_range': (320, 420)},
        {'name': 'Sennheiser Momentum True Wireless 3', 'brand': 'Sennheiser', 'price_range': (250, 330)},
        {'name': 'Sennheiser HD 660S2', 'brand': 'Sennheiser', 'price_range': (450, 600)},
        {'name': 'Beats Studio Pro', 'brand': 'Beats', 'price_range': (320, 400)},
        {'name': 'Beats Solo 4', 'brand': 'Beats', 'price_range': (180, 250)},
        {'name': 'Beats Fit Pro', 'brand': 'Beats', 'price_range': (180, 240)},
        {'name': 'Beats Studio Buds+', 'brand': 'Beats', 'price_range': (150, 200)},
        {'name': 'Marshall Major IV', 'brand': 'Marshall', 'price_range': (120, 180)},
        {'name': 'Marshall Motif II A.N.C', 'brand': 'Marshall', 'price_range': (150, 210)},
        {'name': 'Marshall Emberton II', 'brand': 'Marshall', 'price_range': (140, 190)},
        {'name': 'Marshall Willen', 'brand': 'Marshall', 'price_range': (100, 150)},
        {'name': 'Anker Soundcore Liberty 4', 'brand': 'Anker', 'price_range': (100, 150)},
        {'name': 'Anker Soundcore Space Q45', 'brand': 'Anker', 'price_range': (120, 180)},
        {'name': 'Jabra Elite 10', 'brand': 'Jabra', 'price_range': (220, 300)},
        {'name': 'Jabra Elite 85t', 'brand': 'Jabra', 'price_range': (180, 250)},
        {'name': 'Samsung Galaxy Buds2 Pro', 'brand': 'Samsung', 'price_range': (200, 270)},
        {'name': 'Samsung Galaxy Buds2', 'brand': 'Samsung', 'price_range': (120, 180)},
        {'name': 'Bang & Olufsen Beoplay H95', 'brand': 'B&O', 'price_range': (700, 900)},
        {'name': 'Bang & Olufsen Beoplay EX', 'brand': 'B&O', 'price_range': (350, 450)},
        {'name': 'Audio-Technica ATH-M50x', 'brand': 'Audio-Technica', 'price_range': (130, 190)},
        {'name': 'Shure AONIC 50', 'brand': 'Shure', 'price_range': (280, 380)},
        {'name': 'Ultimate Ears BOOM 4', 'brand': 'Ultimate Ears', 'price_range': (120, 180)},
        {'name': 'Ultimate Ears MEGABOOM 3', 'brand': 'Ultimate Ears', 'price_range': (180, 250)},
        {'name': 'Sonos Move 2', 'brand': 'Sonos', 'price_range': (400, 500)},
        {'name': 'Sonos Era 300', 'brand': 'Sonos', 'price_range': (400, 500)},
        {'name': 'Sonos Era 100', 'brand': 'Sonos', 'price_range': (220, 300)},
        {'name': 'Sonos Roam', 'brand': 'Sonos', 'price_range': (150, 210)},
        {'name': 'Harman Kardon Onyx Studio 8', 'brand': 'Harman Kardon', 'price_range': (350, 450)},
    ],
    'Smart Home': [
        {'name': 'Echo Dot 5th Gen', 'brand': 'Amazon', 'price_range': (40, 60)},
        {'name': 'Echo 4th Gen', 'brand': 'Amazon', 'price_range': (80, 120)},
        {'name': 'Echo Show 5', 'brand': 'Amazon', 'price_range': (70, 110)},
        {'name': 'Echo Show 8', 'brand': 'Amazon', 'price_range': (110, 160)},
        {'name': 'Echo Show 10', 'brand': 'Amazon', 'price_range': (220, 300)},
        {'name': 'Echo Show 15', 'brand': 'Amazon', 'price_range': (250, 330)},
        {'name': 'Echo Studio', 'brand': 'Amazon', 'price_range': (180, 250)},
        {'name': 'Google Nest Hub 2nd Gen', 'brand': 'Google', 'price_range': (80, 120)},
        {'name': 'Google Nest Hub Max', 'brand': 'Google', 'price_range': (200, 270)},
        {'name': 'Google Nest Audio', 'brand': 'Google', 'price_range': (80, 120)},
        {'name': 'Google Nest Mini', 'brand': 'Google', 'price_range': (40, 60)},
        {'name': 'HomePod', 'brand': 'Apple', 'price_range': (280, 350)},
        {'name': 'HomePod mini', 'brand': 'Apple', 'price_range': (90, 130)},
        {'name': 'Ring Video Doorbell Pro 2', 'brand': 'Ring', 'price_range': (220, 300)},
        {'name': 'Ring Video Doorbell 4', 'brand': 'Ring', 'price_range': (180, 250)},
        {'name': 'Ring Video Doorbell', 'brand': 'Ring', 'price_range': (90, 150)},
        {'name': 'Ring Stick Up Cam Battery', 'brand': 'Ring', 'price_range': (90, 140)},
        {'name': 'Ring Floodlight Cam Wired Plus', 'brand': 'Ring', 'price_range': (200, 280)},
        {'name': 'Nest Doorbell Battery', 'brand': 'Google', 'price_range': (160, 220)},
        {'name': 'Nest Doorbell Wired', 'brand': 'Google', 'price_range': (140, 200)},
        {'name': 'Nest Cam Indoor', 'brand': 'Google', 'price_range': (120, 180)},
        {'name': 'Nest Cam Outdoor', 'brand': 'Google', 'price_range': (160, 230)},
        {'name': 'Nest Learning Thermostat', 'brand': 'Google', 'price_range': (220, 300)},
        {'name': 'Nest Thermostat', 'brand': 'Google', 'price_range': (120, 180)},
        {'name': 'Ecobee SmartThermostat', 'brand': 'Ecobee', 'price_range': (220, 300)},
        {'name': 'Philips Hue Bridge', 'brand': 'Philips', 'price_range': (50, 80)},
        {'name': 'Philips Hue White Starter Kit', 'brand': 'Philips', 'price_range': (100, 150)},
        {'name': 'Philips Hue Color Starter Kit', 'brand': 'Philips', 'price_range': (180, 250)},
        {'name': 'Philips Hue Gradient Lightstrip', 'brand': 'Philips', 'price_range': (180, 260)},
        {'name': 'Philips Hue Play Light Bar', 'brand': 'Philips', 'price_range': (120, 180)},
        {'name': 'LIFX Color Bulb', 'brand': 'LIFX', 'price_range': (50, 80)},
        {'name': 'Wyze Cam v3', 'brand': 'Wyze', 'price_range': (30, 50)},
        {'name': 'Wyze Cam Pan v3', 'brand': 'Wyze', 'price_range': (40, 60)},
        {'name': 'Arlo Pro 5', 'brand': 'Arlo', 'price_range': (200, 280)},
        {'name': 'Arlo Essential', 'brand': 'Arlo', 'price_range': (120, 180)},
        {'name': 'Blink Video Doorbell', 'brand': 'Amazon', 'price_range': (50, 80)},
        {'name': 'Blink Outdoor', 'brand': 'Amazon', 'price_range': (80, 120)},
        {'name': 'TP-Link Kasa Smart Plug', 'brand': 'TP-Link', 'price_range': (15, 30)},
        {'name': 'TP-Link Tapo Camera', 'brand': 'TP-Link', 'price_range': (30, 50)},
        {'name': 'Eufy Video Doorbell', 'brand': 'Eufy', 'price_range': (140, 200)},
        {'name': 'Eufy Security Camera', 'brand': 'Eufy', 'price_range': (80, 130)},
    ],
    'Clothing': [
        {'name': 'Levi\'s 501 Jeans', 'brand': 'Levi\'s', 'price_range': (60, 100)},
        {'name': 'Levi\'s 511 Slim', 'brand': 'Levi\'s', 'price_range': (70, 110)},
        {'name': 'Wrangler Jeans', 'brand': 'Wrangler', 'price_range': (50, 80)},
        {'name': 'Nike Air Max 90', 'brand': 'Nike', 'price_range': (120, 180)},
        {'name': 'Nike Air Force 1', 'brand': 'Nike', 'price_range': (100, 150)},
        {'name': 'Nike Dunk Low', 'brand': 'Nike', 'price_range': (110, 160)},
        {'name': 'Adidas Ultraboost', 'brand': 'Adidas', 'price_range': (150, 200)},
        {'name': 'Adidas Superstar', 'brand': 'Adidas', 'price_range': (80, 120)},
        {'name': 'Adidas Stan Smith', 'brand': 'Adidas', 'price_range': (70, 110)},
        {'name': 'Puma Suede', 'brand': 'Puma', 'price_range': (60, 100)},
        {'name': 'Converse Chuck Taylor', 'brand': 'Converse', 'price_range': (50, 80)},
        {'name': 'Vans Old Skool', 'brand': 'Vans', 'price_range': (60, 90)},
        {'name': 'H&M Basic T-Shirt', 'brand': 'H&M', 'price_range': (10, 20)},
        {'name': 'Zara Jacket', 'brand': 'Zara', 'price_range': (50, 90)},
        {'name': 'Uniqlo Sweater', 'brand': 'Uniqlo', 'price_range': (30, 60)},
    ],
    'Men': [
        {'name': 'Hugo Boss Suit', 'brand': 'Hugo Boss', 'price_range': (400, 700)},
        {'name': 'Hugo Boss Blazer', 'brand': 'Hugo Boss', 'price_range': (300, 500)},
        {'name': 'Tommy Hilfiger Shirt', 'brand': 'Tommy Hilfiger', 'price_range': (60, 100)},
        {'name': 'Tommy Hilfiger Polo', 'brand': 'Tommy Hilfiger', 'price_range': (50, 90)},
        {'name': 'Calvin Klein Jeans', 'brand': 'Calvin Klein', 'price_range': (80, 120)},
        {'name': 'Calvin Klein Underwear', 'brand': 'Calvin Klein', 'price_range': (30, 50)},
        {'name': 'Ralph Lauren Polo', 'brand': 'Ralph Lauren', 'price_range': (80, 130)},
        {'name': 'Lacoste Polo', 'brand': 'Lacoste', 'price_range': (90, 140)},
    ],
    'Women': [
        {'name': 'Michael Kors Dress', 'brand': 'Michael Kors', 'price_range': (120, 250)},
        {'name': 'Michael Kors Bag', 'brand': 'Michael Kors', 'price_range': (200, 400)},
        {'name': 'Gucci Handbag', 'brand': 'Gucci', 'price_range': (800, 1500)},
        {'name': 'Louis Vuitton Bag', 'brand': 'Louis Vuitton', 'price_range': (1000, 2000)},
        {'name': 'Prada Bag', 'brand': 'Prada', 'price_range': (900, 1600)},
        {'name': 'Coach Purse', 'brand': 'Coach', 'price_range': (250, 500)},
        {'name': 'Mango Blouse', 'brand': 'Mango', 'price_range': (30, 60)},
        {'name': 'Mango Dress', 'brand': 'Mango', 'price_range': (50, 100)},
        {'name': 'Forever 21 Dress', 'brand': 'Forever 21', 'price_range': (25, 50)},
    ],
    'Kids': [
        {'name': 'Gap Kids Jeans', 'brand': 'Gap', 'price_range': (25, 45)},
        {'name': 'Gap Kids Hoodie', 'brand': 'Gap', 'price_range': (30, 55)},
        {'name': 'Disney T-Shirt', 'brand': 'Disney', 'price_range': (15, 30)},
        {'name': 'Disney Dress', 'brand': 'Disney', 'price_range': (25, 45)},
        {'name': 'Carter\'s Baby Set', 'brand': 'Carter\'s', 'price_range': (20, 40)},
        {'name': 'OshKosh Overalls', 'brand': 'OshKosh', 'price_range': (30, 50)},
    ],
    'Shoes': [
        {'name': 'Nike Running Shoes', 'brand': 'Nike', 'price_range': (80, 140)},
        {'name': 'Adidas Running Shoes', 'brand': 'Adidas', 'price_range': (75, 130)},
        {'name': 'New Balance 574', 'brand': 'New Balance', 'price_range': (70, 110)},
        {'name': 'Timberland Boots', 'brand': 'Timberland', 'price_range': (150, 250)},
        {'name': 'Dr. Martens Boots', 'brand': 'Dr. Martens', 'price_range': (130, 200)},
        {'name': 'Clarks Desert Boots', 'brand': 'Clarks', 'price_range': (100, 160)},
    ],
    'Home & Garden': [
        {'name': 'IKEA Kallax Shelf', 'brand': 'IKEA', 'price_range': (60, 100)},
        {'name': 'IKEA Billy Bookcase', 'brand': 'IKEA', 'price_range': (50, 90)},
        {'name': 'IKEA Malm Dresser', 'brand': 'IKEA', 'price_range': (120, 200)},
        {'name': 'Philips Hue Bulbs', 'brand': 'Philips', 'price_range': (40, 80)},
        {'name': 'Philips Hue Light Strip', 'brand': 'Philips', 'price_range': (60, 100)},
        {'name': 'Dyson V15 Vacuum', 'brand': 'Dyson', 'price_range': (500, 700)},
        {'name': 'Dyson V12 Vacuum', 'brand': 'Dyson', 'price_range': (400, 600)},
        {'name': 'Dyson Air Purifier', 'brand': 'Dyson', 'price_range': (400, 600)},
        {'name': 'Roomba i7', 'brand': 'iRobot', 'price_range': (500, 700)},
        {'name': 'Roomba j7', 'brand': 'iRobot', 'price_range': (600, 800)},
        {'name': 'KitchenAid Mixer', 'brand': 'KitchenAid', 'price_range': (300, 500)},
        {'name': 'Instant Pot', 'brand': 'Instant Pot', 'price_range': (80, 150)},
        {'name': 'Ninja Blender', 'brand': 'Ninja', 'price_range': (80, 140)},
    ],
    'Furniture': [
        {'name': 'IKEA POÄNG Chair', 'brand': 'IKEA', 'price_range': (80, 120)},
        {'name': 'IKEA EKTORP Sofa', 'brand': 'IKEA', 'price_range': (400, 600)},
        {'name': 'Herman Miller Aeron', 'brand': 'Herman Miller', 'price_range': (1200, 1600)},
        {'name': 'Herman Miller Embody', 'brand': 'Herman Miller', 'price_range': (1400, 1800)},
        {'name': 'Steelcase Leap', 'brand': 'Steelcase', 'price_range': (900, 1300)},
        {'name': 'La-Z-Boy Recliner', 'brand': 'La-Z-Boy', 'price_range': (600, 1000)},
    ],
    'Kitchen': [
        {'name': 'Le Creuset Dutch Oven', 'brand': 'Le Creuset', 'price_range': (200, 400)},
        {'name': 'All-Clad Cookware Set', 'brand': 'All-Clad', 'price_range': (400, 700)},
        {'name': 'Cuisinart Food Processor', 'brand': 'Cuisinart', 'price_range': (100, 200)},
        {'name': 'Breville Espresso Machine', 'brand': 'Breville', 'price_range': (400, 800)},
        {'name': 'Nespresso Machine', 'brand': 'Nespresso', 'price_range': (150, 300)},
    ],
    'Decor': [
        {'name': 'Canvas Wall Art', 'brand': 'Various', 'price_range': (40, 120)},
        {'name': 'Table Lamp', 'brand': 'Various', 'price_range': (30, 80)},
        {'name': 'Floor Lamp', 'brand': 'Various', 'price_range': (60, 150)},
        {'name': 'Throw Pillows Set', 'brand': 'Various', 'price_range': (25, 60)},
        {'name': 'Area Rug 5x7', 'brand': 'Various', 'price_range': (100, 300)},
    ],
    'Tools': [
        {'name': 'DeWalt Drill Set', 'brand': 'DeWalt', 'price_range': (120, 250)},
        {'name': 'Bosch Power Tools', 'brand': 'Bosch', 'price_range': (100, 220)},
        {'name': 'Black+Decker Tool Kit', 'brand': 'Black+Decker', 'price_range': (60, 120)},
        {'name': 'Craftsman Tool Set', 'brand': 'Craftsman', 'price_range': (80, 160)},
    ],
    'Sports & Outdoors': [
        {'name': 'Trek Mountain Bike', 'brand': 'Trek', 'price_range': (600, 1200)},
        {'name': 'Specialized Road Bike', 'brand': 'Specialized', 'price_range': (800, 1500)},
        {'name': 'Cannondale Bike', 'brand': 'Cannondale', 'price_range': (700, 1300)},
        {'name': 'Wilson Tennis Racket', 'brand': 'Wilson', 'price_range': (80, 150)},
        {'name': 'Wilson Basketball', 'brand': 'Wilson', 'price_range': (25, 50)},
        {'name': 'Spalding Basketball', 'brand': 'Spalding', 'price_range': (30, 60)},
        {'name': 'Decathlon Tent', 'brand': 'Decathlon', 'price_range': (100, 250)},
        {'name': 'Coleman Camping Set', 'brand': 'Coleman', 'price_range': (80, 180)},
        {'name': 'The North Face Backpack', 'brand': 'The North Face', 'price_range': (80, 150)},
        {'name': 'Patagonia Jacket', 'brand': 'Patagonia', 'price_range': (150, 300)},
        {'name': 'Columbia Jacket', 'brand': 'Columbia', 'price_range': (100, 200)},
        {'name': 'Garmin Forerunner Watch', 'brand': 'Garmin', 'price_range': (250, 450)},
        {'name': 'Garmin Fenix Watch', 'brand': 'Garmin', 'price_range': (500, 800)},
        {'name': 'Fitbit Charge 6', 'brand': 'Fitbit', 'price_range': (130, 180)},
        {'name': 'Apple Watch SE', 'brand': 'Apple', 'price_range': (250, 350)},
        {'name': 'Apple Watch Series 9', 'brand': 'Apple', 'price_range': (400, 500)},
    ],
    'Fitness': [
        {'name': 'Bowflex Dumbbells', 'brand': 'Bowflex', 'price_range': (300, 500)},
        {'name': 'Bowflex Treadmill', 'brand': 'Bowflex', 'price_range': (800, 1400)},
        {'name': 'Peloton Bike', 'brand': 'Peloton', 'price_range': (1400, 1800)},
        {'name': 'Peloton Tread', 'brand': 'Peloton', 'price_range': (2500, 3500)},
        {'name': 'NordicTrack Treadmill', 'brand': 'NordicTrack', 'price_range': (1000, 2000)},
        {'name': 'Yoga Mat Premium', 'brand': 'Lululemon', 'price_range': (60, 100)},
        {'name': 'Resistance Bands Set', 'brand': 'Various', 'price_range': (20, 50)},
    ],
    'Camping': [
        {'name': 'REI Camping Tent', 'brand': 'REI', 'price_range': (200, 400)},
        {'name': 'MSR Backpacking Tent', 'brand': 'MSR', 'price_range': (300, 500)},
        {'name': 'Sleeping Bag', 'brand': 'Marmot', 'price_range': (100, 250)},
        {'name': 'Camping Stove', 'brand': 'Coleman', 'price_range': (50, 120)},
    ],
    'Cycling': [
        {'name': 'Giro Helmet', 'brand': 'Giro', 'price_range': (60, 150)},
        {'name': 'Shimano Pedals', 'brand': 'Shimano', 'price_range': (80, 200)},
        {'name': 'Bike Lock Heavy Duty', 'brand': 'Kryptonite', 'price_range': (50, 100)},
    ],
    'Books & Media': [
        {'name': 'Kindle Paperwhite', 'brand': 'Amazon', 'price_range': (130, 180)},
        {'name': 'Kindle Oasis', 'brand': 'Amazon', 'price_range': (250, 350)},
        {'name': 'Kobo eReader', 'brand': 'Kobo', 'price_range': (120, 200)},
        {'name': 'Best Seller Novel', 'brand': 'Various', 'price_range': (10, 25)},
        {'name': 'Hardcover Book', 'brand': 'Various', 'price_range': (20, 40)},
        {'name': '4K Blu-ray Movie', 'brand': 'Various', 'price_range': (15, 30)},
        {'name': 'DVD Movie', 'brand': 'Various', 'price_range': (8, 15)},
        {'name': 'Vinyl Record', 'brand': 'Various', 'price_range': (20, 40)},
    ],
    'Books': [
        {'name': 'Fiction Bestseller', 'brand': 'Various', 'price_range': (12, 28)},
        {'name': 'Non-Fiction Book', 'brand': 'Various', 'price_range': (15, 32)},
        {'name': 'Cookbook', 'brand': 'Various', 'price_range': (20, 45)},
        {'name': 'Children\'s Book', 'brand': 'Various', 'price_range': (8, 18)},
    ],
    'Movies': [
        {'name': '4K UHD Film', 'brand': 'Various', 'price_range': (18, 35)},
        {'name': 'Blu-ray Collection', 'brand': 'Various', 'price_range': (40, 80)},
        {'name': 'Classic Film DVD', 'brand': 'Various', 'price_range': (10, 20)},
    ],
    'Music': [
        {'name': 'Vinyl Album New', 'brand': 'Various', 'price_range': (25, 45)},
        {'name': 'Vinyl Album Classic', 'brand': 'Various', 'price_range': (20, 35)},
        {'name': 'Music Box Set', 'brand': 'Various', 'price_range': (50, 100)},
    ],
    'Toys & Games': [
        {'name': 'LEGO Star Wars Set', 'brand': 'LEGO', 'price_range': (50, 150)},
        {'name': 'LEGO Harry Potter Set', 'brand': 'LEGO', 'price_range': (60, 180)},
        {'name': 'LEGO Technic', 'brand': 'LEGO', 'price_range': (100, 300)},
        {'name': 'LEGO City Set', 'brand': 'LEGO', 'price_range': (40, 120)},
        {'name': 'Monopoly Board Game', 'brand': 'Hasbro', 'price_range': (20, 40)},
        {'name': 'Catan Board Game', 'brand': 'Catan', 'price_range': (35, 55)},
        {'name': 'Risk Board Game', 'brand': 'Hasbro', 'price_range': (30, 50)},
        {'name': 'Ticket to Ride', 'brand': 'Days of Wonder', 'price_range': (35, 55)},
        {'name': 'PlayStation 5', 'brand': 'Sony', 'price_range': (450, 550)},
        {'name': 'PlayStation 5 Digital', 'brand': 'Sony', 'price_range': (400, 500)},
        {'name': 'Xbox Series X', 'brand': 'Microsoft', 'price_range': (450, 550)},
        {'name': 'Xbox Series S', 'brand': 'Microsoft', 'price_range': (250, 350)},
        {'name': 'Nintendo Switch OLED', 'brand': 'Nintendo', 'price_range': (320, 380)},
        {'name': 'Nintendo Switch', 'brand': 'Nintendo', 'price_range': (280, 340)},
        {'name': 'Steam Deck', 'brand': 'Valve', 'price_range': (400, 600)},
    ],
    'Board Games': [
        {'name': 'Pandemic', 'brand': 'Z-Man Games', 'price_range': (30, 50)},
        {'name': 'Wingspan', 'brand': 'Stonemaier', 'price_range': (50, 70)},
        {'name': 'Azul', 'brand': 'Plan B', 'price_range': (30, 45)},
        {'name': 'Chess Set Premium', 'brand': 'Various', 'price_range': (40, 100)},
    ],
    'Video Games': [
        {'name': 'PS5 Game', 'brand': 'Various', 'price_range': (50, 70)},
        {'name': 'Xbox Game', 'brand': 'Various', 'price_range': (50, 70)},
        {'name': 'Nintendo Switch Game', 'brand': 'Various', 'price_range': (40, 60)},
        {'name': 'PC Game', 'brand': 'Various', 'price_range': (30, 60)},
    ],
    'Kids Toys': [
        {'name': 'Barbie Doll', 'brand': 'Mattel', 'price_range': (15, 40)},
        {'name': 'Hot Wheels Set', 'brand': 'Mattel', 'price_range': (20, 60)},
        {'name': 'Nerf Blaster', 'brand': 'Nerf', 'price_range': (15, 50)},
        {'name': 'Play-Doh Set', 'brand': 'Hasbro', 'price_range': (10, 30)},
    ],
    'Food & Beverages': [
        {'name': 'Lavazza Coffee Beans', 'brand': 'Lavazza', 'price_range': (8, 15)},
        {'name': 'Illy Coffee Beans', 'brand': 'Illy', 'price_range': (10, 18)},
        {'name': 'Starbucks Coffee', 'brand': 'Starbucks', 'price_range': (9, 16)},
        {'name': 'Lindt Chocolate Box', 'brand': 'Lindt', 'price_range': (12, 25)},
        {'name': 'Godiva Chocolate', 'brand': 'Godiva', 'price_range': (15, 35)},
        {'name': 'Ferrero Rocher', 'brand': 'Ferrero', 'price_range': (10, 20)},
        {'name': 'Twinings Tea Set', 'brand': 'Twinings', 'price_range': (10, 20)},
        {'name': 'Harney & Sons Tea', 'brand': 'Harney & Sons', 'price_range': (12, 25)},
    ],
    'Snacks': [
        {'name': 'Pringles Chips', 'brand': 'Pringles', 'price_range': (2, 5)},
        {'name': 'Oreo Cookies', 'brand': 'Oreo', 'price_range': (3, 6)},
        {'name': 'Snickers Bar', 'brand': 'Snickers', 'price_range': (1, 3)},
        {'name': 'Mixed Nuts', 'brand': 'Various', 'price_range': (8, 15)},
    ],
    'Drinks': [
        {'name': 'Red Bull Energy Drink', 'brand': 'Red Bull', 'price_range': (2, 4)},
        {'name': 'Coca Cola Pack', 'brand': 'Coca Cola', 'price_range': (5, 10)},
        {'name': 'Premium Water Pack', 'brand': 'Various', 'price_range': (8, 15)},
    ],
    'Organic': [
        {'name': 'Organic Quinoa', 'brand': 'Various', 'price_range': (8, 15)},
        {'name': 'Organic Honey', 'brand': 'Various', 'price_range': (10, 20)},
        {'name': 'Organic Olive Oil', 'brand': 'Various', 'price_range': (12, 25)},
    ],
    'Health & Beauty': [
        {'name': 'Chanel No. 5 Perfume', 'brand': 'Chanel', 'price_range': (90, 150)},
        {'name': 'Dior Sauvage', 'brand': 'Dior', 'price_range': (80, 130)},
        {'name': 'Tom Ford Perfume', 'brand': 'Tom Ford', 'price_range': (120, 200)},
        {'name': 'L\'Oréal Face Cream', 'brand': 'L\'Oréal', 'price_range': (15, 30)},
        {'name': 'Neutrogena Skincare', 'brand': 'Neutrogena', 'price_range': (10, 25)},
        {'name': 'CeraVe Moisturizer', 'brand': 'CeraVe', 'price_range': (12, 28)},
        {'name': 'Gillette Razor Set', 'brand': 'Gillette', 'price_range': (20, 40)},
        {'name': 'Gillette Fusion Blades', 'brand': 'Gillette', 'price_range': (25, 45)},
        {'name': 'Oral-B Electric Toothbrush', 'brand': 'Oral-B', 'price_range': (50, 100)},
        {'name': 'Philips Sonicare', 'brand': 'Philips', 'price_range': (80, 150)},
        {'name': 'Vitamins Multi Pack', 'brand': 'Various', 'price_range': (15, 35)},
        {'name': 'Protein Powder', 'brand': 'Optimum Nutrition', 'price_range': (30, 60)},
    ],
    'Cosmetics': [
        {'name': 'MAC Lipstick', 'brand': 'MAC', 'price_range': (20, 35)},
        {'name': 'MAC Foundation', 'brand': 'MAC', 'price_range': (35, 55)},
        {'name': 'Urban Decay Palette', 'brand': 'Urban Decay', 'price_range': (45, 75)},
        {'name': 'NARS Blush', 'brand': 'NARS', 'price_range': (30, 50)},
        {'name': 'Maybelline Mascara', 'brand': 'Maybelline', 'price_range': (8, 15)},
        {'name': 'NYX Makeup Set', 'brand': 'NYX', 'price_range': (15, 35)},
    ],
    'Personal Care': [
        {'name': 'Dove Body Wash', 'brand': 'Dove', 'price_range': (5, 12)},
        {'name': 'Nivea Body Lotion', 'brand': 'Nivea', 'price_range': (8, 16)},
        {'name': 'Head & Shoulders Shampoo', 'brand': 'Head & Shoulders', 'price_range': (6, 14)},
        {'name': 'Pantene Hair Care', 'brand': 'Pantene', 'price_range': (7, 15)},
    ],
    'Wellness': [
        {'name': 'Massage Gun', 'brand': 'Theragun', 'price_range': (150, 300)},
        {'name': 'Essential Oils Set', 'brand': 'Various', 'price_range': (25, 50)},
        {'name': 'Diffuser', 'brand': 'Various', 'price_range': (20, 45)},
        {'name': 'Meditation Cushion', 'brand': 'Various', 'price_range': (30, 70)},
    ]
}

products = []
product_id = 1

for category in categories:
    category_name = category['CategoryName']
    
    if category_name in realistic_products:
        product_list = realistic_products[category_name]
        max_products = len(product_list)
        min_products = min(3, max_products)
        num_products_in_cat = random.randint(min_products, max_products) if max_products > min_products else max_products
        selected_products = random.sample(product_list, num_products_in_cat)
        
        for prod_template in selected_products:
            price_min, price_max = prod_template['price_range']
            cost_price = round(random.uniform(price_min * 0.4, price_min * 0.6), 2)
            price = round(random.uniform(price_min, price_max), 2)
            
            variants = ['', '', '', 'Black', 'White', 'Blue', 'Red', 'Silver', 'Gold', 'Rose Gold', 
                       'Gray', 'Navy', 'Green', 'Purple', 'Pink', 'S', 'M', 'L', 'XL', 'XXL',
                       '128GB', '256GB', '512GB', '1TB', 'Pro', 'Plus', 'Premium', 'Standard']
            variant = random.choice(variants)
            product_name = f"{prod_template['name']} {variant}".strip()
            
            if price > 1000:
                stock = random.randint(5, 50)
            elif price > 500:
                stock = random.randint(10, 100)
            else:
                stock = random.randint(20, 200)
            
            created_at = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
            
            random_seller_id = random.choice(sellers_df['SellerID'].tolist())
            
            products.append({
                'ProductID': product_id,
                'ProductName': product_name,
                'CategoryID': category['CategoryID'],
                'SellerID': random_seller_id,
                'Price': price,
                'CostPrice': cost_price,
                'StockQuantity': stock,
                'Description': f'{prod_template["brand"]} {product_name} - High quality product',
                'CreatedAt': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': None
            })
            product_id += 1
            
            if product_id > NUM_PRODUCTS:
                break
    
    if product_id > NUM_PRODUCTS:
        break

while len(products) < NUM_PRODUCTS:
    category = random.choice(categories)
    cost_price = round(random.uniform(10, 500), 2)
    margin = random.uniform(1.2, 2.5)
    price = round(cost_price * margin, 2)
    
    random_seller_id = random.choice(sellers_df['SellerID'].tolist())
    
    products.append({
        'ProductID': product_id,
        'ProductName': f'Product {product_id} - {category["CategoryName"]}',
        'CategoryID': category['CategoryID'],
        'SellerID': random_seller_id,
        'Price': price,
        'CostPrice': cost_price,
        'StockQuantity': random.randint(0, 500),
        'Description': f'Quality product from {category["CategoryName"]} category',
        'CreatedAt': fake.date_time_between(start_date=START_DATE, end_date=END_DATE).strftime('%Y-%m-%d %H:%M:%S'),
        'UpdatedAt': None
    })
    product_id += 1

products_df = pd.DataFrame(products)
products_df['ProductID'] = range(1, len(products_df) + 1)

products_df.to_csv(os.path.join(OUTPUT_DIR, 'products.csv'), index=False)
print(f"Wygenerowano {len(products)} produktów")

print("Generowanie Customers z wzrostem w czasie...")
customers = []
customer_id = 1

for country_row in countries:
    country_id = country_row['CountryID']
    country_name = country_row['CountryName']
    market_strength = country_market_strength[country_name]
    volatility = country_volatility[country_name]
    
    base_mean = random.uniform(100, 900) * market_strength * random.uniform(0.7, 1.5)
    base_customers = int(random.gauss(base_mean, base_mean * volatility * 0.6))
    base_customers = max(40, min(base_customers, int(base_mean * 3)))
    
    for _ in range(base_customers):
        year = random.choices(years, weights=year_weights)[0]
        
        month_weights = [
            0.5, 0.6, 0.7, 0.8, 0.95, 1.0,
            1.1, 1.2, 1.3, 1.5, 1.9, 2.3
        ]
        if random.random() < 0.15:
            spike_month = random.randint(0, 11)
            month_weights[spike_month] *= random.uniform(1.5, 3.0)
        
        month = random.choices(range(1, 13), weights=month_weights)[0]
        day = random.randint(1, 28)
        created_at = datetime(year, month, day, 
                             random.randint(0, 23), 
                             random.randint(0, 59), 
                             random.randint(0, 59))
        
        locale = [loc for loc, c in locale_to_country.items() if c == country_name][0]
        fake = fakers[locale]
        
        customers.append({
            'CustomerID': customer_id,
            'FirstName': fake.first_name(),
            'LastName': fake.last_name(),
            'Email': fake.unique.email(),
            'Phone': fake.phone_number()[:20],
            'Address': fake.address().replace('\n', ', ')[:200],
            'CountryID': country_id,
            'CreatedAt': created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'UpdatedAt': None
        })
        customer_id += 1

customers_df = pd.DataFrame(customers)
customers_df['CustomerID'] = range(1, len(customers_df) + 1)
customers_df['CreatedAt_dt'] = pd.to_datetime(customers_df['CreatedAt'])

customers_df_clean = customers_df[['CustomerID', 'FirstName', 'LastName', 'Email', 'Phone', 'Address', 
                                    'CountryID', 'CreatedAt', 'UpdatedAt']].copy()
customers_df_clean.to_csv(os.path.join(OUTPUT_DIR, 'customers.csv'), index=False)
print(f"Wygenerowano {len(customers_df)} klientów (wzrost wykładniczy w czasie)")
print(f"  → Zakres: od {customers_df['CreatedAt'].min()} do {customers_df['CreatedAt'].max()}")

print("Generowanie BankAccounts...")
bank_accounts = []
account_id = 1

for seller_row in sellers_df.to_dict('records'):
    seller_id = seller_row['SellerID']
    seller_region = regions_df[regions_df['RegionID'] == seller_row['RegionID']].iloc[0]
    seller_country = countries_df[countries_df['CountryID'] == seller_region['CountryID']].iloc[0]
    country_name = seller_country['CountryName']
    
    locale = [loc for loc, country in locale_to_country.items() if country == country_name][0]
    fake = fakers[locale]
    
    currency = country_currencies[country_name]
    
    balance = round(random.uniform(1000, 100000), 2)
    bank_names = ['Standard Bank', 'National Bank', 'Commercial Bank', 'Trust Bank', 'First Bank']
    
    bank_accounts.append({
        'AccountID': account_id,
        'AccountNumber': fake.iban(),
        'BankName': random.choice(bank_names),
        'Currency': currency,
        'Balance': balance,
        'AccountType': random.choice(['business', 'personal']),
        'SellerID': seller_id,
        'CreatedAt': seller_row['CreatedAt'],
        'UpdatedAt': None
    })
    account_id += 1
    
    if random.random() < 0.3:
        balance = round(random.uniform(500, 50000), 2)
        bank_accounts.append({
            'AccountID': account_id,
            'AccountNumber': fake.iban(),
            'BankName': random.choice(bank_names),
            'Currency': currency,
            'Balance': balance,
            'AccountType': 'savings',
            'SellerID': seller_id,
            'CreatedAt': seller_row['CreatedAt'],
            'UpdatedAt': None
        })
        account_id += 1

bank_accounts_df = pd.DataFrame(bank_accounts)
bank_accounts_df['AccountID'] = range(1, len(bank_accounts_df) + 1)

bank_accounts_df.to_csv(os.path.join(OUTPUT_DIR, 'bank_accounts.csv'), index=False)
print(f"Wygenerowano {len(bank_accounts)} kont bankowych dla {len(sellers_df)} sprzedawców")

print("Generowanie Orders z wzrostem organicznym...")

def get_seasonal_multiplier(month):
    seasonal_factors = {
        1: 0.8,
        2: 0.9,
        3: 1.0,
        4: 1.1,
        5: 1.2,
        6: 1.3,
        7: 1.4,
        8: 1.3,
        9: 1.1,
        10: 1.2,
        11: 1.6,
        12: 2.0
    }
    return seasonal_factors.get(month, 1.0)

def get_realistic_order_hour():
    hour_weights = [
        0.5, 0.3, 0.2, 0.2, 0.3, 0.5,
        1.0, 2.0, 3.0, 3.5, 4.0, 4.5,
        5.0, 4.5, 4.0, 4.5, 5.5, 7.0,
        8.5, 9.0, 8.0, 6.0, 4.0, 2.0
    ]
    return random.choices(range(24), weights=hour_weights, k=1)[0]

customer_profiles = {}
for customer_row in customers_df.to_dict('records'):
    customer_profiles[customer_row['CustomerID']] = {
        'purchase_frequency': random.choice(['rare', 'occasional', 'frequent', 'vip']),
        'avg_order_value': random.choice(['low', 'medium', 'high']),
        'preferred_categories': random.sample(categories, random.randint(1, 3))
    }

orders = []
order_details = []
order_detail_id = 1
order_id = 1

print("Generowanie zamówień z uwzględnieniem wzrostu platformy...")

for year in range(START_DATE.year, END_DATE.year + 1):
    year_index = year - START_DATE.year
    global_year_growth_factor = 0.2 + (year_index / len(years)) ** 1.9 * 6.0
    
    for month in range(1, 13):
        if year == END_DATE.year and month > END_DATE.month:
            break
        
        base_seasonal = get_seasonal_multiplier(month)
        seasonal = base_seasonal * random.uniform(0.8, 1.2)
        
        if random.random() < 0.02:
            seasonal *= random.uniform(2.0, 4.0)
        
        for country_row in countries:
            country_id = country_row['CountryID']
            country_name = country_row['CountryName']
            market_strength = country_market_strength[country_name]
            growth_rate = country_growth_rate[country_name]
            volatility = country_volatility[country_name]
            
            country_year_growth = global_year_growth_factor * growth_rate
            
            base_mean = (
                random.uniform(10, 50) *
                market_strength *
                country_year_growth *
                seasonal *
                random.uniform(0.7, 1.4)
            )
            
            std_dev = base_mean * volatility * 0.6
            base_orders_month = int(random.gauss(base_mean, std_dev))
            base_orders_month = max(1, min(base_orders_month, int(base_mean * 3.5)))
            
            country_customers = customers_df[
                (customers_df['CountryID'] == country_id) &
                (customers_df['CreatedAt_dt'] <= datetime(year, month, 28))
            ]
            
            if len(country_customers) == 0:
                continue
            
            for _ in range(base_orders_month):
                customer_row = country_customers.sample(1).iloc[0]
                customer = customer_row.to_dict()
                profile = customer_profiles[customer['CustomerID']]
                
                if profile['purchase_frequency'] == 'rare' and random.random() < 0.85:
                    continue
                elif profile['purchase_frequency'] == 'occasional' and random.random() < 0.5:
                    continue
                
                customer_country = customer['CountryID']
                if random.random() < 0.7:
                    customer_region = regions_df[regions_df['CountryID'] == customer_country]
                    if len(customer_region) > 0:
                        region = customer_region.sample(1).iloc[0]
                        regional_sellers = sellers_df[
                            (sellers_df['RegionID'] == region['RegionID']) &
                            (sellers_df['HireDate_dt'] <= datetime(year, month, 1))
                        ]
                        if len(regional_sellers) > 0:
                            seller_row = regional_sellers.sample(1).iloc[0]
                        else:
                            active_sellers = sellers_df[
                                sellers_df['HireDate_dt'] <= datetime(year, month, 1)
                            ]
                            if len(active_sellers) == 0:
                                continue
                            seller_row = active_sellers.sample(1).iloc[0]
                    else:
                        active_sellers = sellers_df[
                            sellers_df['HireDate_dt'] <= datetime(year, month, 1)
                        ]
                        if len(active_sellers) == 0:
                            continue
                        seller_row = active_sellers.sample(1).iloc[0]
                else:
                    active_sellers = sellers_df[
                        sellers_df['HireDate_dt'] <= datetime(year, month, 1)
                    ]
                    if len(active_sellers) == 0:
                        continue
                    seller_row = active_sellers.sample(1).iloc[0]
                
                seller = seller_row.to_dict()
                
                day = random.randint(1, 28)
                hour = get_realistic_order_hour()
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                order_date = datetime(year, month, day, hour, minute, second)
                
                date_str = order_date.strftime('%Y-%m-%d')
                date_rows = dates_df[dates_df['FullDate'] == date_str]
                if len(date_rows) == 0:
                    continue
                date_id = date_rows.iloc[0]['DateID']
                
                status = random.choices(
                    ['completed', 'pending', 'cancelled', 'shipped'],
                    weights=[0.75, 0.08, 0.05, 0.12]
                )[0]
                
                payment_method = random.choices(
                    ['credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash_on_delivery'],
                    weights=[0.40, 0.30, 0.15, 0.10, 0.05]
                )[0]
                
                shipping_country_id = customer['CountryID']
                
                if profile['avg_order_value'] == 'low':
                    num_items = random.choices([1, 2], weights=[0.7, 0.3])[0]
                elif profile['avg_order_value'] == 'medium':
                    num_items = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
                else:
                    num_items = random.choices([2, 3, 4, 5], weights=[0.3, 0.4, 0.2, 0.1])[0]
                
                preferred_cat_ids = [cat['CategoryID'] for cat in profile['preferred_categories']]
                available_products = products_df[products_df['CategoryID'].isin(preferred_cat_ids)]
                
                if len(available_products) < num_items:
                    available_products = products_df
                
                if len(available_products) == 0:
                    continue
                
                order_products = available_products.sample(min(num_items, len(available_products))).to_dict('records')
                
                total_amount = 0
                for product in order_products:
                    quantity = random.choices([1, 2, 3, 4, 5], weights=[0.70, 0.15, 0.08, 0.05, 0.02])[0]
                    unit_price = product['Price']
                    unit_cost = product['CostPrice']
                    
                    discount = random.choices([0, 5, 10, 15, 20, 25], weights=[0.70, 0.10, 0.08, 0.06, 0.04, 0.02])[0]
                    
                    line_total = quantity * unit_price * (1 - discount / 100)
                    total_amount += line_total
                    
                    order_details.append({
                        'OrderDetailID': order_detail_id,
                        'OrderID': order_id,
                        'ProductID': product['ProductID'],
                        'Quantity': quantity,
                        'UnitPrice': unit_price,
                        'UnitCostPrice': unit_cost,
                        'Discount': discount
                    })
                    order_detail_id += 1
                
                orders.append({
                    'OrderID': order_id,
                    'CustomerID': customer['CustomerID'],
                    'SellerID': seller['SellerID'],
                    'OrderDate': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'DateID': date_id,
                    'TotalAmount': round(total_amount, 2),
                    'Status': status,
                    'ShippingAddress': customer['Address'],
                    'CountryID': shipping_country_id,
                    'PaymentMethod': payment_method,
                    'CreatedAt': order_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                
                customer_purchase_history[customer['CustomerID']].append(order_id)
                
                order_id += 1
    
    print(f"  Rok {year}: wygenerowano {len([o for o in orders if o['OrderDate'].startswith(str(year))])} zamówień")

orders_df = pd.DataFrame(orders)
orders_df.to_csv(os.path.join(OUTPUT_DIR, 'orders.csv'), index=False)
print(f"Wygenerowano {len(orders)} zamówień")

order_details_df = pd.DataFrame(order_details)
order_details_df.to_csv(os.path.join(OUTPUT_DIR, 'order_details.csv'), index=False)
print(f"Wygenerowano {len(order_details)} szczegółów zamówień")

print("Generowanie BankTransactions...")
bank_transactions = []
transaction_id = 1

for order in orders:
    if order['Status'] == 'completed':
        transaction_date = datetime.strptime(order['OrderDate'], '%Y-%m-%d %H:%M:%S')
        date_str = transaction_date.strftime('%Y-%m-%d')
        date_row = dates_df[dates_df['FullDate'] == date_str].iloc[0]
        
        seller_accounts = bank_accounts_df[bank_accounts_df['SellerID'] == order['SellerID']]
        if len(seller_accounts) > 0:
            account = seller_accounts.iloc[0]
            
            bank_transactions.append({
                'TransactionID': transaction_id,
                'AccountID': account['AccountID'],
                'TransactionDate': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                'DateID': date_row['DateID'],
                'Amount': order['TotalAmount'],
                'TransactionType': 'credit',
                'Description': f'Payment for Order #{order["OrderID"]}',
                'Counterparty': f'Customer #{order["CustomerID"]}',
                'ReferenceNumber': f'ORD-{order["OrderID"]}-{transaction_id}',
                'SellerID': order['SellerID']
            })
            transaction_id += 1

num_extra_transactions = 500
for i in range(num_extra_transactions):
    account = random.choice(bank_accounts)
    transaction_date = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
    date_str = transaction_date.strftime('%Y-%m-%d')
    date_row = dates_df[dates_df['FullDate'] == date_str].iloc[0]
    
    transaction_type = random.choice(['debit', 'credit', 'fee', 'withdrawal'])
    amount = round(random.uniform(10, 5000), 2)
    
    descriptions = {
        'debit': ['Purchase supplies', 'Pay vendor', 'Business expense', 'Equipment purchase'],
        'credit': ['Payment received', 'Refund received', 'Investment return'],
        'fee': ['Account maintenance fee', 'Transaction fee', 'Service charge'],
        'withdrawal': ['Cash withdrawal', 'ATM withdrawal', 'Bank withdrawal']
    }
    
    bank_transactions.append({
        'TransactionID': transaction_id,
        'AccountID': account['AccountID'],
        'TransactionDate': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
        'DateID': date_row['DateID'],
        'Amount': amount,
        'TransactionType': transaction_type,
        'Description': random.choice(descriptions[transaction_type]),
        'Counterparty': fake.company() if random.random() > 0.5 else fake.name(),
        'ReferenceNumber': f'TXN-{transaction_id}-{random.randint(1000, 9999)}',
        'SellerID': account['SellerID']
    })
    transaction_id += 1

bank_transactions_df = pd.DataFrame(bank_transactions)
bank_transactions_df.to_csv(os.path.join(OUTPUT_DIR, 'bank_transactions.csv'), index=False)
print(f"Wygenerowano {len(bank_transactions)} transakcji bankowych")

print("Generowanie Promotions...")
promotions = []

for i in range(1, NUM_PROMOTIONS + 1):
    start_date = fake.date_between(start_date=START_DATE, end_date=END_DATE - timedelta(days=30))
    start_date_str = start_date.strftime('%Y-%m-%d')
    start_date_row = dates_df[dates_df['FullDate'] == start_date_str].iloc[0]
    
    duration = random.randint(7, 30)
    end_date = start_date + timedelta(days=duration)
    end_date_str = end_date.strftime('%Y-%m-%d')
    end_date_row = dates_df[dates_df['FullDate'] == end_date_str].iloc[0]
    
    discount = random.choice([5, 10, 15, 20, 25, 30, 40, 50])
    
    promo_type = random.choice(['product', 'category'])
    product_id = None
    category_id = None
    
    if promo_type == 'product':
        product = random.choice(products)
        product_id = product['ProductID']
        promo_name = f"{discount}% off {product['ProductName']}"
    else:
        category = random.choice(categories)
        category_id = category['CategoryID']
        promo_name = f"{discount}% off {category['CategoryName']}"
    
    promotions.append({
        'PromotionID': i,
        'PromotionName': promo_name,
        'StartDateID': start_date_row['DateID'],
        'EndDateID': end_date_row['DateID'],
        'DiscountPercentage': discount,
        'ProductID': product_id,
        'CategoryID': category_id,
        'SellerID': random.choice(sellers)['SellerID']
    })

promotions_df = pd.DataFrame(promotions)
promotions_df.to_csv(os.path.join(OUTPUT_DIR, 'promotions.csv'), index=False)
print(f"Wygenerowano {len(promotions)} promocji")

print("\n" + "="*70)
print("ROZPOCZYNAM WALIDACJĘ I CZYSZCZENIE WYGENEROWANYCH DANYCH")
print("="*70)

print("\n[1/10] Walidacja Countries...")
countries_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'countries.csv'))
countries_df = validator.remove_duplicates(countries_df)
countries_df.to_csv(os.path.join(OUTPUT_DIR, 'countries.csv'), index=False)

print("[2/10] Walidacja Regions...")
regions_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'regions.csv'))
regions_df = validator.remove_duplicates(regions_df, subset=['RegionName', 'CountryID'])
regions_df = validator.sanitize_dataframe(regions_df, text_columns=['RegionName'])
regions_df.to_csv(os.path.join(OUTPUT_DIR, 'regions.csv'), index=False)

print("[3/10] Walidacja Categories...")
categories_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'categories.csv'))
categories_df = validator.remove_duplicates(categories_df)
categories_df = validator.sanitize_dataframe(categories_df, text_columns=['CategoryName', 'Description'])
categories_df.to_csv(os.path.join(OUTPUT_DIR, 'categories.csv'), index=False)

print("[4/10] Walidacja Sellers...")
sellers_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'sellers.csv'))
sellers_df = validator.remove_duplicates(sellers_df, subset=['Email'])
sellers_df, invalid_emails = validator.validate_dataframe_emails(sellers_df, 'Email')
sellers_df, invalid_phones = validator.validate_dataframe_phones(sellers_df, 'Phone')
sellers_df = validator.sanitize_dataframe(sellers_df, text_columns=['FirstName', 'LastName'])
sellers_df.to_csv(os.path.join(OUTPUT_DIR, 'sellers.csv'), index=False)

print("[5/10] Walidacja Products...")
products_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'products.csv'))
products_df = validator.remove_duplicates(products_df, subset=['ProductName', 'SellerID'])
products_df = validator.sanitize_dataframe(products_df, text_columns=['ProductName', 'Description'])
outliers_price = validator.detect_outliers_iqr(products_df, 'Price', multiplier=2.0)
outliers_stock = validator.detect_outliers_iqr(products_df, 'StockQuantity', multiplier=2.0)
products_df.to_csv(os.path.join(OUTPUT_DIR, 'products.csv'), index=False)

print("[6/10] Walidacja Customers...")
customers_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'customers.csv'))
customers_df = validator.remove_duplicates(customers_df, subset=['Email'])
customers_df, invalid_emails = validator.validate_dataframe_emails(customers_df, 'Email')
customers_df, invalid_phones = validator.validate_dataframe_phones(customers_df, 'Phone')
customers_df = validator.sanitize_dataframe(customers_df, text_columns=['FirstName', 'LastName', 'Address'])
customers_df.to_csv(os.path.join(OUTPUT_DIR, 'customers.csv'), index=False)

print("[7/10] Walidacja BankAccounts...")
bank_accounts_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'bank_accounts.csv'))
bank_accounts_df = validator.remove_duplicates(bank_accounts_df, subset=['AccountNumber'])
bank_accounts_df = validator.sanitize_dataframe(bank_accounts_df, text_columns=['BankName'])
outliers_balance = validator.detect_outliers_iqr(bank_accounts_df, 'Balance', multiplier=2.0)
bank_accounts_df.to_csv(os.path.join(OUTPUT_DIR, 'bank_accounts.csv'), index=False)

print("[8/10] Walidacja Orders i OrderDetails...")
orders_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'orders.csv'))
orders_df = validator.remove_duplicates(orders_df)
outliers_total = validator.detect_outliers_iqr(orders_df, 'TotalAmount', multiplier=2.0)
orders_df.to_csv(os.path.join(OUTPUT_DIR, 'orders.csv'), index=False)

order_details_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'order_details.csv'))
order_details_df = validator.remove_duplicates(order_details_df, subset=['OrderID', 'ProductID'])
outliers_qty = validator.detect_outliers_iqr(order_details_df, 'Quantity', multiplier=2.0)
order_details_df.to_csv(os.path.join(OUTPUT_DIR, 'order_details.csv'), index=False)

print("[9/10] Walidacja BankTransactions...")
bank_transactions_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'bank_transactions.csv'))
bank_transactions_df = validator.remove_duplicates(bank_transactions_df, subset=['ReferenceNumber'])
bank_transactions_df = validator.sanitize_dataframe(bank_transactions_df, text_columns=['Description', 'Counterparty'])
outliers_amount = validator.detect_outliers_iqr(bank_transactions_df, 'Amount', multiplier=2.5)
bank_transactions_df.to_csv(os.path.join(OUTPUT_DIR, 'bank_transactions.csv'), index=False)

print("[10/10] Walidacja Promotions...")
promotions_df = pd.read_csv(os.path.join(OUTPUT_DIR, 'promotions.csv'))
promotions_df = validator.remove_duplicates(promotions_df)
promotions_df = validator.sanitize_dataframe(promotions_df, text_columns=['PromotionName'])
promotions_df.to_csv(os.path.join(OUTPUT_DIR, 'promotions.csv'), index=False)

print("\n" + "="*70)
print("RAPORT WALIDACJI I CZYSZCZENIA DANYCH")
print("="*70)
validation_summary = validator.validation_report
print(f"[OK] Usuniete duplikaty:        {validation_summary['duplicates_removed']}")
print(f"[OK] Uzupelnione wartosci:       {validation_summary['missing_values_imputed']}")
print(f"[WARN] Niepoprawne emaile:         {validation_summary['invalid_emails']}")
print(f"[WARN] Niepoprawne telefony:       {validation_summary['invalid_phones']}")
print(f"Wykryte outliers:           {validation_summary['outliers_detected']}")
print("="*70)

print("\n" + "="*60)
print("PODSUMOWANIE WYGENEROWANYCH DANYCH")
print("="*60)
print(f"Katalog: {OUTPUT_DIR}/")
print(f"Countries: {len(countries)} rekordów")
print(f"DateDimension: {len(dates)} rekordów")
print(f"Regions: {len(regions)} rekordów")
print(f"Categories: {len(categories)} rekordów")
print(f"Sellers: {len(sellers)} rekordów")
print(f"Products: {len(products)} rekordów")
print(f"Customers: {len(customers)} rekordów")
print(f"BankAccounts: {len(bank_accounts)} rekordów")
print(f"Orders: {len(orders)} rekordów")
print(f"OrderDetails: {len(order_details)} rekordów")
print(f"BankTransactions: {len(bank_transactions)} rekordów")
print(f"Promotions: {len(promotions)} rekordów")
print("="*60)
print("Generowanie zakończone pomyślnie!")
print("="*60)

print("\nWszystkie dane zostały pomyślnie wygenerowane!")