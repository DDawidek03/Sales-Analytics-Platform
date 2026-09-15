# 🔧 Konfiguracja Projektu GlobalVista Analytics

## Wymagania wstępne

### Oprogramowanie
- **Python 3.x** (zalecane 3.10+)
- **SQL Server** (lokalny, z bazą `SalesDB`)
- **MongoDB** (lokalny, domyślny port 27017)
- **ODBC Driver** dla SQL Server (17 lub 18)

### Konta chmurowe (opcjonalnie)
- **Azure SQL Database** — do synchronizacji danych
- **Azure Cosmos DB** — do przechowywania danych NoSQL w chmurze

---

## 🚀 Szybki start

### 1. Zainstaluj zależności Python

```bash
pip install -r requirements.txt
```

### 2. Skonfiguruj zmienne środowiskowe

```bash
# Skopiuj szablon
cp .env.example .env

# Edytuj plik .env i wpisz swoje wartości
# (serwer Azure, hasła, klucze itp.)
```

### 3. Utwórz bazę danych

Uruchom skrypt SQL na swoim serwerze:
```bash
# Dla SQL Server
sqlcmd -S localhost -i src/database/SalesDB_SQLServer.sql

# Lub otwórz plik w SSMS i wykonaj go ręcznie
```

### 4. Wygeneruj dane testowe

```bash
python src/tools/generate_sales_data.py --orders 1000
python src/tools/generate_nosql_data.py
```

### 5. Załaduj dane do baz

```bash
python src/tools/load_data_to_db.py
python src/tools/load_json_to_mongodb.py
```

### 6. Uruchom aplikację

```bash
cd src/web
python app.py
```

Otwórz: http://127.0.0.1:5000

---

## 📁 Struktura konfiguracji

```
Praca_Inzynierska/
├── .env                  # ⛔ Twoje hasła (NIE COMMITOWAĆ!)
├── .env.example          # ✅ Szablon bez wartości (w repo)
├── .gitignore            # ✅ Lista ignorowanych plików
├── config/
│   └── README_SETUP.md   # ✅ Ta instrukcja
└── ...
```

---

## 🔐 Zmienne środowiskowe (.env)

| Zmienna | Opis | Wymagana |
|---------|------|----------|
| `FLASK_SECRET_KEY` | Klucz sesji Flask | ✅ Tak |
| `AZURE_SQL_SERVER` | Adres serwera Azure SQL | Tylko z Azure |
| `AZURE_SQL_DATABASE` | Nazwa bazy Azure SQL | Tylko z Azure |
| `AZURE_SQL_USERNAME` | Login Azure SQL | Tylko z Azure |
| `AZURE_SQL_PASSWORD` | Hasło Azure SQL | Tylko z Azure |
| `COSMOS_ENDPOINT` | URL endpointu Cosmos DB | Tylko z Cosmos |
| `COSMOS_KEY` | Klucz Cosmos DB | Tylko z Cosmos |
| `COSMOS_DATABASE` | Nazwa bazy Cosmos DB | Tylko z Cosmos |
| `LOCAL_SQL_SERVER` | Adres lokalnego SQL Server | Domyślnie: `localhost` |
| `LOCAL_SQL_DATABASE` | Nazwa lokalnej bazy SQL | Domyślnie: `SalesDB` |
| `MONGO_HOST` | Adres MongoDB | Domyślnie: `127.0.0.1` |
| `MONGO_PORT` | Port MongoDB | Domyślnie: `27017` |
| `MONGO_DATABASE` | Nazwa bazy MongoDB | Domyślnie: `Global_Vista` |

---

## ⚠️ Bezpieczeństwo

1. **NIGDY** nie commituj pliku `.env` do repozytorium
2. **Zmień** domyślne hasła przed pierwszym użyciem
3. Plik `.env` jest automatycznie wykluczony przez `.gitignore`
4. Jeśli klucze zostały kiedykolwiek ujawnione — **zmień je natychmiast**
5. W produkcji używaj **HTTPS** i silnego `FLASK_SECRET_KEY`

