import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any
from flask_login import UserMixin

class User(UserMixin):
    """Klasa reprezentująca użytkownika"""
    def __init__(self, user_id: int, username: str, role: str, email: str = None):
        self.id = user_id
        self.username = username
        self.role = role  # 'admin', 'user', 'guest'
        self.email = email
    
    def has_permission(self, permission: str) -> bool:
        """Sprawdza czy użytkownik ma daną uprawnienie"""
        permissions = {
            'admin': ['read', 'write', 'delete', 'generate', 'sync', 'admin_panel'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
        return permission in permissions.get(self.role, [])

class AuthHandler:
    """Handler do zarządzania uwierzytelnianiem"""
    
    def __init__(self, cloud_handler):
        self.cloud_handler = cloud_handler
        self._ensure_users_table()
    
    def _ensure_users_table(self):
        """Tworzy tabelę Users jeśli nie istnieje"""
        if not self.cloud_handler.azure_sql_enabled:
            print("[!] Azure SQL niedostępny - system uwierzytelniania wyłączony")
            return
        
        try:
            create_table_query = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
            BEGIN
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
                
                -- Utworzenie indeksu dla szybkiego wyszukiwania
                CREATE INDEX idx_username ON Users(username);
            END
            """
            
            self.cloud_handler.azure_sql_cursor.execute(create_table_query)
            self.cloud_handler.azure_sql_connection.commit()
            print("[+] Tabela Users gotowa w Azure SQL")
            
        except Exception as e:
            print(f"[-] Błąd tworzenia tabeli Users: {e}")
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple:
        """Hashuje hasło z solą"""
        if not salt:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return password_hash, salt
    
    def create_user(self, username: str, password: str, role: str = 'user', email: str = None) -> bool:
        """Tworzy nowego użytkownika"""
        if not self.cloud_handler.azure_sql_enabled:
            return False
        
        try:
            check_query = "SELECT user_id FROM Users WHERE username = ?"
            self.cloud_handler.azure_sql_cursor.execute(check_query, (username,))
            if self.cloud_handler.azure_sql_cursor.fetchone():
                print(f"[-] Użytkownik '{username}' już istnieje")
                return False
            
            password_hash, salt = self.hash_password(password)
            
            insert_query = """
                INSERT INTO Users (username, password_hash, salt, role, email)
                VALUES (?, ?, ?, ?, ?)
            """
            self.cloud_handler.azure_sql_cursor.execute(
                insert_query,
                (username, password_hash, salt, role, email)
            )
            self.cloud_handler.azure_sql_connection.commit()
            print(f"[+] Utworzono użytkownika: {username} ({role})")
            return True
            
        except Exception as e:
            print(f"[-] Błąd tworzenia użytkownika: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Uwierzytelnia użytkownika"""
        if not self.cloud_handler.azure_sql_enabled:
            return None
        
        try:
            query = """
                SELECT user_id, username, password_hash, salt, role, email, is_active
                FROM Users
                WHERE username = ?
            """
            self.cloud_handler.azure_sql_cursor.execute(query, (username,))
            row = self.cloud_handler.azure_sql_cursor.fetchone()
            
            if not row:
                return None
            
            user_id, db_username, db_hash, salt, role, email, is_active = row
            
            if not is_active:
                print(f"[-] Konto '{username}' jest nieaktywne")
                return None
            
            password_hash, _ = self.hash_password(password, salt)
            
            if password_hash == db_hash:
                update_query = "UPDATE Users SET last_login = GETDATE() WHERE user_id = ?"
                self.cloud_handler.azure_sql_cursor.execute(update_query, (user_id,))
                self.cloud_handler.azure_sql_connection.commit()
                
                print(f"[+] Użytkownik '{username}' zalogowany")
                return User(user_id, db_username, role, email)
            
            return None
            
        except Exception as e:
            print(f"[-] Błąd uwierzytelniania: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Pobiera użytkownika po ID"""
        if not self.cloud_handler.azure_sql_enabled:
            return None
        
        try:
            query = """
                SELECT user_id, username, role, email
                FROM Users
                WHERE user_id = ? AND is_active = 1
            """
            self.cloud_handler.azure_sql_cursor.execute(query, (user_id,))
            row = self.cloud_handler.azure_sql_cursor.fetchone()
            
            if row:
                return User(row[0], row[1], row[2], row[3])
            return None
            
        except Exception as e:
            print(f"[-] Błąd pobierania użytkownika: {e}")
            return None
    
    def get_all_users(self) -> list:
        """Pobiera listę wszystkich użytkowników"""
        if not self.cloud_handler.azure_sql_enabled:
            return []
        
        try:
            query = """
                SELECT user_id, username, role, email, created_at, last_login, is_active
                FROM Users
                ORDER BY created_at DESC
            """
            self.cloud_handler.azure_sql_cursor.execute(query)
            rows = self.cloud_handler.azure_sql_cursor.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'role': row[2],
                    'email': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'last_login': row[5].isoformat() if row[5] else None,
                    'is_active': row[6]
                })
            
            return users
            
        except Exception as e:
            print(f"[-] Błąd pobierania użytkowników: {e}")
            return []
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Zmienia hasło użytkownika"""
        if not self.cloud_handler.azure_sql_enabled:
            return False
        
        try:
            password_hash, salt = self.hash_password(new_password)
            
            update_query = """
                UPDATE Users
                SET password_hash = ?, salt = ?
                WHERE username = ?
            """
            self.cloud_handler.azure_sql_cursor.execute(
                update_query,
                (password_hash, salt, username)
            )
            self.cloud_handler.azure_sql_connection.commit()
            print(f"[+] Hasło zmienione dla użytkownika: {username}")
            return True
            
        except Exception as e:
            print(f"[-] Błąd zmiany hasła: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """Usuwa użytkownika (ustawia is_active = 0)"""
        if not self.cloud_handler.azure_sql_enabled:
            return False
        
        try:
            update_query = "UPDATE Users SET is_active = 0 WHERE username = ?"
            self.cloud_handler.azure_sql_cursor.execute(update_query, (username,))
            self.cloud_handler.azure_sql_connection.commit()
            print(f"[+] Użytkownik '{username}' dezaktywowany")
            return True
            
        except Exception as e:
            print(f"[-] Błąd usuwania użytkownika: {e}")
            return False


