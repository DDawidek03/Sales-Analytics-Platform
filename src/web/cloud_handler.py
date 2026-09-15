import pyodbc
from azure.cosmos import CosmosClient, exceptions
from typing import Dict, Any, Optional
from datetime import datetime
import time

class CloudHandler:
    
    def __init__(self):
        self.azure_sql_server = os.environ.get('AZURE_SQL_SERVER', '')
        self.azure_sql_database = 'SalesDB'
        self.azure_sql_username = os.environ.get('AZURE_SQL_USERNAME', '')
        self.azure_sql_password = os.environ.get('AZURE_SQL_PASSWORD', '')
        
        self.cosmos_endpoint = os.environ.get('COSMOS_ENDPOINT', '')
        self.cosmos_key = os.environ.get('COSMOS_KEY', '')
        self.cosmos_database = "Global_Vista"
        
        self.azure_sql_connection = None
        self.azure_sql_cursor = None
        self.cosmos_client = None
        self.cosmos_db = None
        
        self.azure_sql_enabled = False
        self.cosmos_enabled = False
        
        self.driver = self._get_best_driver()
        
    def _get_best_driver(self) -> str:
        drivers = pyodbc.drivers()
        
        preferred_drivers = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 13 for SQL Server',
            'ODBC Driver 11 for SQL Server',
            'SQL Server'
        ]
        
        for driver in preferred_drivers:
            if driver in drivers:
                return driver
        
        return 'SQL Server'
    
    def connect_azure_sql(self) -> bool:
        try:
            if 'ODBC Driver 18' in self.driver:
                connection_string = (
                    f'DRIVER={{{self.driver}}};'
                    f'SERVER=tcp:{self.azure_sql_server},1433;'
                    f'DATABASE={self.azure_sql_database};'
                    f'UID={self.azure_sql_username};'
                    f'PWD={self.azure_sql_password};'
                    f'Encrypt=yes;'
                    f'TrustServerCertificate=yes;'
                    f'Connection Timeout=30;'
                    f'LoginTimeout=30;'
                )
            else:
                connection_string = (
                    f'DRIVER={{{self.driver}}};'
                    f'SERVER=tcp:{self.azure_sql_server},1433;'
                    f'DATABASE={self.azure_sql_database};'
                    f'UID={self.azure_sql_username};'
                    f'PWD={self.azure_sql_password};'
                    f'Encrypt=yes;'
                    f'TrustServerCertificate=no;'
                    f'Connection Timeout=30;'
                    f'LoginTimeout=30;'
                )
            
            self.azure_sql_connection = pyodbc.connect(connection_string)
            self.azure_sql_cursor = self.azure_sql_connection.cursor()
            self.azure_sql_enabled = True
            print("[+] Połączono z Azure SQL Database")
            return True
            
        except Exception as e:
            print(f"[-] Azure SQL niedostępny: {e}")
            self.azure_sql_enabled = False
            return False
    
    def connect_cosmos_db(self) -> bool:
        try:
            self.cosmos_client = CosmosClient(self.cosmos_endpoint, self.cosmos_key)
            self.cosmos_db = self.cosmos_client.get_database_client(self.cosmos_database)
            self.cosmos_db.read()
            self.cosmos_enabled = True
            print("[+] Połączono z Azure Cosmos DB")
            return True
            
        except exceptions.CosmosResourceNotFoundError:
            print(f"[-] Baza Cosmos DB '{self.cosmos_database}' nie istnieje")
            self.cosmos_enabled = False
            return False
        except Exception as e:
            print(f"[-] Cosmos DB niedostępny: {e}")
            self.cosmos_enabled = False
            return False
    
    def disconnect(self):
        if self.azure_sql_cursor:
            self.azure_sql_cursor.close()
        if self.azure_sql_connection:
            self.azure_sql_connection.close()
            print("[+] Azure SQL connection closed")
        if self.cosmos_client:
            print("[+] Cosmos DB connection closed")
    
    def validate_country_id(self, country_id: int) -> Optional[int]:
        if not self.azure_sql_enabled or not country_id:
            return None
        
        try:
            query = "SELECT COUNT(*) FROM Countries WHERE CountryID = ?"
            self.azure_sql_cursor.execute(query, (country_id,))
            count = self.azure_sql_cursor.fetchone()[0]
            return country_id if count > 0 else None
        except Exception as e:
            print(f"[-] Błąd walidacji CountryID: {e}")
            return None
    
    def insert_customer_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
            query = """
            INSERT INTO Customers (FirstName, LastName, Email, Phone, Address, CountryID)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            country_id = data.get('country') or data.get('countryId') or data.get('CountryID')
            if country_id:
                country_id = int(country_id)
                country_id = self.validate_country_id(country_id)
                if country_id is None:
                    print(f"[!] CountryID {data.get('country')} nie istnieje w Azure SQL - używam NULL")
            
            params = (
                data.get('firstName', data.get('FirstName')),
                data.get('lastName', data.get('LastName')),
                data.get('email', data.get('Email')),
                data.get('phone', data.get('Phone')),
                data.get('address', data.get('Address')),
                country_id
            )
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Customer zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Customer do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_product_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Product zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Product do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_seller_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Seller zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Seller do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_order_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
            query = """
            INSERT INTO Orders (CustomerID, SellerID, OrderDate, DateID, TotalAmount, 
                              Status, ShippingAddress, CountryID, PaymentMethod)
            VALUES (?, ?, GETDATE(), ?, ?, ?, ?, ?, ?)
            """
            
            customer_id = data.get('klient') or data.get('customerId') or data.get('CustomerID')
            seller_id = data.get('sprzedawca') or data.get('sellerId') or data.get('SellerID') or 1
            total_amount = data.get('całkowityKoszt') or data.get('totalAmount') or data.get('TotalAmount') or 0
            shipping_address = data.get('adresWysyłki') or data.get('shippingAddress') or data.get('ShippingAddress')
            country_id = data.get('kraj') or data.get('countryId') or data.get('CountryID') or 1
            payment_method = data.get('metodaPłatności') or data.get('paymentMethod') or data.get('PaymentMethod') or 'Credit Card'
            
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Order zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Order do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_country_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Country zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Country do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_region_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Region zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Region do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_category_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Category zapisana do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Category do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_bank_account_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] BankAccount zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu BankAccount do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_order_detail_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
            query = """
            INSERT INTO OrderDetails (OrderID, ProductID, Quantity, UnitPrice, 
                                     UnitCostPrice, Discount)
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] OrderDetail zapisany do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu OrderDetail do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_bank_transaction_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] BankTransaction zapisana do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu BankTransaction do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_promotion_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] Promotion zapisana do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu Promotion do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def insert_date_dimension_to_azure(self, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        try:
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
            
            self.azure_sql_cursor.execute(query, params)
            self.azure_sql_connection.commit()
            
            self.azure_sql_cursor.execute("SELECT @@IDENTITY")
            row = self.azure_sql_cursor.fetchone()
            new_id = int(row[0]) if row else None
            
            if new_id:
                print(f"[+] DateDimension zapisana do Azure SQL (ID: {new_id})")
            return new_id
            
        except Exception as e:
            print(f"[-] Błąd zapisu DateDimension do Azure SQL: {e}")
            self.azure_sql_connection.rollback()
            return None
    
    def sync_to_azure_sql(self, resource_path: str, data: Dict[str, Any]) -> Optional[int]:
        if not self.azure_sql_enabled:
            return None
        
        resource_handlers = {
            'customers': self.insert_customer_to_azure,
            'products': self.insert_product_to_azure,
            'sellers': self.insert_seller_to_azure,
            'orders': self.insert_order_to_azure,
            'banking/accounts': self.insert_bank_account_to_azure,
            'bankaccounts': self.insert_bank_account_to_azure,
            'countries': self.insert_country_to_azure,
            'regions': self.insert_region_to_azure,
            'categories': self.insert_category_to_azure,
            'orderdetails': self.insert_order_detail_to_azure,
            'order_details': self.insert_order_detail_to_azure,
            'order-details': self.insert_order_detail_to_azure,
            'banktransactions': self.insert_bank_transaction_to_azure,
            'bank_transactions': self.insert_bank_transaction_to_azure,
            'banking/transactions': self.insert_bank_transaction_to_azure,
            'promotions': self.insert_promotion_to_azure,
            'datedimension': self.insert_date_dimension_to_azure,
            'date_dimension': self.insert_date_dimension_to_azure,
        }
        
        handler = resource_handlers.get(resource_path.lower())
        if handler:
            return handler(data)
        
        print(f"Brak handlera Azure SQL dla: {resource_path}")
        return None
    
    def insert_purchase_history_to_cosmos(self, data: Dict) -> bool:
        if not self.cosmos_enabled:
            return False
        
        try:
            container = self.cosmos_db.get_container_client('PurchaseHistories')
            
            document = {
                "id": f"customer_{data.get('idKlienta', 0)}_{int(time.time())}",
                "CustomerID": int(data.get('idKlienta', 0)),
                "Email": data.get('email', ''),
                "CountryID": int(data.get('idKraju', 0)),
                "Purchases": [{
                    "OrderID": int(data.get('idZamWienia', 0)),
                    "OrderDate": datetime.fromisoformat(data.get('dataZamWienia', datetime.now().isoformat())).isoformat() if isinstance(data.get('dataZamWienia'), str) else datetime.now().isoformat(),
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
                "LastUpdated": datetime.now().isoformat()
            }
            
            container.create_item(body=document)
            print(f"[+] Purchase History zapisany do Cosmos DB")
            return True
            
        except Exception as e:
            print(f"[-] Błąd zapisu Purchase History do Cosmos DB: {e}")
            return False
    
    def insert_customer_behavior_to_cosmos(self, data: Dict) -> bool:
        if not self.cosmos_enabled:
            return False
        
        try:
            container = self.cosmos_db.get_container_client('CustomerBehavior')
            
            import random
            
            document = {
                "id": f"behavior_{data.get('idKlienta', 0)}_{int(time.time())}",
                "CustomerID": int(data.get('idKlienta', 0)),
                "Email": data.get('email', ''),
                "CountryID": int(data.get('idKraju', 1)),
                "Activity": [{
                    "EventID": random.randint(1000, 9999),
                    "EventType": data.get('typZdarzenia', 'page_view'),
                    "EventDate": datetime.now().isoformat(),
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
                "LastUpdated": datetime.now().isoformat()
            }
            
            container.create_item(body=document)
            print(f"[+] Customer Behavior zapisany do Cosmos DB")
            return True
            
        except Exception as e:
            print(f"[-] Błąd zapisu Customer Behavior do Cosmos DB: {e}")
            return False
    
    def insert_seller_profile_to_cosmos(self, data: Dict) -> bool:
        if not self.cosmos_enabled:
            return False
        
        try:
            container = self.cosmos_db.get_container_client('SellerProfiles')
            
            document = {
                "id": f"seller_{data.get('idSprzedawcy', 0)}_{int(time.time())}",
                "SellerID": int(data.get('idSprzedawcy', 0)),
                "Email": data.get('email', ''),
                "FirstName": data.get('imie', ''),
                "LastName": data.get('nazwisko', ''),
                "SellerType": data.get('typSprzedawcy', 'individual'),
                "RegionID": int(data.get('idRegionu', 0)),
                "HireDate": datetime.fromisoformat(data.get('dataZatrudnienia', datetime.now().isoformat())).isoformat() if isinstance(data.get('dataZatrudnienia'), str) else datetime.now().isoformat(),
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
                "LastUpdated": datetime.now().isoformat()
            }
            
            container.create_item(body=document)
            print(f"[+] Seller Profile zapisany do Cosmos DB")
            return True
            
        except Exception as e:
            print(f"[-] Błąd zapisu Seller Profile do Cosmos DB: {e}")
            return False
    
    def sync_to_cosmos_db(self, resource_path: str, data: Dict[str, Any]) -> bool:
        if not self.cosmos_enabled:
            return False
        
        resource_handlers = {
            'purchase': self.insert_purchase_history_to_cosmos,
            'behavior': self.insert_customer_behavior_to_cosmos,
            'profiles': self.insert_seller_profile_to_cosmos,
        }
        
        handler = resource_handlers.get(resource_path.lower())
        if handler:
            return handler(data)
        
        print(f"Brak handlera Cosmos DB dla: {resource_path}")
        return False
    
    def test_azure_connection(self) -> bool:
        try:
            if not self.azure_sql_enabled or not self.azure_sql_cursor:
                return self.connect_azure_sql()
            
            self.azure_sql_cursor.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"[-] Azure SQL connection test failed: {e}")
            return False
    
    def test_cosmos_connection(self) -> bool:
        try:
            if not self.cosmos_enabled or not self.cosmos_db:
                return self.connect_cosmos_db()
            
            self.cosmos_db.read()
            return True
        except Exception as e:
            print(f"[-] Cosmos DB connection test failed: {e}")
            return False
    
    def get_azure_record_count(self) -> int:
        try:
            if not self.azure_sql_enabled or not self.azure_sql_cursor:
                return 0
            
            total = 0
            tables = ['Customers', 'Sellers', 'Categories', 'Products', 'Orders']
            
            for table in tables:
                self.azure_sql_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.azure_sql_cursor.fetchone()[0]
                total += count
            
            return total
        except Exception as e:
            print(f"[-] Error counting Azure SQL records: {e}")
            return 0
    
    def get_cosmos_document_count(self) -> int:
        try:
            if not self.cosmos_enabled or not self.cosmos_db:
                return 0
            
            total = 0
            collections = ['PurchaseHistory', 'CustomerBehavior', 'SellerProfiles']
            
            for coll_name in collections:
                try:
                    container = self.cosmos_db.get_container_client(coll_name)
                    query = "SELECT VALUE COUNT(1) FROM c"
                    items = list(container.query_items(query=query, enable_cross_partition_query=True))
                    if items:
                        total += items[0]
                except Exception:
                    pass
            
            return total
        except Exception as e:
            print(f"[-] Error counting Cosmos DB documents: {e}")
            return 0
    
    def sync_all_to_azure_sql(self) -> Dict[str, Any]:
        try:
            if not self.azure_sql_enabled:
                return {'success': False, 'error': 'Azure SQL not connected'}
            
            # Import database_handler
            from database_handler import db_handler
            
            if not db_handler or not db_handler.connection:
                return {'success': False, 'error': 'Local database not connected'}
            
            print("\n" + "=" * 70)
            print("SYNCHRONIZACJA LOKALNEJ BAZY DO AZURE SQL")
            print("=" * 70)
            
            total_synced = 0
            
            # Tabele w kolejności zależności FK - DOKŁADNA struktura z lokalnej bazy
            tables = [
                # (nazwa, kolumny_z_ID, order_by)
                ('Countries', ['CountryID', 'CountryName', 'Continent'], 'CountryID'),
                ('Regions', ['RegionID', 'RegionName', 'CountryID'], 'RegionID'),
                ('Categories', ['CategoryID', 'CategoryName', 'ParentCategoryID', 'Description'], 'CASE WHEN ParentCategoryID IS NULL THEN 0 ELSE 1 END, CategoryID'),
                ('DateDimension', ['DateID', 'FullDate', 'Year', 'Quarter', 'Month', 'MonthName', 'Day', 'DayOfWeek'], 'DateID'),
                ('Sellers', ['SellerID', 'FirstName', 'LastName', 'Email', 'Phone', 'SellerType', 'RegionID', 'HireDate', 'CreatedAt', 'UpdatedAt'], 'SellerID'),
                ('Products', ['ProductID', 'ProductName', 'CategoryID', 'SellerID', 'Price', 'CostPrice', 'StockQuantity', 'Description', 'CreatedAt', 'UpdatedAt'], 'ProductID'),
                ('Customers', ['CustomerID', 'FirstName', 'LastName', 'Email', 'Phone', 'Address', 'CountryID', 'CreatedAt', 'UpdatedAt'], 'CustomerID'),
                ('BankAccounts', ['AccountID', 'AccountNumber', 'BankName', 'Currency', 'Balance', 'AccountType', 'SellerID', 'CreatedAt', 'UpdatedAt'], 'AccountID'),
                ('Orders', ['OrderID', 'CustomerID', 'SellerID', 'OrderDate', 'DateID', 'TotalAmount', 'Status', 'ShippingAddress', 'CountryID', 'PaymentMethod', 'CreatedAt'], 'OrderID'),
                ('OrderDetails', ['OrderDetailID', 'OrderID', 'ProductID', 'Quantity', 'UnitPrice', 'UnitCostPrice', 'Discount'], 'OrderDetailID'),
                ('BankTransactions', ['TransactionID', 'AccountID', 'TransactionDate', 'DateID', 'Amount', 'TransactionType', 'Description', 'Counterparty', 'ReferenceNumber', 'SellerID'], 'TransactionID'),
                ('Promotions', ['PromotionID', 'PromotionName', 'StartDateID', 'EndDateID', 'DiscountPercentage', 'ProductID', 'CategoryID', 'SellerID'], 'PromotionID'),
            ]
            
            local_cursor = db_handler.connection.cursor()
            azure_cursor = self.azure_sql_cursor
            
            for table_name, columns, order_by in tables:
                try:
                    print(f"\n[*] Synchronizacja {table_name}...")
                    
                    # Pobierz dane z lokalnej bazy w odpowiedniej kolejności
                    select_query = f"SELECT {', '.join(columns)} FROM {table_name} ORDER BY {order_by}"
                    local_cursor.execute(select_query)
                    rows = local_cursor.fetchall()
                    
                    if not rows:
                        print(f"  [i] Brak danych")
                        continue
                    
                    # Włącz IDENTITY_INSERT aby zachować oryginalne ID
                    azure_cursor.execute(f"SET IDENTITY_INSERT {table_name} ON")
                    
                    # Przygotuj INSERT query
                    placeholders = ', '.join(['?' for _ in columns])
                    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    
                    # Wstaw dane wiersz po wierszu (jak load_data_to_db.py)
                    count = 0
                    errors = 0
                    batch_size = 1000  # Commit co 1000 rekordów dla stabilności
                    
                    for row in rows:
                        try:
                            azure_cursor.execute(insert_query, *row)
                            count += 1
                            
                            # Commit częściej dla dużych tabel
                            if count % batch_size == 0:
                                self.azure_sql_connection.commit()
                                print(f"  [+] {count}/{len(rows)}...")
                        except Exception as e:
                            errors += 1
                            if errors <= 3:
                                print(f"  [-] Błąd: {str(e)[:80]}")
                    
                    # Wyłącz IDENTITY_INSERT i commit
                    azure_cursor.execute(f"SET IDENTITY_INSERT {table_name} OFF")
                    self.azure_sql_connection.commit()
                    total_synced += count
                    
                    print(f"  [✓] Załadowano {count}/{len(rows)}" + (f" ({errors} błędów)" if errors > 0 else ""))
                    
                except Exception as e:
                    print(f"  [!] Błąd tabeli {table_name}: {str(e)[:100]}")
                    self.azure_sql_connection.rollback()
            
            print("\n" + "=" * 70)
            print(f"[✓] ZAKOŃCZONO: Zsynchronizowano {total_synced} rekordów")
            print("=" * 70)
            
            return {
                'success': True,
                'records': total_synced,
                'message': f'Zsynchronizowano {total_synced} rekordów do Azure SQL'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_all_to_cosmos(self) -> Dict[str, Any]:
        """
        Synchronizuje wszystkie dane z lokalnego MongoDB do Cosmos DB
        Kopiuje WSZYSTKIE dokumenty zachowując ich strukturę
        """
        try:
            if not self.cosmos_enabled:
                return {'success': False, 'error': 'Cosmos DB not connected'}
            
            # Import database_handler
            from database_handler import db_handler
            
            if not db_handler or not db_handler.mongo_client:
                return {'success': False, 'error': 'Local MongoDB not connected'}
            
            print("\n" + "=" * 70)
            print("SYNCHRONIZACJA LOKALNEGO MONGODB DO COSMOS DB")
            print("=" * 70)
            
            total_synced = 0
            
            # Kolekcje do synchronizacji
            collections = [
                'PurchaseHistories',
                'CustomerBehavior', 
                'SellerProfiles',
                'BankTransactionLogs'
            ]
            
            local_db = db_handler.mongo_client['Global_Vista']  # Prawidłowa nazwa bazy
            
            for collection_name in collections:
                try:
                    print(f"\n[*] Synchronizacja {collection_name}...")
                    
                    # Pobierz WSZYSTKIE dokumenty z lokalnego MongoDB
                    local_collection = local_db[collection_name]
                    documents = list(local_collection.find())
                    
                    if not documents:
                        print(f"  [i] Brak dokumentów")
                        continue
                    
                    # Wstaw do Cosmos DB
                    cosmos_container = self.cosmos_db.get_container_client(collection_name)
                    count = 0
                    errors = 0
                    batch_size = 100  # Batch co 100 dokumentów
                    
                    for doc in documents:
                        try:
                            # Zamień MongoDB _id na Cosmos DB id
                            doc['id'] = str(doc['_id'])
                            del doc['_id']
                            
                            # Konwertuj datetime na string (ISO format)
                            def convert_datetime(obj):
                                """Rekursywnie konwertuje datetime na string"""
                                if isinstance(obj, dict):
                                    return {k: convert_datetime(v) for k, v in obj.items()}
                                elif isinstance(obj, list):
                                    return [convert_datetime(item) for item in obj]
                                elif hasattr(obj, 'isoformat'):  # datetime, date, time
                                    return obj.isoformat()
                                else:
                                    return obj
                            
                            doc = convert_datetime(doc)
                            
                            cosmos_container.upsert_item(doc)
                            count += 1
                            
                            if count % batch_size == 0:
                                print(f"  [+] {count}/{len(documents)}...")
                                
                        except Exception as e:
                            errors += 1
                            if errors <= 3:
                                print(f"  [-] Błąd: {str(e)[:80]}")
                    
                    total_synced += count
                    print(f"  [✓] Załadowano {count}/{len(documents)}" + (f" ({errors} błędów)" if errors > 0 else ""))
                    
                except Exception as e:
                    print(f"  [!] Błąd kolekcji {collection_name}: {str(e)[:100]}")
            
            print("\n" + "=" * 70)
            print(f"[✓] ZAKOŃCZONO: Zsynchronizowano {total_synced} dokumentów")
            print("=" * 70)
            
            return {
                'success': True,
                'documents': total_synced,
                'message': f'Zsynchronizowano {total_synced} dokumentów do Cosmos DB'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @property
    def azure_connected(self) -> bool:
        return self.azure_sql_enabled
    
    @property
    def cosmos_connected(self) -> bool:
        return self.cosmos_enabled
    
    def clear_azure_sql(self) -> Dict[str, Any]:
        """Czyści wszystkie dane z Azure SQL (poza tabelą Users)"""
        try:
            if not self.azure_sql_enabled:
                return {'success': False, 'error': 'Azure SQL not connected'}
            
            print("\n" + "=" * 70)
            print("CZYSZCZENIE AZURE SQL DATABASE")
            print("=" * 70)
            
            # Tabele w odwrotnej kolejności FK
            tables = [
                'Promotions', 'BankTransactions', 'OrderDetails', 'Orders',
                'BankAccounts', 'Customers', 'Products', 'Sellers',
                'DateDimension', 'Categories', 'Regions', 'Countries'
            ]
            
            cursor = self.azure_sql_cursor
            total_deleted = 0
            
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                    deleted = cursor.rowcount
                    self.azure_sql_connection.commit()
                    print(f"[✓] {table}: usunięto {deleted} rekordów")
                    total_deleted += deleted
                except Exception as e:
                    print(f"[!] Błąd {table}: {str(e)[:80]}")
            
            print("\n" + "=" * 70)
            print(f"[✓] ZAKOŃCZONO: Usunięto {total_deleted} rekordów")
            print("[i] Tabela 'Users' pozostała nietknięta")
            print("=" * 70)
            
            return {
                'success': True,
                'deleted': total_deleted,
                'message': f'Usunięto {total_deleted} rekordów z Azure SQL'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def clear_cosmos_db(self) -> Dict[str, Any]:
        """Czyści wszystkie dokumenty z Cosmos DB"""
        try:
            if not self.cosmos_enabled:
                return {'success': False, 'error': 'Cosmos DB not connected'}
            
            print("\n" + "=" * 70)
            print("CZYSZCZENIE COSMOS DB")
            print("=" * 70)
            
            collections = [
                'PurchaseHistories',
                'CustomerBehavior',
                'SellerProfiles',
                'BankTransactionLogs'
            ]
            
            total_deleted = 0
            
            for collection_name in collections:
                try:
                    print(f"\n[*] Czyszczenie {collection_name}...")
                    container = self.cosmos_db.get_container_client(collection_name)
                    
                    # Pobierz wszystkie dokumenty (tylko id)
                    query = "SELECT c.id FROM c"
                    items = list(container.query_items(query=query, enable_cross_partition_query=True))
                    
                    if not items:
                        print(f"  [i] Już pusta")
                        continue
                    
                    # Usuń każdy dokument
                    deleted = 0
                    for item in items:
                        try:
                            container.delete_item(item=item['id'], partition_key=item['id'])
                            deleted += 1
                            
                            if deleted % 100 == 0:
                                print(f"  [+] {deleted}/{len(items)}...")
                        except Exception:
                            pass  # Ignoruj błędy pojedynczych dokumentów
                    
                    total_deleted += deleted
                    print(f"  [✓] Usunięto {deleted} dokumentów")
                    
                except Exception as e:
                    print(f"  [!] Błąd: {str(e)[:80]}")
            
            print("\n" + "=" * 70)
            print(f"[✓] ZAKOŃCZONO: Usunięto {total_deleted} dokumentów")
            print("=" * 70)
            
            return {
                'success': True,
                'deleted': total_deleted,
                'message': f'Usunięto {total_deleted} dokumentów z Cosmos DB'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


cloud_handler = CloudHandler()

def init_cloud_connections():
    print("\nInicjalizacja połączeń z chmurą...")
    azure_status = cloud_handler.connect_azure_sql()
    cosmos_status = cloud_handler.connect_cosmos_db()
    
    if azure_status and cosmos_status:
        print("Wszystkie połączenia chmurowe aktywne")
    elif azure_status or cosmos_status:
        print("Połączenia chmurowe częściowo aktywne")
    else:
        print("Brak połączeń chmurowych - tylko lokalna baza danych")
    
    return (azure_status, cosmos_status)

def close_cloud_connections():
    cloud_handler.disconnect()

def sync_to_cloud(resource_path: str, data: Dict[str, Any], db_type: str = 'sql'):
    if db_type == 'sql':
        cloud_handler.sync_to_azure_sql(resource_path, data)
    elif db_type == 'mongo':
        cloud_handler.sync_to_cosmos_db(resource_path, data)
