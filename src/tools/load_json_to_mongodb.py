
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
import json
import os
from datetime import datetime
import sys
import re
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.append(os.path.dirname(__file__))
from data_validation import DataValidator

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
DATABASE = 'Global_Vista'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_FOLDER = os.path.join(PROJECT_ROOT, 'nosql_data')

FILE_TO_COLLECTION = {
    'seller_profiles.json': 'SellerProfiles',
    'customer_behavior.json': 'CustomerBehavior',
    'purchase_histories.json': 'PurchaseHistories',
    'bank_transaction_logs.json': 'BankTransactionLogs'
}

def get_mongo_connection():
    try:
        client = MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/')
        client.admin.command('ping')
        print(f"Połączono z MongoDB: {MONGO_HOST}:{MONGO_PORT}")
        return client
    except Exception as e:
        print(f"Błąd połączenia z MongoDB: {e}")
        raise

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"  Błąd wczytywania {os.path.basename(file_path)}: {e}")
        return None

def clean_data(data, validator=None):
    if isinstance(data, list):
        for item in data:
            clean_data(item, validator)
    elif isinstance(data, dict):
        for key, value in data.items():
            if value == "NaN" or (isinstance(value, float) and str(value) == 'nan'):
                data[key] = None
            elif isinstance(value, str) and ('T' in value or '-' in value):
                try:
                    data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
            elif validator and key.lower() == 'email' and isinstance(value, str):
                if not validator.validate_email(value):
                    validator.validation_report['invalid_emails'] += 1
            elif validator and 'phone' in key.lower() and isinstance(value, str):
                if not validator.validate_phone(value):
                    validator.validation_report['invalid_phones'] += 1
            elif validator and isinstance(value, str) and key.lower() not in ['email', '_id']:
                data[key] = validator.sanitize_string(value)
            elif isinstance(value, (dict, list)):
                clean_data(value, validator)
    return data

def load_collection(collection, file_path, collection_name, validator=None):
    print(f"\nŁadowanie {collection_name}...")
    
    data = load_json_file(file_path)
    if not data:
        return 0
    
    print(f"  Walidacja danych (Regex, sanityzacja)...")
    data = clean_data(data, validator)
    
    if not isinstance(data, list):
        data = [data]
    
    if not data:
        print(f"  Brak danych w pliku")
        return 0
    
    try:
        if len(data) == 1:
            collection.insert_one(data[0])
            print(f"  Załadowano 1 dokument")
            return 1
        else:
            result = collection.insert_many(data, ordered=False)
            print(f"  Załadowano {len(result.inserted_ids)}/{len(data)} dokumentów")
            return len(result.inserted_ids)
    except BulkWriteError as e:
        successful = len(data) - len(e.details.get('writeErrors', []))
        print(f"  Załadowano {successful}/{len(data)} dokumentów (pomijam duplikaty)")
        return successful
    except Exception as e:
        print(f"  Błąd: {e}")
        return 0

def main():
    print("=" * 70)
    print("ŁADOWANIE DANYCH JSON DO MONGODB")
    print("=" * 70)
    print(f"Źródło danych: {DATA_FOLDER}")
    print(f"Cel: mongodb://{MONGO_HOST}:{MONGO_PORT}/{DATABASE}")
    
    validator = DataValidator(verbose=True)
    print("Moduł walidacji danych aktywny")
    
    try:
        print("\nŁączenie z MongoDB...")
        client = get_mongo_connection()
        db = client[DATABASE]
        
        print("\nSkanowanie plików JSON...")
        available_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.json')]
        print(f"Znaleziono {len(available_files)} plików JSON")
        
        total_loaded = 0
        loaded_collections = []
        
        for json_file, collection_name in FILE_TO_COLLECTION.items():
            file_path = os.path.join(DATA_FOLDER, json_file)
            
            if os.path.exists(file_path):
                count = load_collection(db[collection_name], file_path, collection_name, validator)
                total_loaded += count
                if count > 0:
                    loaded_collections.append(f"{collection_name} ({count} docs)")
            else:
                print(f"\nPlik {json_file} nie istnieje, pomijam...")
        
        for json_file in available_files:
            if json_file not in FILE_TO_COLLECTION:
                collection_name = os.path.splitext(json_file)[0]
                file_path = os.path.join(DATA_FOLDER, json_file)
                
                print(f"\nZnaleziono dodatkowy plik: {json_file}")
                count = load_collection(db[collection_name], file_path, collection_name, validator)
                total_loaded += count
                if count > 0:
                    loaded_collections.append(f"{collection_name} ({count} docs)")
        
        print("\n" + "=" * 70)
        print(f"ZAKOŃCZONO: Załadowano łącznie {total_loaded} dokumentów")
        print("=" * 70)
        
        if loaded_collections:
            print("\nZaładowane kolekcje:")
            for i, col in enumerate(loaded_collections, 1):
                print(f"   {i}. {col}")
        
        print("\nStatystyki bazy danych:")
        for collection_name in db.list_collection_names():
            count = db[collection_name].count_documents({})
            print(f"   {collection_name}: {count} dokumentów")
        
        print("\n" + "=" * 70)
        print("RAPORT WALIDACJI DANYCH")
        print("=" * 70)
        validation_summary = validator.validation_report
        print(f"Niepoprawne emaile (Regex):    {validation_summary['invalid_emails']}")
        print(f"Niepoprawne telefony (Regex):  {validation_summary['invalid_phones']}")
        print(f"Sanityzacja wykonana:          Wszystkie pola tekstowe")
        print("=" * 70)
        
        client.close()
        print("\nPołączenie zamknięte")
        
    except Exception as e:
        print(f"\nBŁĄD: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
