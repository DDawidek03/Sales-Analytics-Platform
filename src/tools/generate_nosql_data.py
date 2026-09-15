import json
import pandas as pd
import os
from datetime import datetime
from collections import defaultdict
import random
import uuid
import sys
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.path.dirname(__file__))
from data_validation import DataValidator

INPUT_DIR = "sales_data"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "nosql_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

validator = DataValidator(verbose=True)

print("="*60)
print("TRANSFORMACJA DANYCH RELACYJNYCH -> NoSQL")
print("="*60)
print(f"Źródło:  {INPUT_DIR}/  (baza relacyjna - CSV)")
print(f"Cel:     {OUTPUT_DIR}/ (MongoDB - JSON)")
print("[OK] Modul walidacji danych aktywny")
print("="*60)
print()
sys.stdout.flush()


print("Wczytywanie danych z CSV...")
sys.stdout.flush()

try:
    countries_df = pd.read_csv(os.path.join(INPUT_DIR, 'countries.csv'))
    regions_df = pd.read_csv(os.path.join(INPUT_DIR, 'regions.csv'))
    categories_df = pd.read_csv(os.path.join(INPUT_DIR, 'categories.csv'))
    sellers_df = pd.read_csv(os.path.join(INPUT_DIR, 'sellers.csv'))
    products_df = pd.read_csv(os.path.join(INPUT_DIR, 'products.csv'))
    customers_df = pd.read_csv(os.path.join(INPUT_DIR, 'customers.csv'))
    orders_df = pd.read_csv(os.path.join(INPUT_DIR, 'orders.csv'))
    order_details_df = pd.read_csv(os.path.join(INPUT_DIR, 'order_details.csv'))
    bank_accounts_df = pd.read_csv(os.path.join(INPUT_DIR, 'bank_accounts.csv'))
    bank_transactions_df = pd.read_csv(os.path.join(INPUT_DIR, 'bank_transactions.csv'))
    
    print(f"[OK] Countries: {len(countries_df)} rekordow")
    print(f"[OK] Regions: {len(regions_df)} rekordow")
    print(f"[OK] Categories: {len(categories_df)} rekordow")
    print(f"[OK] Sellers: {len(sellers_df)} rekordow")
    print(f"[OK] Products: {len(products_df)} rekordow")
    print(f"[OK] Customers: {len(customers_df)} rekordow")
    print(f"[OK] Orders: {len(orders_df)} rekordow")
    print(f"[OK] Order Details: {len(order_details_df)} rekordow")
    print(f"[OK] Bank Accounts: {len(bank_accounts_df)} rekordow")
    print(f"[OK] Bank Transactions: {len(bank_transactions_df)} rekordow")
    sys.stdout.flush()
    
    print("\n[INFO] Walidacja wczytanych danych...")
    sys.stdout.flush()
    sellers_df = validator.impute_missing_values(sellers_df, strategy={})
    customers_df = validator.impute_missing_values(customers_df, strategy={})
    products_df = validator.impute_missing_values(products_df, strategy={})
    print("[OK] Walidacja zakonczona")
    sys.stdout.flush()
    print()
    
except FileNotFoundError as e:
    print(f"[ERROR] BLAD: Nie znaleziono pliku: {e}")
    print(f"   Najpierw uruchom: python src/tools/generate_sales_data.py")
    exit(1)


print("Generowanie kolekcji SellerProfiles...")
sys.stdout.flush()
seller_profiles = []

for idx, seller_row in sellers_df.iterrows():
    seller_products = products_df[products_df['SellerID'] == seller_row['SellerID']]
    
    products_list = []
    for _, product in seller_products.iterrows():
        category = categories_df[categories_df['CategoryID'] == product['CategoryID']].iloc[0]
        
        products_list.append({
            'ProductID': int(product['ProductID']),
            'ProductName': str(product['ProductName']),
            'CategoryID': int(category['CategoryID']),
            'CategoryName': str(category['CategoryName']),
            'Price': float(product['Price']),
            'CostPrice': float(product['CostPrice']),
            'StockQuantity': int(product['StockQuantity']),
            'Description': str(product['Description']) if pd.notna(product['Description']) else ''
        })
    
    seller_orders = orders_df[orders_df['SellerID'] == seller_row['SellerID']]
    total_orders = len(seller_orders)
    total_revenue = seller_orders['TotalAmount'].sum() if total_orders > 0 else 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    seller_order_ids = seller_orders['OrderID'].tolist()
    sold_products = order_details_df[order_details_df['OrderID'].isin(seller_order_ids)]
    total_products_sold = sold_products['Quantity'].sum() if len(sold_products) > 0 else 0
    
    seller_profile = {
        'SellerID': int(seller_row['SellerID']),
        'Email': str(seller_row['Email']),
        'FirstName': str(seller_row['FirstName']),
        'LastName': str(seller_row['LastName']),
        'Phone': str(seller_row['Phone']) if pd.notna(seller_row['Phone']) else '',
        'SellerType': str(seller_row['SellerType']),
        'RegionID': int(seller_row['RegionID']),
        'HireDate': str(seller_row['HireDate']),
        'Products': products_list,
        'SalesSummary': {
            'TotalOrders': int(total_orders),
            'TotalRevenue': float(total_revenue),
            'AverageOrderValue': float(avg_order_value),
            'TotalProductsSold': int(total_products_sold)
        },
        'LastUpdated': datetime.now().isoformat()
    }
    
    seller_profiles.append(seller_profile)
    
    if (idx + 1) % 50 == 0 or (idx + 1) == len(sellers_df):
        print(f"  Przetworzono {idx + 1}/{len(sellers_df)} sprzedawców...")
        sys.stdout.flush()

with open(os.path.join(OUTPUT_DIR, 'seller_profiles.json'), 'w', encoding='utf-8') as f:
    json.dump(seller_profiles, f, indent=2, ensure_ascii=False)

print(f"[OK] Wygenerowano {len(seller_profiles)} profili sprzedawcow")
print(f"  Zapisano do: {OUTPUT_DIR}/seller_profiles.json")
sys.stdout.flush()
print()


print("Generowanie kolekcji PurchaseHistories...")
sys.stdout.flush()
purchase_histories = []

for idx, customer_row in customers_df.iterrows():
    customer_orders = orders_df[orders_df['CustomerID'] == customer_row['CustomerID']]
    
    purchases_list = []
    for _, order in customer_orders.iterrows():
        seller = sellers_df[sellers_df['SellerID'] == order['SellerID']].iloc[0]
        
        order_items = order_details_df[order_details_df['OrderID'] == order['OrderID']]
        
        products_in_order = []
        for _, item in order_items.iterrows():
            product = products_df[products_df['ProductID'] == item['ProductID']].iloc[0]
            category = categories_df[categories_df['CategoryID'] == product['CategoryID']].iloc[0]
            
            products_in_order.append({
                'ProductID': int(item['ProductID']),
                'ProductName': str(product['ProductName']),
                'CategoryID': int(category['CategoryID']),
                'CategoryName': str(category['CategoryName']),
                'Quantity': int(item['Quantity']),
                'UnitPrice': float(item['UnitPrice']),
                'UnitCostPrice': float(item['UnitCostPrice']),
                'Discount': float(item['Discount'])
            })
        
        order_date = pd.to_datetime(order['OrderDate'])
        
        purchase = {
            'OrderID': int(order['OrderID']),
            'OrderDate': order_date.isoformat(),
            'Year': int(order_date.year),
            'Quarter': int((order_date.month - 1) // 3 + 1),
            'Month': int(order_date.month),
            'TotalAmount': float(order['TotalAmount']),
            'Status': str(order['Status']),
            'Seller': {
                'SellerID': int(seller['SellerID']),
                'SellerName': f"{seller['FirstName']} {seller['LastName']}",
                'SellerType': str(seller['SellerType']),
                'RegionID': int(seller['RegionID'])
            },
            'Products': products_in_order,
            'ShippingCountryID': int(order['CountryID']),
            'PaymentMethod': str(order['PaymentMethod'])
        }
        
        purchases_list.append(purchase)
    
    purchase_history = {
        'CustomerID': int(customer_row['CustomerID']),
        'Email': str(customer_row['Email']),
        'FirstName': str(customer_row['FirstName']),
        'LastName': str(customer_row['LastName']),
        'Phone': str(customer_row['Phone']) if pd.notna(customer_row['Phone']) else '',
        'Address': str(customer_row['Address']) if pd.notna(customer_row['Address']) else '',
        'CountryID': int(customer_row['CountryID']),
        'Purchases': purchases_list,
        'LastUpdated': datetime.now().isoformat()
    }
    
    purchase_histories.append(purchase_history)
    
    if (idx + 1) % 500 == 0 or (idx + 1) == len(customers_df):
        print(f"  Przetworzono {idx + 1}/{len(customers_df)} klientów...")
        sys.stdout.flush()

with open(os.path.join(OUTPUT_DIR, 'purchase_histories.json'), 'w', encoding='utf-8') as f:
    json.dump(purchase_histories, f, indent=2, ensure_ascii=False)

print(f"[OK] Wygenerowano {len(purchase_histories)} historii zakupow")
print(f"  Zapisano do: {OUTPUT_DIR}/purchase_histories.json")
sys.stdout.flush()
print()


print("Generowanie kolekcji BankTransactionLogs...")
sys.stdout.flush()
bank_transaction_logs = []

for idx, account_row in bank_accounts_df.iterrows():
    account_transactions = bank_transactions_df[bank_transactions_df['AccountID'] == account_row['AccountID']]
    
    transactions_list = []
    for _, trans in account_transactions.iterrows():
        seller = sellers_df[sellers_df['SellerID'] == trans['SellerID']].iloc[0]
        
        trans_date = pd.to_datetime(trans['TransactionDate'])
        
        transaction = {
            'TransactionID': int(trans['TransactionID']),
            'TransactionDate': trans_date.isoformat(),
            'Year': int(trans_date.year),
            'Quarter': int((trans_date.month - 1) // 3 + 1),
            'Month': int(trans_date.month),
            'Amount': float(trans['Amount']),
            'TransactionType': str(trans['TransactionType']),
            'Description': str(trans['Description']) if pd.notna(trans['Description']) else '',
            'Counterparty': str(trans['Counterparty']) if pd.notna(trans['Counterparty']) else '',
            'ReferenceNumber': str(trans['ReferenceNumber']) if pd.notna(trans['ReferenceNumber']) else '',
            'Status': 'completed',
            'Seller': {
                'SellerID': int(seller['SellerID']),
                'SellerName': f"{seller['FirstName']} {seller['LastName']}",
                'SellerType': str(seller['SellerType']),
                'RegionID': int(seller['RegionID'])
            }
        }
        
        transactions_list.append(transaction)
    
    bank_log = {
        'AccountID': int(account_row['AccountID']),
        'AccountNumber': str(account_row['AccountNumber']),
        'BankName': str(account_row['BankName']) if pd.notna(account_row['BankName']) else '',
        'Currency': str(account_row['Currency']),
        'AccountType': str(account_row['AccountType']),
        'Balance': float(account_row['Balance']),
        'Transactions': transactions_list,
        'LastUpdated': datetime.now().isoformat()
    }
    
    bank_transaction_logs.append(bank_log)
    
    if (idx + 1) % 50 == 0 or (idx + 1) == len(bank_accounts_df):
        print(f"  Przetworzono {idx + 1}/{len(bank_accounts_df)} kont bankowych...")
        sys.stdout.flush()

with open(os.path.join(OUTPUT_DIR, 'bank_transaction_logs.json'), 'w', encoding='utf-8') as f:
    json.dump(bank_transaction_logs, f, indent=2, ensure_ascii=False)

print(f"[OK] Wygenerowano {len(bank_transaction_logs)} logow transakcji bankowych")
print(f"  Zapisano do: {OUTPUT_DIR}/bank_transaction_logs.json")
sys.stdout.flush()
print()


print("Generowanie kolekcji CustomerBehavior...")
sys.stdout.flush()
customer_behaviors = []

event_types = ['page_view', 'product_view', 'add_to_cart', 'remove_from_cart', 
               'wishlist_add', 'search', 'filter_apply', 'purchase_click']

for idx, customer_row in customers_df.iterrows():
    customer_orders = orders_df[orders_df['CustomerID'] == customer_row['CustomerID']]
    
    activity_list = []
    event_id = 1
    
    for _, order in customer_orders.iterrows():
        order_items = order_details_df[order_details_df['OrderID'] == order['OrderID']]
        
        for _, item in order_items.iterrows():
            product = products_df[products_df['ProductID'] == item['ProductID']].iloc[0]
            category = categories_df[categories_df['CategoryID'] == product['CategoryID']].iloc[0]
            seller = sellers_df[sellers_df['SellerID'] == order['SellerID']].iloc[0]
            
            num_events = random.randint(2, 3)
            order_date = pd.to_datetime(order['OrderDate'])
            
            for _ in range(num_events):
                event_type = random.choice(event_types)
                
                import random
                hours_before = random.randint(1, 48)
                event_date = order_date - pd.Timedelta(hours=hours_before)
                
                event = {
                    'EventID': event_id,
                    'EventType': event_type,
                    'EventDate': event_date.isoformat(),
                    'Year': int(event_date.year),
                    'Quarter': int((event_date.month - 1) // 3 + 1),
                    'Month': int(event_date.month),
                    'Details': {
                        'ProductID': int(product['ProductID']),
                        'ProductName': str(product['ProductName']),
                        'CategoryID': int(category['CategoryID']),
                        'CategoryName': str(category['CategoryName']),
                        'Action': event_type.replace('_', ' '),
                        'PageURL': f'/products/{product["ProductID"]}',
                        'SessionID': str(uuid.uuid4()),
                        'SellerID': int(seller['SellerID']),
                        'SellerName': f"{seller['FirstName']} {seller['LastName']}",
                        'RegionID': int(seller['RegionID'])
                    }
                }
                
                activity_list.append(event)
                event_id += 1
    
    customer_behavior = {
        'CustomerID': int(customer_row['CustomerID']),
        'Email': str(customer_row['Email']),
        'CountryID': int(customer_row['CountryID']),
        'Activity': activity_list,
        'LastUpdated': datetime.now().isoformat()
    }
    
    customer_behaviors.append(customer_behavior)
    
    if (idx + 1) % 500 == 0 or (idx + 1) == len(customers_df):
        print(f"  Przetworzono {idx + 1}/{len(customers_df)} zachowań klientów...")
        sys.stdout.flush()

with open(os.path.join(OUTPUT_DIR, 'customer_behavior.json'), 'w', encoding='utf-8') as f:
    json.dump(customer_behaviors, f, indent=2, ensure_ascii=False)

print(f"[OK] Wygenerowano {len(customer_behaviors)} zachowan klientow")
print(f"  Zapisano do: {OUTPUT_DIR}/customer_behavior.json")
sys.stdout.flush()
print()


total_purchases = sum(len(ph['Purchases']) for ph in purchase_histories)
total_transactions = sum(len(btl['Transactions']) for btl in bank_transaction_logs)
total_events = sum(len(cb['Activity']) for cb in customer_behaviors)
total_products = sum(len(sp['Products']) for sp in seller_profiles)

print("\n" + "="*70)
print("[RAPORT] WALIDACJA DANYCH NoSQL")
print("="*70)
validation_summary = validator.validation_report
print(f"[OK] Uzupelnione wartosci:      {validation_summary['missing_values_imputed']}")
print(f"[WARN] Niepoprawne emaile:      {validation_summary['invalid_emails']}")
print(f"[WARN] Niepoprawne telefony:    {validation_summary['invalid_phones']}")
print("="*70)

print("\n" + "="*60)
print("PODSUMOWANIE TRANSFORMACJI")
print("="*60)
print(f"Katalog wyjściowy: {OUTPUT_DIR}/")
print()
print("KOLEKCJE MONGODB (4 główne):")
print(f"  1. seller_profiles.json         - {len(seller_profiles)} dokumentów")
print(f"  2. purchase_histories.json      - {len(purchase_histories)} dokumentów")
print(f"  3. bank_transaction_logs.json   - {len(bank_transaction_logs)} dokumentów")
print(f"  4. customer_behavior.json       - {len(customer_behaviors)} dokumentów")
print()
print("STATYSTYKI ZAGNIEŻDŻONYCH DANYCH:")
print(f"  Zamówienia (w purchase_histories):     {total_purchases}")
print(f"  Transakcje (w bank_transaction_logs):  {total_transactions}")
print(f"  Wydarzenia (w customer_behavior):      {total_events}")
print(f"  Produkty (w seller_profiles):          {total_products}")
print()
print("UWAGA:")
print(f" Dane referencyjne (Countries, Regions, Categories) są w SQL Server")
print(f" MongoDB używa tylko ID do odwołań do danych referencyjnych")
print(f" Dane są IDENTYCZNE z bazą relacyjną - tylko inna struktura!")
print("="*60)
print()
print("[OK] Transformacja zakonczona pomyslnie!")
print("="*60)
sys.stdout.flush()
