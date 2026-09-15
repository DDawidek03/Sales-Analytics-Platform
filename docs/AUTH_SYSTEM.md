# System Uwierzytelniania GlobalVista

## 🔐 Opis

System uwierzytelniania z kontrolą dostępu dla aplikacji GlobalVista. Dane użytkowników przechowywane są w **Azure SQL Database**.

## 📋 Wymagania

```bash
pip install flask-login
```

## 🚀 Pierwsze uruchomienie

### 1. Utwórz domyślnego admina

**Domyślne dane logowania:**
- Login: `admin`
- Hasło: `admin123`

⚠️ **WAŻNE**: Zmień hasło po pierwszym logowaniu!

### 2. Uruchom aplikację

```bash
python app.py
```

### 3. Zaloguj się

Otwórz: http://127.0.0.1:5000/login

## 👥 Role użytkowników

### Admin
- ✅ Pełny dostęp do panelu administracyjnego
- ✅ Generowanie danych (SQL, NoSQL)
- ✅ Ładowanie danych do baz
- ✅ Synchronizacja z Azure (SQL, Cosmos DB)
- ✅ Usuwanie danych
- ✅ Odczyt i zapis danych

### User
- ✅ Dostęp do dashboardu
- ✅ Odczyt danych
- ✅ Podstawowe operacje CRUD
- ❌ Brak dostępu do generowania danych
- ❌ Brak dostępu do panelu admin

### Guest
- ✅ Tylko odczyt danych
- ❌ Brak możliwości modyfikacji

## 🔧 Zarządzanie użytkownikami

### Dodawanie użytkownika

Użyj interfejsu panelu administracyjnego lub kodu:

```python
from cloud_handler import CloudHandler
from auth_handler import AuthHandler

cloud = CloudHandler()
cloud.connect_azure_sql()
auth = AuthHandler(cloud)

auth.create_user('jan_kowalski', 'haslo123', 'user', 'jan@example.com')
```

### Zmiana hasła

```python
auth.change_password('jan_kowalski', 'nowe_haslo')
```

### Dezaktywacja użytkownika

```python
auth.delete_user('jan_kowalski')
```

### Lista użytkowników

```python
users = auth.get_all_users()
for user in users:
    print(f"{user['username']} - {user['role']}")
```

## 🛡️ Zabezpieczenia

### Chronione endpointy (wymagają logowania)

#### Admin (tylko rola `admin`)
- `POST /api/admin/generate-sql` - generowanie danych SQL
- `POST /api/admin/load-sql` - ładowanie danych SQL
- `POST /api/admin/sync-azure-sql` - synchronizacja z Azure SQL
- `POST /api/admin/sync-cosmos` - synchronizacja z Cosmos DB

#### Dashboard (wszystkie zalogowane role)
- `GET /dashboard` - panel zarządzania

### API uwierzytelniania

#### Logowanie
```javascript
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123",
  "remember": false
}
```

#### Wylogowanie
```javascript
POST /api/auth/logout
```

#### Sprawdzenie użytkownika
```javascript
GET /api/auth/current-user
```

#### Lista użytkowników (tylko admin)
```javascript
GET /api/auth/users
```

## 📊 Struktura bazy danych

### Tabela `Users` (Azure SQL)

```sql
CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(50) UNIQUE NOT NULL,
    password_hash NVARCHAR(128) NOT NULL,
    salt NVARCHAR(64) NOT NULL,
    role NVARCHAR(20) NOT NULL,
    email NVARCHAR(100),
    created_at DATETIME DEFAULT GETDATE(),
    last_login DATETIME NULL,
    is_active BIT DEFAULT 1
);
```

## 🔄 Przepływ uwierzytelniania

1. Użytkownik wchodzi na `/dashboard` lub `/admin.html`
2. Middleware sprawdza czy użytkownik jest zalogowany
3. Jeśli NIE → przekierowanie do `/login.html`
4. Użytkownik podaje login i hasło
5. Backend weryfikuje w Azure SQL
6. Przy sukcesie → tworzenie sesji Flask-Login
7. Przekierowanie do odpowiedniej strony (admin/dashboard)

## 🛠️ Rozwiązywanie problemów

### System uwierzytelniania wyłączony

Jeśli widzisz:
```
[!] Azure SQL niedostępny - system uwierzytelniania wyłączony
```

**Przyczyny:**
- Brak połączenia z Azure SQL
- Nieprawidłowe dane logowania w `cloud_handler.py`
- Firewall Azure blokuje połączenie

**Rozwiązanie:**
1. Sprawdź połączenie: `python test_azure_sql_connection.py`
2. Zweryfikuj dane w `cloud_handler.py`:
   - `azure_sql_server`
   - `azure_sql_username`
   - `azure_sql_password`
3. Dodaj swoje IP do firewall Azure

### Nie można utworzyć użytkownika

**Problem:** `Użytkownik już istnieje`

**Rozwiązanie:** Użytkownik o tej nazwie już jest w bazie. Wybierz inną nazwę.

### Błąd podczas logowania

**Problem:** `Nieprawidłowa nazwa użytkownika lub hasło`

**Rozwiązanie:**
- Sprawdź czy użytkownik jest aktywny (`is_active = 1`)
- Zweryfikuj poprawność hasła
- Sprawdź logi serwera

## 📝 Changelog

### v1.0 (28.12.2024)
- ✅ System uwierzytelniania z Flask-Login
- ✅ Przechowywanie użytkowników w Azure SQL
- ✅ Role: admin, user, guest
- ✅ Hashowanie haseł (PBKDF2-SHA256)
- ✅ Kontrola dostępu do endpointów
- ✅ Strona logowania
- ✅ Auto-przekierowanie niezalogowanych użytkowników
- ✅ Wyświetlanie zalogowanego użytkownika w UI

## 🔐 Bezpieczeństwo

- Hasła hashowane algorytmem PBKDF2-HMAC-SHA256 (100,000 iteracji)
- Każde hasło ma unikalny salt (64 znaki hex)
- Sesje zarządzane przez Flask-Login
- Secret key aplikacji (zmień w produkcji!)
- HTTPS zalecane w produkcji

## 📞 Kontakt

W razie problemów sprawdź logi aplikacji lub skontaktuj się z administratorem.
