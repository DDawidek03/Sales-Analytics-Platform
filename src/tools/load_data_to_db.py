import pyodbc
import pandas as pd
import os
import sys
import codecs
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

SERVER = 'localhost'
DATABASE = 'SalesDB'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_FOLDER = os.path.join(PROJECT_ROOT, 'sales_data')

def get_connection():
    drivers = pyodbc.drivers()
    
    if 'ODBC Driver 17 for SQL Server' in drivers:
        driver = 'ODBC Driver 17 for SQL Server'
    elif 'ODBC Driver 18 for SQL Server' in drivers:
        driver = 'ODBC Driver 18 for SQL Server'
    elif 'ODBC Driver 13 for SQL Server' in drivers:
        driver = 'ODBC Driver 13 for SQL Server'
    else:
        driver = 'SQL Server'
    
    connection_string = (
        f'DRIVER={{{driver}}};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'Trusted_Connection=yes;'
    )
    
    return pyodbc.connect(connection_string)

def load_countries(cursor, df):
    print("\nŁadowanie Countries...")
    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO Countries (CountryName, Continent)
                VALUES (?, ?)
            """, row['CountryName'], row['Continent'])
            count += 1
        except Exception as e:
            print(f"  Błąd wiersza {row['CountryID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} krajów")
    return count

def load_date_dimension(cursor, df):
    print("\nŁadowanie DateDimension...")
    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO DateDimension (FullDate, Year, Quarter, Month, MonthName, Day, DayOfWeek)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row['FullDate'], row['Year'], row['Quarter'], row['Month'], 
                row['MonthName'], row['Day'], row['DayOfWeek'])
            count += 1
        except Exception as e:
            if count == 0:
                print(f"  Błąd: {e}")
    print(f"  Załadowano {count}/{len(df)} dat")
    return count

def load_categories(cursor, df):
    print("\nŁadowanie Categories...")
    count = 0
    for _, row in df.iterrows():
        try:
            parent_id = int(row['ParentCategoryID']) if pd.notna(row['ParentCategoryID']) else None
            cursor.execute("""
                INSERT INTO Categories (CategoryName, ParentCategoryID, Description)
                VALUES (?, ?, ?)
            """, row['CategoryName'], parent_id, row.get('Description', ''))
            count += 1
        except Exception as e:
            print(f"  Błąd kategorii '{row['CategoryName']}': {e}")
    print(f"  Załadowano {count}/{len(df)} kategorii")
    return count

def load_regions(cursor, df):
    print("\nŁadowanie Regions...")
    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO Regions (RegionName, CountryID)
                VALUES (?, ?)
            """, row['RegionName'], row['CountryID'])
            count += 1
        except Exception as e:
            if count == 0:
                print(f"  Błąd: {e}")
    print(f"  Załadowano {count}/{len(df)} regionów")
    return count

def load_sellers(cursor, df):
    print("\nŁadowanie Sellers...")
    count = 0
    for _, row in df.iterrows():
        try:
            hire_date = pd.to_datetime(row['HireDate']) if pd.notna(row['HireDate']) else None
            cursor.execute("""
                INSERT INTO Sellers (FirstName, LastName, Email, Phone, SellerType, RegionID, HireDate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row['FirstName'], row['LastName'], row['Email'], row['Phone'],
                row['SellerType'], row['RegionID'], hire_date)
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd sprzedawcy {row['SellerID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} sprzedawców")
    return count

def load_products(cursor, df):
    print("\nŁadowanie Products...")
    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO Products (ProductName, CategoryID, SellerID, Price, CostPrice, StockQuantity, Description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row['ProductName'], row['CategoryID'], row['SellerID'],
                row['Price'], row['CostPrice'], row['StockQuantity'], row.get('Description', ''))
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd produktu {row['ProductID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} produktów")
    return count

def load_customers(cursor, df):
    print("\nŁadowanie Customers...")
    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO Customers (FirstName, LastName, Email, Phone, Address, CountryID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, row['FirstName'], row['LastName'], row['Email'], row['Phone'],
                row['Address'], row['CountryID'])
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd klienta {row['CustomerID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} klientów")
    return count

def load_bank_accounts(cursor, df):
    print("\nŁadowanie BankAccounts...")
    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO BankAccounts (AccountNumber, BankName, Currency, Balance, AccountType, SellerID)
                VALUES (?, ?, ?, ?, ?, ?)
            """, row['AccountNumber'], row['BankName'], row['Currency'],
                row['Balance'], row['AccountType'], row['SellerID'])
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd konta {row['AccountID']}: {e}")
    print(f"Załadowano {count}/{len(df)} kont bankowych")
    return count

def load_orders(cursor, df):
    print("\nŁadowanie Orders...")
    count = 0
    for _, row in df.iterrows():
        try:
            order_date = pd.to_datetime(row['OrderDate']) if pd.notna(row['OrderDate']) else None
            cursor.execute("""
                INSERT INTO Orders (CustomerID, SellerID, OrderDate, DateID, TotalAmount, Status, ShippingAddress, CountryID, PaymentMethod)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row['CustomerID'], row['SellerID'], order_date, row['DateID'],
                row['TotalAmount'], row['Status'], row['ShippingAddress'], 
                row['CountryID'], row['PaymentMethod'])
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd zamówienia {row['OrderID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} zamówień")
    return count

def load_order_details(cursor, df):
    print("\nŁadowanie OrderDetails...")
    count = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO OrderDetails (OrderID, ProductID, Quantity, UnitPrice, UnitCostPrice, Discount)
                VALUES (?, ?, ?, ?, ?, ?)
            """, row['OrderID'], row['ProductID'], row['Quantity'],
                row['UnitPrice'], row['UnitCostPrice'], row['Discount'])
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd szczegółu zamówienia {row['OrderDetailID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} szczegółów zamówień")
    return count

def load_bank_transactions(cursor, df):
    print("\nŁadowanie BankTransactions...")
    count = 0
    for _, row in df.iterrows():
        try:
            trans_date = pd.to_datetime(row['TransactionDate']) if pd.notna(row['TransactionDate']) else None
            cursor.execute("""
                INSERT INTO BankTransactions (AccountID, TransactionDate, DateID, Amount, TransactionType, Description, Counterparty, ReferenceNumber, SellerID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row['AccountID'], trans_date, row['DateID'], row['Amount'],
                row['TransactionType'], row.get('Description', ''), 
                row.get('Counterparty', ''), row.get('ReferenceNumber', ''), row['SellerID'])
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd transakcji {row['TransactionID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} transakcji bankowych")
    return count

def load_promotions(cursor, df):
    print("\nŁadowanie Promotions...")
    count = 0
    for _, row in df.iterrows():
        try:
            product_id = int(row['ProductID']) if pd.notna(row['ProductID']) else None
            category_id = int(row['CategoryID']) if pd.notna(row['CategoryID']) else None
            seller_id = int(row['SellerID']) if pd.notna(row['SellerID']) else None
            cursor.execute("""
                INSERT INTO Promotions (PromotionName, StartDateID, EndDateID, DiscountPercentage, ProductID, CategoryID, SellerID)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row['PromotionName'], row['StartDateID'], row['EndDateID'],
                row['DiscountPercentage'], product_id, category_id, seller_id)
            count += 1
        except Exception as e:
            if count < 3:
                print(f"  Błąd promocji {row['PromotionID']}: {e}")
    print(f"  Załadowano {count}/{len(df)} promocji")
    return count

def main():
    print("=" * 70)
    print("ŁADOWANIE DANYCH DO BAZY SALESDB")
    print("=" * 70)
    print(f"Źródło danych: {DATA_FOLDER}")
    print(f"Cel: {SERVER}/{DATABASE}")
    
    try:
        print("\nŁączenie z bazą danych...")
        conn = get_connection()
        cursor = conn.cursor()
        print("Połączono z bazą danych")
        
        total_loaded = 0
        
        file_path = os.path.join(DATA_FOLDER, 'countries.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_countries(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'date_dimension.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_date_dimension(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'categories.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df = df.sort_values('ParentCategoryID', na_position='first')
            total_loaded += load_categories(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'regions.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_regions(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'sellers.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_sellers(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'products.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_products(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'customers.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_customers(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'bank_accounts.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_bank_accounts(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'orders.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_orders(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'order_details.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_order_details(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'bank_transactions.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_bank_transactions(cursor, df)
            conn.commit()
        
        file_path = os.path.join(DATA_FOLDER, 'promotions.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            total_loaded += load_promotions(cursor, df)
            conn.commit()
        
        print("\n" + "=" * 70)
        print(f"ZAKOŃCZONO: Załadowano łącznie {total_loaded} rekordów")
        print("=" * 70)
        
        cursor.close()
        conn.close()
        print("\nPołączenie zamknięte")
        
    except Exception as e:
        print(f"\nBŁĄD: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == '__main__':
    main()
