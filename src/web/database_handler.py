import pyodbc
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class DatabaseHandler:
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.driver = self._get_best_driver()
        self.mongo_client = None
        self.mongo_db = None
        self._lock = threading.Lock()
        
    def _get_best_driver(self) -> str:
        drivers = pyodbc.drivers()
        
        preferred_drivers = [
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 13 for SQL Server',
            'ODBC Driver 11 for SQL Server',
            'SQL Server'
        ]
        
        for driver in preferred_drivers:
            if driver in drivers:
                return driver
        
        return 'SQL Server'
    
    def connect(self, server='localhost', database='SalesDB'):
        try:
            connection_string = (
                f'DRIVER={{{self.driver}}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'Trusted_Connection=yes;'
            )
            
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            print(f"[+] Połączono z lokalną bazą SQL: {database} na {server}")
            return True
            
        except Exception as e:
            print(f"[-] Nie można połączyć z lokalną bazą SQL: {e}")
            print(f"    Upewnij się, że SQL Server jest uruchomiony i baza '{database}' istnieje")
            self.connection = None
            self.cursor = None
            return False
    
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("[+] Połączenie SQL zamknięte")
        if self.mongo_client:
            self.mongo_client.close()
            print("[+] Połączenie MongoDB zamknięte")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List]:
        with self._lock:
            if not self.cursor or not self.connection:
                print(f"[-] Brak połączenia z bazą danych")
                return None
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return self.cursor.fetchall()
            except Exception as e:
                print(f"[-] Błąd zapytania: {e}")
                return None
    
    def execute_insert(self, query: str, params: tuple) -> Optional[int]:
        with self._lock:
            if not self.cursor or not self.connection:
                print(f"[-] Brak połączenia z bazą danych")
                return None
            try:
                self.cursor.execute(query, params)
                self.connection.commit()
                
                self.cursor.execute("SELECT @@IDENTITY")
                row = self.cursor.fetchone()
                return int(row[0]) if row else None
                
            except Exception as e:
                print(f"[-] Błąd INSERT: {e}")
                self.connection.rollback()
                return None
    
    def insert_customer(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Customers (FirstName, LastName, Email, Phone, Address, CountryID)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        country_id = data.get('country') or data.get('countryId') or data.get('CountryID')
        if country_id:
            country_id = int(country_id)
        else:
            country_id = 1
        
        params = (
            data.get('firstName', data.get('FirstName')),
            data.get('lastName', data.get('LastName')),
            data.get('email', data.get('Email')),
            data.get('phone', data.get('Phone')),
            data.get('address', data.get('Address')),
            country_id
        )
        
        return self.execute_insert(query, params)
    
    def insert_product(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Products (ProductName, CategoryID, SellerID, Price, CostPrice, 
                             StockQuantity, Description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        product_name = data.get('nazwaProduktu') or data.get('productName') or data.get('ProductName')
        category_id = data.get('kategoriaId') or data.get('categoryId') or data.get('CategoryID') or 1
        seller_id = data.get('sprzedawcaId') or data.get('sellerId') or data.get('SellerID') or 1
        price = data.get('cena') or data.get('price') or data.get('Price') or 0
        cost_price = data.get('cenaKosztowa') or data.get('costPrice') or data.get('CostPrice') or 0
        stock_qty = data.get('stanMagazynowy') or data.get('ilo') or data.get('stockQuantity') or data.get('StockQuantity') or 0
        description = data.get('opis') or data.get('description') or data.get('Description') or ''
        
        params = (
            product_name,
            int(category_id) if category_id else 1,
            int(seller_id) if seller_id else 1,
            float(price) if price else 0,
            float(cost_price) if cost_price else 0,
            int(stock_qty) if stock_qty else 0,
            description
        )
        
        return self.execute_insert(query, params)
    
    def insert_seller(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Sellers (FirstName, LastName, Email, Phone, SellerType, 
                           RegionID, HireDate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        seller_type = data.get('typSprzedawcy') or data.get('sellerType') or data.get('SellerType') or 'External'
        region_id = data.get('region') or data.get('regionId') or data.get('RegionID') or 1
        hire_date = data.get('dataZatrudnienia') or data.get('hireDate') or data.get('HireDate') or datetime.now()
        
        params = (
            data.get('firstName', data.get('FirstName')),
            data.get('lastName', data.get('LastName')),
            data.get('email', data.get('Email')),
            data.get('phone', data.get('Phone')),
            seller_type,
            int(region_id) if region_id else 1,
            hire_date
        )
        
        return self.execute_insert(query, params)
    
    def insert_order(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Orders (CustomerID, SellerID, OrderDate, DateID, TotalAmount, 
                          Status, ShippingAddress, CountryID, PaymentMethod)
        VALUES (?, ?, GETDATE(), ?, ?, ?, ?, ?, ?)
        """
        
        customer_id = data.get('klient') or data.get('customerId') or data.get('CustomerID')
        seller_id = data.get('sprzedawca') or data.get('sellerId') or data.get('SellerID') or 1
        total_amount = data.get('cakowityKoszt') or data.get('totalAmount') or data.get('TotalAmount') or 0
        shipping_address = data.get('adresWysyki') or data.get('shippingAddress') or data.get('ShippingAddress')
        country_id = data.get('kraj') or data.get('countryId') or data.get('CountryID') or 1
        payment_method = data.get('metodaPatnoci') or data.get('paymentMethod') or data.get('PaymentMethod') or 'Credit Card'
        
        params = (
            int(customer_id) if customer_id else None,
            int(seller_id) if seller_id else 1,
            data.get('dateId', data.get('DateID')),
            float(total_amount) if total_amount else 0,
            data.get('status', data.get('Status', 'Pending')),
            shipping_address,
            int(country_id) if country_id else 1,
            payment_method
        )
        
        return self.execute_insert(query, params)
    
    def insert_bank_account(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO BankAccounts (AccountNumber, BankName, Currency, Balance, 
                                 AccountType, SellerID)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        account_number = data.get('numerKonta') or data.get('accountNumber') or data.get('AccountNumber')
        bank_name = data.get('nazwaBanku') or data.get('bankName') or data.get('BankName')
        currency = data.get('waluta') or data.get('currency') or data.get('Currency') or 'PLN'
        balance = data.get('saldo') or data.get('balance') or data.get('Balance') or 0
        account_type = data.get('typKonta') or data.get('accountType') or data.get('AccountType') or 'Business'
        seller_id = data.get('sprzedawca') or data.get('sprzedawcaId') or data.get('sellerId') or data.get('SellerID') or 1
        
        params = (
            account_number,
            bank_name,
            currency,
            float(balance) if balance else 0,
            account_type,
            int(seller_id) if seller_id else 1
        )
        
        return self.execute_insert(query, params)
    
    def insert_country(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Countries (CountryName, Continent)
        VALUES (?, ?)
        """
        
        country_name = data.get('nazwaKraju') or data.get('countryName') or data.get('CountryName')
        continent = data.get('kontynent') or data.get('continent') or data.get('Continent') or 'Europe'
        
        params = (
            country_name,
            continent
        )
        
        return self.execute_insert(query, params)
    
    def insert_region(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Regions (RegionName, CountryID)
        VALUES (?, ?)
        """
        
        region_name = data.get('nazwaRegionu') or data.get('regionName') or data.get('RegionName')
        country_id = data.get('kraj') or data.get('krajId') or data.get('countryId') or data.get('CountryID') or 1
        
        params = (
            region_name,
            int(country_id) if country_id else 1
        )
        
        return self.execute_insert(query, params)
    
    def insert_category(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Categories (CategoryName, ParentCategoryID, Description)
        VALUES (?, ?, ?)
        """
        
        category_name = data.get('nazwaKategorii') or data.get('categoryName') or data.get('CategoryName')
        parent_id = data.get('kategoriaNadrzDna') or data.get('parentCategoryId') or data.get('ParentCategoryID')
        description = data.get('opis') or data.get('description') or data.get('Description') or ''
        
        if parent_id:
            try:
                parent_id = int(parent_id) if parent_id else None
            except (ValueError, TypeError):
                parent_id = None
        
        params = (
            category_name,
            parent_id,
            description
        )
        
        return self.execute_insert(query, params)
    
    def insert_order_detail(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO OrderDetails (OrderID, ProductID, Quantity, UnitPrice, UnitCostPrice, Discount)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        order_id = data.get('zamWienie') or data.get('orderId') or data.get('OrderID')
        product_id = data.get('produkt') or data.get('productId') or data.get('ProductID')
        quantity = data.get('ilo') or data.get('quantity') or data.get('Quantity') or 1
        unit_price = data.get('price') or data.get('unitPrice') or data.get('UnitPrice') or 0
        unit_cost_price = data.get('costPrice') or data.get('unitCostPrice') or data.get('UnitCostPrice') or 0
        discount = data.get('rabat') or data.get('discount') or data.get('Discount') or 0
        
        try:
            order_id = int(order_id) if order_id else None
            product_id = int(product_id) if product_id else None
            quantity = int(quantity)
            unit_price = float(unit_price)
            unit_cost_price = float(unit_cost_price)
            discount = float(discount)
        except (ValueError, TypeError) as e:
            print(f"[-] Błąd konwersji danych OrderDetail: {e}")
            return None
        
        params = (
            order_id,
            product_id,
            quantity,
            unit_price,
            unit_cost_price,
            discount
        )
        
        return self.execute_insert(query, params)
    
    def insert_bank_transaction(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO BankTransactions (AccountID, TransactionDate, DateID, Amount, 
                                     TransactionType, Description, Counterparty, 
                                     ReferenceNumber, SellerID)
        VALUES (?, GETDATE(), ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('accountId', data.get('AccountID')),
            data.get('dateId', data.get('DateID')),
            data.get('amount', data.get('Amount', 0)),
            data.get('transactionType', data.get('TransactionType', 'Transfer')),
            data.get('description', data.get('Description', '')),
            data.get('counterparty', data.get('Counterparty', '')),
            data.get('referenceNumber', data.get('ReferenceNumber', '')),
            data.get('sellerId', data.get('SellerID'))
        )
        
        return self.execute_insert(query, params)
    
    def insert_promotion(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO Promotions (PromotionName, StartDateID, EndDateID, 
                               DiscountPercentage, ProductID, CategoryID, SellerID)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        promotion_name = data.get('nazwaPromocji') or data.get('promotionName') or data.get('PromotionName')
        start_date = data.get('dataRozpoczcia') or data.get('dataRozpoczęcia') or data.get('startDateId') or data.get('StartDateID')
        end_date = data.get('dataZakoczenia') or data.get('dataZakończenia') or data.get('endDateId') or data.get('EndDateID')
        discount = data.get('procentRabatu') or data.get('rabat') or data.get('discountPercentage') or data.get('DiscountPercentage') or 0
        product_id = data.get('produkt') or data.get('productId') or data.get('ProductID')
        category_id = data.get('kategoria') or data.get('categoryId') or data.get('CategoryID')
        seller_id = data.get('sprzedawca') or data.get('sellerId') or data.get('SellerID')
        
        if start_date:
            start_date = int(start_date) if start_date else None
        if end_date:
            end_date = int(end_date) if end_date else None
        if product_id:
            product_id = int(product_id) if product_id else None
        if category_id:
            category_id = int(category_id) if category_id else None
        if seller_id:
            seller_id = int(seller_id) if seller_id else None
        
        params = (
            promotion_name,
            start_date,
            end_date,
            float(discount) if discount else 0,
            product_id,
            category_id,
            seller_id
        )
        
        return self.execute_insert(query, params)
    
    def insert_date_dimension(self, data: Dict[str, Any]) -> Optional[int]:
        query = """
        INSERT INTO DateDimension (FullDate, Year, Quarter, Month, MonthName, Day, DayOfWeek)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('fullDate', data.get('FullDate')),
            data.get('year', data.get('Year')),
            data.get('quarter', data.get('Quarter')),
            data.get('month', data.get('Month')),
            data.get('monthName', data.get('MonthName')),
            data.get('day', data.get('Day')),
            data.get('dayOfWeek', data.get('DayOfWeek'))
        )
        
        return self.execute_insert(query, params)
    
    def insert_generic(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
        resource_handlers = {
            'customers': self.insert_customer,
            'products': self.insert_product,
            'sellers': self.insert_seller,
            'orders': self.insert_order,
            'banking/accounts': self.insert_bank_account,
            'bankaccounts': self.insert_bank_account,
            'countries': self.insert_country,
            'regions': self.insert_region,
            'categories': self.insert_category,
            'orderdetails': self.insert_order_detail,
            'order_details': self.insert_order_detail,
            'order-details': self.insert_order_detail,
            'banktransactions': self.insert_bank_transaction,
            'bank_transactions': self.insert_bank_transaction,
            'banking/transactions': self.insert_bank_transaction,
            'promotions': self.insert_promotion,
            'datedimension': self.insert_date_dimension,
            'date_dimension': self.insert_date_dimension,
        }
        
        handler = resource_handlers.get(table_name.lower())
        if handler:
            return handler(data)
        
        print(f"[WARN] Brak handlera dla tabeli: {table_name}")
        return None
    
    def get_countries(self) -> List:
        query = "SELECT CountryID, CountryName, Continent FROM Countries ORDER BY CountryName"
        return self.execute_query(query) or []
    
    def get_categories(self) -> List:
        query = "SELECT CategoryID, CategoryName, ParentCategoryID, Description FROM Categories ORDER BY CategoryName"
        return self.execute_query(query) or []
    
    def get_regions(self) -> List:
        query = "SELECT RegionID, RegionName, CountryID FROM Regions ORDER BY RegionName"
        return self.execute_query(query) or []
    
    def get_sellers(self, limit: int = 10000) -> List:
        query = f"SELECT TOP {limit} SellerID, FirstName, LastName, Email, Phone, SellerType, RegionID, HireDate FROM Sellers ORDER BY SellerID"
        return self.execute_query(query) or []
    
    def get_customers(self, limit: int = 10000) -> List:
        query = f"SELECT TOP {limit} CustomerID, FirstName, LastName, Email, Phone, Address, CountryID FROM Customers ORDER BY CustomerID"
        return self.execute_query(query) or []
    
    def get_products(self, limit: int = 10000) -> List:
        query = f"SELECT TOP {limit} ProductID, ProductName, CategoryID, SellerID, Price, CostPrice, StockQuantity, Description FROM Products ORDER BY ProductID"
        return self.execute_query(query) or []
    
    def get_orders(self, limit: int = 10000) -> List:
        query = f"SELECT TOP {limit} OrderID, CustomerID, SellerID, OrderDate, DateID, TotalAmount, Status, ShippingAddress, CountryID, PaymentMethod FROM Orders ORDER BY OrderID DESC"
        return self.execute_query(query) or []
    
    def get_bank_accounts(self) -> List:
        query = "SELECT AccountID, AccountNumber, BankName, Currency, Balance, AccountType, SellerID FROM BankAccounts ORDER BY AccountID"
        return self.execute_query(query) or []
    
    def get_stats(self) -> Dict[str, int]:
        with self._lock:
            if not self.cursor or not self.connection:
                print(f"[-] Brak połączenia z bazą danych - statystyki niedostępne")
                return {'customers': 0, 'sellers': 0, 'categories': 0, 'products': 0, 'orders': 0, 'total': 0}
            
            stats = {}
            try:
                tables = [
                    'Countries', 'Regions', 'Categories', 'Sellers', 
                    'Customers', 'Products', 'BankAccounts', 'Orders', 
                    'OrderDetails', 'DateDimension'
                ]
                
                total = 0
                for table in tables:
                    try:
                        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = self.cursor.fetchone()[0]
                        stats[table.lower()] = count
                        total += count
                    except Exception as e:
                        print(f"[-] Błąd liczenia {table}: {e}")
                        stats[table.lower()] = 0
                
                stats['total'] = total
                
            except Exception as e:
                print(f"[-] Błąd pobierania statystyk: {e}")
                return {'customers': 0, 'sellers': 0, 'categories': 0, 'products': 0, 'orders': 0, 'total': 0}
            
            return stats
    
    
    def connect_mongo(self, connection_string: str = 'mongodb://localhost:27017/', db_name: str = 'Global_Vista'):
        try:
            print(f"[*] Próba połączenia z MongoDB: {connection_string}")
            self.mongo_client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.mongo_client.admin.command('ping')
            self.mongo_db = self.mongo_client[db_name]
            print(f"[+] Połączono z MongoDB: {db_name}")
            return True
        except ConnectionFailure as e:
            print(f"[-] Błąd połączenia z MongoDB (ConnectionFailure): {e}")
            self.mongo_client = None
            self.mongo_db = None
            return False
        except Exception as e:
            print(f"[-] Błąd MongoDB (Exception): {e}")
            import traceback
            traceback.print_exc()
            self.mongo_client = None
            self.mongo_db = None
            return False
    
    def get_mongo_transactions(self, limit: int = 50, transaction_type: str = None, currency: str = None) -> List[Dict]:
        try:
            print(f"[*] get_mongo_transactions called with limit={limit}, type={transaction_type}, currency={currency}")
            
            if self.mongo_db is None:
                print("[-] Brak połączenia z MongoDB")
                return []
            
            print(f"[*] MongoDB database: {self.mongo_db.name}")
            collection = self.mongo_db['BankTransactionLogs']
            
            doc_count = collection.count_documents({})
            print(f"[*] BankTransactionLogs collection has {doc_count} documents")
            
            if doc_count == 0:
                print("[-] Kolekcja BankTransactionLogs jest pusta!")
                return []
            
            pipeline = [
                {'$unwind': '$Transactions'},
                {'$project': {
                    '_id': 0,
                    'AccountID': 1,
                    'AccountNumber': 1,
                    'Currency': 1,
                    'TransactionID': '$Transactions.TransactionID',
                    'TransactionDate': '$Transactions.TransactionDate',
                    'Year': '$Transactions.Year',
                    'Quarter': '$Transactions.Quarter',
                    'Month': '$Transactions.Month',
                    'Amount': '$Transactions.Amount',
                    'TransactionType': '$Transactions.TransactionType',
                    'Description': '$Transactions.Description',
                    'Counterparty': '$Transactions.Counterparty',
                    'ReferenceNumber': '$Transactions.ReferenceNumber',
                    'Status': '$Transactions.Status',
                    'SellerID': '$Transactions.Seller.SellerID',
                    'SellerName': '$Transactions.Seller.SellerName',
                    'SellerType': '$Transactions.Seller.SellerType'
                }}
            ]
            
            if transaction_type and transaction_type != 'all':
                pipeline.append({'$match': {'TransactionType': transaction_type}})
            
            if currency:
                pipeline.append({'$match': {'Currency': currency}})
            
            pipeline.extend([
                {'$sort': {'TransactionDate': -1}},
                {'$limit': limit}
            ])
            
            print(f"[*] Executing aggregation pipeline...")
            results = list(collection.aggregate(pipeline))
            
            for doc in results:
                if 'TransactionDate' in doc and hasattr(doc['TransactionDate'], 'isoformat'):
                    doc['TransactionDate'] = doc['TransactionDate'].isoformat()
            
            print(f"[+] Pobrano {len(results)} transakcji z MongoDB")
            return results
            
        except Exception as e:
            print(f"[-] Błąd pobierania transakcji z MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_mongo_transaction_stats(self, transaction_type: str = None, currency: str = None) -> Dict:
        try:
            print(f"[*] get_mongo_transaction_stats called with type={transaction_type}, currency={currency}")
            
            if self.mongo_db is None:
                print("[-] Brak połączenia z MongoDB")
                return {'total': 0, 'deposits': 0, 'withdrawals': 0, 'balance': 0}
            
            collection = self.mongo_db['BankTransactionLogs']
            
            pipeline = [
                {'$unwind': '$Transactions'},
            ]
            
            match_stage = {}
            if transaction_type and transaction_type != 'all':
                match_stage['Transactions.TransactionType'] = transaction_type
            if currency:
                match_stage['Currency'] = currency
            
            if match_stage:
                pipeline.append({'$match': match_stage})
            
            pipeline.append({
                '$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'totalAmount': {'$sum': '$Transactions.Amount'},
                    'deposits': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$Transactions.TransactionType', 'deposit']},
                                '$Transactions.Amount',
                                0
                            ]
                        }
                    },
                    'withdrawals': {
                        '$sum': {
                            '$cond': [
                                {'$eq': ['$Transactions.TransactionType', 'withdrawal']},
                                '$Transactions.Amount',
                                0
                            ]
                        }
                    }
                }
            })
            
            print(f"[*] Executing stats aggregation pipeline...")
            result = list(collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats_dict = {
                    'total': stats.get('total', 0),
                    'deposits': float(stats.get('deposits', 0)),
                    'withdrawals': float(stats.get('withdrawals', 0)),
                    'balance': float(stats.get('deposits', 0)) - float(stats.get('withdrawals', 0))
                }
                print(f"[+] Stats calculated: {stats_dict}")
                return stats_dict
            else:
                print("[-] No stats data found")
                return {'total': 0, 'deposits': 0.0, 'withdrawals': 0.0, 'balance': 0.0}
                
        except Exception as e:
            print(f"[-] Błąd pobierania statystyk MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return {'total': 0, 'deposits': 0.0, 'withdrawals': 0.0, 'balance': 0.0}
    
    def insert_mongo_purchase_history(self, data: Dict) -> bool:
        try:
            if self.mongo_db is None:
                print("[-] Brak połączenia z MongoDB")
                return False
            
            from datetime import datetime
            
            collection = self.mongo_db['PurchaseHistories']
            
            document = {
                "CustomerID": int(data.get('idKlienta', 0)),
                "Email": data.get('email', ''),
                "CountryID": int(data.get('idKraju', 0)),
                "Purchases": [{
                    "OrderID": int(data.get('idZamWienia', 0)),
                    "OrderDate": datetime.fromisoformat(data.get('dataZamWienia', datetime.now().isoformat())),
                    "Year": int(data.get('rok', datetime.now().year)),
                    "Quarter": int(data.get('kwarta', 1)),
                    "Month": int(data.get('miesiC', 1)),
                    "TotalAmount": float(data.get('kwotaCaKowita', 0)),
                    "Status": data.get('status', 'pending'),
                    "Seller": {
                        "SellerID": int(data.get('idSprzedawcy', 0)),
                        "SellerName": data.get('nazwaSprzedawcy', ''),
                        "SellerType": data.get('typSprzedawcy', 'individual'),
                        "RegionID": int(data.get('idRegionu', 0))
                    },
                    "Products": [{
                        "ProductID": int(data.get('idProduktu', 0)),
                        "ProductName": data.get('productName', ''),
                        "CategoryID": int(data.get('idKategorii', 0)),
                        "CategoryName": data.get('nazwaKategorii', ''),
                        "Quantity": int(data.get('ilo', 0)),
                        "UnitPrice": float(data.get('price', 0)),
                        "UnitCostPrice": float(data.get('costPrice', 0)),
                        "Discount": float(data.get('rabat', 0))
                    }],
                    "ShippingCountryID": int(data.get('idKrajuWysyKi', 0)),
                    "PaymentMethod": data.get('metodaPAtnoCi', 'card')
                }],
                "LastUpdated": datetime.now()
            }
            
            result = collection.insert_one(document)
            
            if result.inserted_id:
                print(f"[+] Zapisano historię zakupów do MongoDB (ID: {result.inserted_id})")
                return True
            return False
            
        except Exception as e:
            print(f"[-] Błąd zapisu historii zakupów: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def insert_mongo_customer_behavior(self, data: Dict) -> bool:
        try:
            if self.mongo_db is None:
                print("[-] Brak połączenia z MongoDB")
                return False
            
            from datetime import datetime
            import random
            
            collection = self.mongo_db['CustomerBehavior']
            
            document = {
                "CustomerID": int(data.get('idKlienta', 0)),
                "Email": data.get('email', ''),
                "CountryID": int(data.get('idKraju', 1)),
                "Activity": [{
                    "EventID": random.randint(1000, 9999),
                    "EventType": data.get('typZdarzenia', 'page_view'),
                    "EventDate": datetime.now(),
                    "Year": datetime.now().year,
                    "Quarter": (datetime.now().month - 1) // 3 + 1,
                    "Month": datetime.now().month,
                    "Details": {
                        "ProductID": int(data.get('idProduktu', 0)),
                        "ProductName": data.get('nazwaProduktu', ''),
                        "CategoryID": int(data.get('idKategorii', 0)),
                        "CategoryName": data.get('nazwaKategorii', ''),
                        "Action": data.get('akcja', 'view'),
                        "PageURL": data.get('adresURL', '/'),
                        "SessionID": data.get('idSesji', f"session_{random.randint(10000, 99999)}"),
                        "SellerID": int(data.get('idSprzedawcy', 0)),
                        "SellerName": data.get('nazwaSprzedawcy', ''),
                        "RegionID": int(data.get('idRegionu', 0))
                    }
                }],
                "LastUpdated": datetime.now()
            }
            
            result = collection.insert_one(document)
            
            if result.inserted_id:
                print(f"[+] Zapisano dane zachowań klienta do MongoDB (ID: {result.inserted_id})")
                return True
            return False
            
        except Exception as e:
            print(f"[-] Błąd zapisu zachowań klienta: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def insert_mongo_seller_profile(self, data: Dict) -> bool:
        try:
            if self.mongo_db is None:
                print("[-] Brak połączenia z MongoDB")
                return False
            
            from datetime import datetime
            
            collection = self.mongo_db['SellerProfiles']
            
            document = {
                "SellerID": int(data.get('idSprzedawcy', 0)),
                "Email": data.get('email', ''),
                "FirstName": data.get('imie', ''),
                "LastName": data.get('nazwisko', ''),
                "SellerType": data.get('typSprzedawcy', 'individual'),
                "RegionID": int(data.get('idRegionu', 0)),
                "HireDate": datetime.fromisoformat(data.get('dataZatrudnienia', datetime.now().isoformat())),
                "Products": [{
                    "ProductID": int(data.get('idProduktu', 0)),
                    "ProductName": data.get('nazwaProduktu', ''),
                    "CategoryID": int(data.get('idKategorii', 0)),
                    "CategoryName": data.get('nazwaKategorii', ''),
                    "Price": float(data.get('cena', 0)),
                    "CostPrice": float(data.get('koszt', 0))
                }],
                "SalesSummary": {
                    "TotalOrders": int(data.get('liczbaZamowien', 0)),
                    "TotalRevenue": float(data.get('calkowitePrzychody', 0)),
                    "AverageOrderValue": float(data.get('sredniaWartoscZamowienia', 0)),
                    "TotalProductsSold": int(data.get('liczbaProdukow', 0))
                },
                "LastUpdated": datetime.now()
            }
            
            result = collection.insert_one(document)
            
            if result.inserted_id:
                print(f"[+] Zapisano profil sprzedawcy do MongoDB (ID: {result.inserted_id})")
                return True
            return False
            
        except Exception as e:
            print(f"[-] Błąd zapisu profilu sprzedawcy: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_mongo_transaction_count(self) -> int:
        """Get total count of transactions in MongoDB"""
        try:
            if self.mongo_db is None:
                print("[-] Brak połączenia z MongoDB")
                return 0
            
            collection = self.mongo_db['BankTransactionLogs']
            pipeline = [
                {'$unwind': '$Transactions'},
                {'$count': 'total'}
            ]
            result = list(collection.aggregate(pipeline))
            return result[0]['total'] if result else 0
        except Exception as e:
            print(f"[-] Błąd pobierania liczby transakcji MongoDB: {e}")
            return 0
    
    def get_mongo_document_count(self) -> int:
        """Get total count of all documents in MongoDB"""
        try:
            if self.mongo_db is None:
                print("[-] Brak połączenia z MongoDB")
                return 0
            
            total = 0
            collections = ['PurchaseHistories', 'CustomerBehavior', 'SellerProfiles', 'BankTransactionLogs']
            
            for coll_name in collections:
                try:
                    count = self.mongo_db[coll_name].count_documents({})
                    total += count
                except Exception:
                    pass
            
            return total
        except Exception as e:
            print(f"[-] Błąd pobierania liczby dokumentów MongoDB: {e}")
            return 0

db_handler = DatabaseHandler()

def init_database():
    sql_connected = db_handler.connect()
    mongo_connected = db_handler.connect_mongo()
    return sql_connected or mongo_connected

def close_database():
    db_handler.disconnect()
