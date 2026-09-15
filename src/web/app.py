from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import json
import time
import datetime
from functools import wraps
import threading
from database_handler import db_handler, init_database, close_database
from cloud_handler import cloud_handler, init_cloud_connections, close_cloud_connections, sync_to_cloud
import auth_handler as auth_module
from auth_handler import AuthHandler, User

app = Flask(__name__, static_folder='.')
app.template_folder = '.'
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32).hex())

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Musisz się zalogować, aby uzyskać dostęp do tej strony.'

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_files')

@login_manager.user_loader
def load_user(user_id):
    if auth_module.auth_handler:
        return auth_module.auth_handler.get_user_by_id(int(user_id))
    return None

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                return jsonify({
                    'success': False,
                    'message': 'Brak uprawnień do wykonania tej operacji'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/admin')
@permission_required('admin_panel')
def admin_panel():
    return send_from_directory('.', 'admin.html')

@app.route('/login')
def login():
    return send_from_directory('.', 'login.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Podaj nazwę użytkownika i hasło'
            }), 400
        
        if not auth_module.auth_handler:
            return jsonify({
                'success': False,
                'message': 'System uwierzytelniania niedostępny'
            }), 503
        
        user = auth_module.auth_handler.authenticate(username, password)
        
        if user:
            login_user(user, remember=data.get('remember', False))
            return jsonify({
                'success': True,
                'message': 'Zalogowano pomyślnie',
                'user': {
                    'username': user.username,
                    'role': user.role
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nieprawidłowa nazwa użytkownika lub hasło'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Wylogowano pomyślnie'
    })

@app.route('/api/auth/current-user', methods=['GET'])
def api_current_user():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'username': current_user.username,
                'role': current_user.role,
                'email': current_user.email
            }
        })
    else:
        return jsonify({
            'authenticated': False
        })

@app.route('/api/auth/register', methods=['POST'])
def api_register_user():
    try:
        if not auth_module.auth_handler:
            return jsonify({
                'success': False,
                'message': 'System uwierzytelniania niedostępny'
            }), 503
        
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip() or None
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Nazwa użytkownika i hasło są wymagane'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Nazwa użytkownika musi mieć co najmniej 3 znaki'
            }), 400
        
        if len(password) < 4:
            return jsonify({
                'success': False,
                'message': 'Hasło musi mieć co najmniej 4 znaki'
            }), 400
        
        # Twórz użytkownika z rolą 'user'
        success = auth_module.auth_handler.create_user(username, password, 'user', email)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Użytkownik {username} został utworzony pomyślnie!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nie udało się utworzyć użytkownika. Nazwa może być już zajęta.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/auth/register-admin', methods=['POST'])
def api_register_admin():
    """Rejestracja administratora z weryfikacją istniejącego admina"""
    try:
        if not auth_module.auth_handler:
            return jsonify({
                'success': False,
                'message': 'System uwierzytelniania niedostępny'
            }), 503
        
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip() or None
        admin_username = data.get('admin_username', '').strip()
        admin_password = data.get('admin_password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Nazwa użytkownika i hasło są wymagane'
            }), 400
        
        if not admin_username or not admin_password:
            return jsonify({
                'success': False,
                'message': 'Weryfikacja administratora wymagana - podaj login i hasło istniejącego admina'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Nazwa użytkownika musi mieć co najmniej 3 znaki'
            }), 400
        
        if len(password) < 4:
            return jsonify({
                'success': False,
                'message': 'Hasło musi mieć co najmniej 4 znaki'
            }), 400
        
        # Weryfikuj dane administratora
        admin_user = auth_module.auth_handler.authenticate(admin_username, admin_password)
        
        if not admin_user:
            return jsonify({
                'success': False,
                'message': 'Weryfikacja nieudana - nieprawidłowe dane administratora'
            }), 401
        
        if admin_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Weryfikacja nieudana - podany użytkownik nie jest administratorem'
            }), 403
        
        success = auth_module.auth_handler.create_user(username, password, 'admin', email)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Administrator {username} został utworzony pomyślnie!'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nie udało się utworzyć administratora. Nazwa może być już zajęta.'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# === Zarządzanie użytkownikami (tylko dla adminów) ===

@app.route('/api/auth/users', methods=['GET'])
@permission_required('admin_panel')
def api_get_users():
    try:
        if not auth_module.auth_handler:
            return jsonify({
                'success': False,
                'message': 'System uwierzytelniania niedostępny'
            }), 503
        
        users = auth_module.auth_handler.get_all_users()
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/auth/users/create', methods=['POST'])
@permission_required('admin_panel')
def api_create_user():
    try:
        if not auth_module.auth_handler:
            return jsonify({
                'success': False,
                'message': 'System uwierzytelniania niedostępny'
            }), 503
        
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'user').strip()
        email = data.get('email', '').strip() or None
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Nazwa użytkownika i hasło są wymagane'
            }), 400
        
        if len(password) < 4:
            return jsonify({
                'success': False,
                'message': 'Hasło musi mieć co najmniej 4 znaki'
            }), 400
        
        if role not in ['admin', 'user', 'guest']:
            return jsonify({
                'success': False,
                'message': 'Nieprawidłowa rola. Dostępne: admin, user, guest'
            }), 400
        
        success = auth_module.auth_handler.create_user(username, password, role, email)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Użytkownik "{username}" został utworzony'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nie udało się utworzyć użytkownika (może już istnieje)'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/auth/users/<username>/change-password', methods=['POST'])
@permission_required('admin_panel')
def api_change_user_password(username):
    try:
        if not auth_module.auth_handler:
            return jsonify({
                'success': False,
                'message': 'System uwierzytelniania niedostępny'
            }), 503
        
        data = request.get_json()
        new_password = data.get('new_password', '').strip()
        
        if not new_password or len(new_password) < 4:
            return jsonify({
                'success': False,
                'message': 'Hasło musi mieć co najmniej 4 znaki'
            }), 400
        
        success = auth_module.auth_handler.change_password(username, new_password)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Hasło użytkownika "{username}" zostało zmienione'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nie udało się zmienić hasła'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/auth/users/<username>', methods=['DELETE'])
@permission_required('admin_panel')
def api_delete_user(username):
    try:
        if not auth_module.auth_handler:
            return jsonify({
                'success': False,
                'message': 'System uwierzytelniania niedostępny'
            }), 503
        
        if username == current_user.username:
            return jsonify({
                'success': False,
                'message': 'Nie możesz usunąć samego siebie'
            }), 400
        
        success = auth_module.auth_handler.delete_user(username)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Użytkownik "{username}" został dezaktywowany'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Nie udało się usunąć użytkownika'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# === API Admin (chronione) ===

@app.route('/api/admin/generate-sql', methods=['POST'])
@permission_required('generate')
def generate_sql_data():
    try:
        import subprocess
        import sys
        data = request.get_json()
        counts = data or {}
        
        print(f"[+] Generating SQL data with {counts.get('records', 1000)} records...")
        
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'generate_sales_data.py')
        
        print(f"[+] Python: {python_exe}")
        print(f"[+] Script: {script_path}")
        
        orders_count = counts.get('records', 1000)
        cmd = [python_exe, script_path, '--orders', str(orders_count)]
        print(f"[+] Command: {' '.join(cmd)}")
        
        print("[+] Uruchamianie generatora...")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        output_lines = []
        for line in process.stdout:
            print(line.rstrip())
            output_lines.append(line)
        
        return_code = process.wait(timeout=1800)
        
        print(f"[+] Return code: {return_code}")
        
        if return_code == 0:
            return jsonify({
                'success': True,
                'message': 'Dane SQL zostały wygenerowane pomyślnie',
                'filename': 'sales_data.sql',
                'output': ''.join(output_lines[-50:])
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Błąd podczas generowania danych SQL',
                'error': ''.join(output_lines[-20:])
            }), 500
            
    except Exception as e:
        print(f"[!] Exception in generate_sql_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/load-sql', methods=['POST'])
@permission_required('generate')
def load_sql_data():
    try:
        import subprocess
        import sys
        
        print("[+] Loading SQL data to database...")
        
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'load_data_to_db.py')
        
        print(f"[+] Python: {python_exe}")
        print(f"[+] Script: {script_path}")
        
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"[+] Return code: {result.returncode}")
        print(f"[+] STDOUT: {result.stdout[:500]}..." if len(result.stdout) > 500 else f"[+] STDOUT: {result.stdout}")
        if result.stderr:
            print(f"[!] STDERR: {result.stderr}")
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Dane SQL zostały załadowane do bazy pomyślnie',
                'records_loaded': 'Zobacz output konsoli',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Błąd podczas ładowania danych SQL',
                'error': result.stderr or result.stdout
            }), 500
            
    except Exception as e:
        print(f"[!] Exception in load_sql_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/generate-mongo', methods=['POST'])
def generate_mongo_data():
    try:
        import subprocess
        import sys
        data = request.get_json()
        counts = data or {}
        
        print(f"[+] Generating MongoDB data with {counts.get('records', 1000)} records...")
        
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'generate_nosql_data.py')
        
        print(f"[+] Python: {python_exe}")
        print(f"[+] Script: {script_path}")
        
        print("[+] Uruchamianie generatora NoSQL...")
        
        process = subprocess.Popen(
            [python_exe, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        output_lines = []
        for line in process.stdout:
            print(line.rstrip())
            output_lines.append(line)
        
        return_code = process.wait(timeout=1800)
        
        print(f"[+] Return code: {return_code}")
        
        if return_code == 0:
            return jsonify({
                'success': True,
                'message': 'Dane MongoDB zostały wygenerowane pomyślnie',
                'filename': 'nosql_data.json',
                'output': ''.join(output_lines[-50:])
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Błąd podczas generowania danych MongoDB',
                'error': ''.join(output_lines[-20:])
            }), 500
            
    except Exception as e:
        print(f"[!] Exception in generate_mongo_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/load-mongo', methods=['POST'])
def load_mongo_data():
    try:
        import subprocess
        import sys
        
        print("[+] Loading MongoDB data to database...")
        
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'load_json_to_mongodb.py')
        
        print(f"[+] Python: {python_exe}")
        print(f"[+] Script: {script_path}")
        
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"[+] Return code: {result.returncode}")
        print(f"[+] STDOUT: {result.stdout[:500]}..." if len(result.stdout) > 500 else f"[+] STDOUT: {result.stdout}")
        if result.stderr:
            print(f"[!] STDERR: {result.stderr}")
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Dane MongoDB zostały załadowane do bazy pomyślnie',
                'documents_loaded': 'Zobacz output konsoli',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Błąd podczas ładowania danych MongoDB',
                'error': result.stderr or result.stdout
            }), 500
            
    except Exception as e:
        print(f"[!] Exception in load_mongo_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/<db_type>/<path:resource_path>', methods=['GET', 'POST'])
def handle_api_request(db_type, resource_path):
    if request.method == 'POST':
        data = request.get_json()
        print(f"\n=== Received: {db_type}/{resource_path} ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if db_type == 'sql':
            new_id = save_to_database(resource_path, data)
            
            if new_id:
                response_data = {
                    "success": True,
                    "message": f"Dane dla {resource_path} zostały zapisane w bazie SQL",
                    "id": new_id,
                    "data": data,
                    "database_type": db_type,
                    "timestamp": time.time(),
                }
            else:
                response_data = {
                    "success": False,
                    "message": f"Błąd podczas zapisywania danych do bazy SQL",
                    "database_type": db_type,
                    "timestamp": time.time(),
                }
        elif db_type == 'mongo':
            success = save_to_mongo(resource_path, data)
            
            if success:
                response_data = {
                    "success": True,
                    "message": f"Dane dla {resource_path} zostały zapisane w MongoDB",
                    "database_type": db_type,
                    "timestamp": time.time(),
                }
            else:
                response_data = {
                    "success": False,
                    "message": f"Błąd podczas zapisywania danych do MongoDB",
                    "database_type": db_type,
                    "timestamp": time.time(),
                }
        else:
            response_data = {
                "success": False,
                "message": f"Nieobsługiwany typ bazy danych: {db_type}",
                "database_type": db_type,
                "timestamp": time.time(),
            }
        
        time.sleep(0.5)
        return jsonify(response_data)
    
    else:
        params = {}
        if request.args.get('limit'):
            params['limit'] = int(request.args.get('limit'))
        if request.args.get('type'):
            params['transaction_type'] = request.args.get('type')
        if request.args.get('currency'):
            params['currency'] = request.args.get('currency')
        
        if db_type in ['sql', 'mongo']:
            data = load_from_database(resource_path, db_type, params if params else None)
            if data is not None:
                return jsonify(data)
        
        try:
            data = load_data_from_file(db_type, resource_path)
            return jsonify(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return jsonify([
                {"id": 1, "name": "Przykładowy element 1", "type": resource_path},
                {"id": 2, "name": "Przykładowy element 2", "type": resource_path}
            ])


def save_to_database(resource_path: str, data: dict) -> int:
    try:
        new_id = db_handler.insert_generic(resource_path, data)
        if new_id:
            print(f"Zapisano do bazy SQL: {resource_path} (ID: {new_id})")
            # Synchronizacja tylko przez przycisk w admin panelu
        return new_id
    except Exception as e:
        print(f"Błąd zapisu do bazy SQL: {e}")
        return None


def save_to_mongo(resource_path: str, data: dict) -> bool:
    try:
        mongo_handlers = {
            'purchase': db_handler.insert_mongo_purchase_history,
            'behavior': db_handler.insert_mongo_customer_behavior,
            'profiles': db_handler.insert_mongo_seller_profile,
        }
        
        handler = mongo_handlers.get(resource_path.lower())
        if handler:
            success = handler(data)
            # Synchronizacja tylko przez przycisk w admin panelu
            return success
        else:
            print(f"Brak handlera MongoDB dla: {resource_path}")
            return False
            
    except Exception as e:
        print(f"Błąd zapisu do MongoDB: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_from_database(resource_path: str, db_type: str = 'sql', params: dict = None) -> list:
    try:
        if db_type == 'mongo':
            print(f"[*] MongoDB GET request for: {resource_path}")
            print(f"[*] Parameters: {params}")
            
            mongo_getters = {
                'transactions': db_handler.get_mongo_transactions,
                'transaction-stats': db_handler.get_mongo_transaction_stats,
            }
            
            getter = mongo_getters.get(resource_path.lower())
            if getter:
                if params:
                    print(f"[*] Calling getter with params: {params}")
                    result = getter(**params)
                else:
                    print(f"[*] Calling getter without params")
                    result = getter()
                
                print(f"[+] MongoDB query returned {len(result) if isinstance(result, list) else 1} items")
                return result if isinstance(result, list) else [result]
            else:
                print(f"[-] No getter found for MongoDB resource: {resource_path}")
            
            return None
        
        resource_getters = {
            'customers': db_handler.get_customers,
            'sellers': db_handler.get_sellers,
            'categories': db_handler.get_categories,
            'countries': db_handler.get_countries,
            'regions': db_handler.get_regions,
            'products': db_handler.get_products,
            'orders': db_handler.get_orders,
            'banking/accounts': db_handler.get_bank_accounts,
            'bankaccounts': db_handler.get_bank_accounts,
            'stats': db_handler.get_stats,
        }
        
        getter = resource_getters.get(resource_path.lower())
        if getter:
            result = getter()
            
            if resource_path.lower() == 'stats' and isinstance(result, dict):
                print(f"[+] Zwracam statystyki jako dict: {result}")
                return result
            
            if result and len(result) > 0:
                if isinstance(result[0], dict):
                    print(f"[+] Zwracam {len(result)} rekordów jako dict dla {resource_path}")
                    return result
                if db_handler.cursor and db_handler.cursor.description:
                    columns = [column[0] for column in db_handler.cursor.description]
                    records = []
                    for row in result:
                        record = {}
                        for col, value in zip(columns, row):
                            if hasattr(value, 'isoformat'):
                                record[col] = value.isoformat()
                            else:
                                record[col] = value
                        records.append(record)
                    print(f"[+] Zwracam {len(records)} rekordów (skonwertowanych z tuple) dla {resource_path}")
                    return records
                else:
                    print(f"[-] Brak cursor.description dla {resource_path}")
            elif result is not None and len(result) == 0:
                print(f"[+] Zwracam pustą listę dla {resource_path}")
                return []
            
            print(f"[-] Brak danych dla {resource_path}")
            return []
        
        print(f"[-] Brak gettera dla {resource_path}")
        return None
    except Exception as e:
        print(f"[-] Błąd odczytu z bazy: {e}")
        import traceback
        traceback.print_exc()
        return None


def prepare_data_for_database(db_type, resource_path, data):
    processed_data = data.copy()
    
    semantic_keys = {}
    keys_to_remove = []
    
    for key, value in processed_data.items():
        if key.startswith('np.'):
            keys_to_remove.append(key)
            field_type = key.replace('np.', '').strip()
            if 'Jan' in field_type:
                semantic_keys['firstName'] = value
            elif 'Kowalski' in field_type:
                semantic_keys['lastName'] = value
            elif '@example' in field_type:
                semantic_keys['email'] = value
            elif '+48' in field_type:
                semantic_keys['phone'] = value
            elif 'ul.' in field_type:
                semantic_keys['address'] = value
            elif 'Laptop' in field_type:
                semantic_keys['productName'] = value
            else:
                semantic_keys[key] = value
    
    for key in keys_to_remove:
        if key in processed_data:
            del processed_data[key]
    
    processed_data.update(semantic_keys)
    
    processed_data['timestamp'] = time.time()
    processed_data['resource_type'] = resource_path
    processed_data['source'] = 'web_dashboard'
    
    if db_type == 'sql':
        for key, value in processed_data.items():
            if key.endswith('_id') or key.endswith('Id'):
                try:
                    processed_data[key] = int(value) if value else None
                except ValueError:
                    pass
    
    elif db_type == 'mongo':
        processed_data['metadata'] = {
            'created_at': time.time(),
            'version': '1.0',
            'resource_path': resource_path
        }
    
    return processed_data


def save_data_to_file(db_type, resource_path, data):
    db_dir = os.path.join(DATA_DIR, db_type)
    os.makedirs(db_dir, exist_ok=True)
    
    safe_resource_path = resource_path.replace('/', '_')
    resource_dir = os.path.join(db_dir, safe_resource_path)
    os.makedirs(resource_dir, exist_ok=True)
    
    table_name = resource_path.split('/')[-1]
    safe_table_name = ''.join(c if c.isalnum() or c in '_-' else '_' for c in table_name)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{safe_table_name}_{timestamp}.json"
    file_path = os.path.join(resource_dir, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    latest_file = os.path.join(resource_dir, f"{safe_table_name}_latest.json")
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    all_file = os.path.join(resource_dir, f"{safe_table_name}_all_records.json")
    
    all_data = []
    try:
        if os.path.exists(all_file):
            with open(all_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
    except json.JSONDecodeError:
        all_data = []
    
    all_data.append(data)
    with open(all_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    return os.path.join('data_files', db_type, safe_resource_path, file_name)


def load_data_from_file(db_type, resource_path):
    safe_resource_path = resource_path.replace('/', '_')
    resource_dir = os.path.join(DATA_DIR, db_type, safe_resource_path)
    
    table_name = resource_path.split('/')[-1]
    safe_table_name = ''.join(c if c.isalnum() or c in '_-' else '_' for c in table_name)
    
    all_file = os.path.join(resource_dir, f"{safe_table_name}_all_records.json")
    
    if os.path.exists(all_file):
        with open(all_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    raise FileNotFoundError(f"Brak danych dla {db_type}/{resource_path}")


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Nie znaleziono zasobu"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Błąd wewnętrzny serwera"}), 500

@app.route('/api/azure/sql/status', methods=['GET'])
def azure_sql_status():
    """Sprawdź status tabel w Azure SQL Database"""
    try:
        if not cloud_handler.azure_sql_enabled:
            return jsonify({
                'success': False,
                'connected': False,
                'message': 'Azure SQL nie jest połączone'
            })
        
        tables = [
            'Countries', 'DateDimension', 'Categories', 'Regions',
            'Sellers', 'Products', 'Customers', 'BankAccounts',
            'BankTransactions', 'Orders', 'OrderDetails', 'Promotions'
        ]
        
        table_status = {}
        total_records = 0
        populated_count = 0
        
        for table in tables:
            try:
                query = f"SELECT COUNT(*) FROM {table}"
                cloud_handler.azure_sql_cursor.execute(query)
                count = cloud_handler.azure_sql_cursor.fetchone()[0]
                table_status[table] = count
                total_records += count
                if count > 0:
                    populated_count += 1
            except Exception as e:
                table_status[table] = -1
        
        return jsonify({
            'success': True,
            'connected': True,
            'tables': table_status,
            'total_tables': len(tables),
            'total_records': total_records,
            'populated_tables': populated_count,
            'empty_tables': len(tables) - populated_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'connected': False,
            'message': str(e)
        }), 500

@app.route('/api/azure/cosmos/status', methods=['GET'])
def azure_cosmos_status():
    """Sprawdź status kolekcji w Azure Cosmos DB"""
    try:
        if not cloud_handler.cosmos_enabled:
            return jsonify({
                'success': False,
                'connected': False,
                'message': 'Cosmos DB nie jest połączone'
            })
        
        collections = {
            'PurchaseHistories': 0,
            'CustomerBehavior': 0,
            'SellerProfiles': 0,
            'BankTransactionLogs': 0
        }
        
        total_documents = 0
        
        for collection_name in collections.keys():
            try:
                container = cloud_handler.cosmos_db.get_container_client(collection_name)
                query = "SELECT VALUE COUNT(1) FROM c"
                items = list(container.query_items(query=query, enable_cross_partition_query=True))
                count = items[0] if items else 0
                collections[collection_name] = count
                total_documents += count
            except Exception as e:
                collections[collection_name] = -1
        
        return jsonify({
            'success': True,
            'connected': True,
            'collections': collections,
            'total_documents': total_documents
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'connected': False,
            'message': str(e)
        }), 500

@app.route('/api/azure/sql/sync', methods=['POST'])
def sync_to_azure_sql_bulk():
    """Synchronizuj dane z lokalnego SQL Server do Azure SQL"""
    try:
        data = request.get_json()
        tables = data.get('tables', [])
        
        if not cloud_handler.azure_sql_enabled:
            return jsonify({
                'success': False,
                'message': 'Azure SQL nie jest połączone'
            }), 400
        
        if not db_handler.connection:
            return jsonify({
                'success': False,
                'message': 'Lokalna baza SQL nie jest połączona'
            }), 400
        
        results = {}
        
        for table in tables:
            try:
                query = f"SELECT * FROM {table}"
                db_handler.cursor.execute(query)
                columns = [column[0] for column in db_handler.cursor.description]
                rows = db_handler.cursor.fetchall()
                
                inserted = 0
                errors = 0
                
                for row in rows:
                    try:
                        data_dict = dict(zip(columns, row))
                        result = cloud_handler.sync_to_azure_sql(table.lower(), data_dict)
                        if result:
                            inserted += 1
                        else:
                            errors += 1
                    except Exception as e:
                        errors += 1
                
                results[table] = {
                    'total': len(rows),
                    'inserted': inserted,
                    'errors': errors
                }
                
            except Exception as e:
                results[table] = {
                    'error': str(e)
                }
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/azure/cosmos/sync', methods=['POST'])
def sync_to_cosmos_bulk():
    """Synchronizuj dane z MongoDB do Cosmos DB"""
    try:
        data = request.get_json()
        collections = data.get('collections', [])
        
        if not cloud_handler.cosmos_enabled:
            return jsonify({
                'success': False,
                'message': 'Cosmos DB nie jest połączone'
            }), 400
        
        if not db_handler.mongo_db:
            return jsonify({
                'success': False,
                'message': 'Lokalny MongoDB nie jest połączony'
            }), 400
        
        results = {}
        
        for collection in collections:
            try:
                mongo_collection = db_handler.mongo_db[collection]
                documents = list(mongo_collection.find())
                
                inserted = 0
                errors = 0
                
                for doc in documents:
                    try:
                        if '_id' in doc:
                            del doc['_id']
                        
                        result = cloud_handler.sync_to_cosmos_db(collection.lower(), doc)
                        if result:
                            inserted += 1
                        else:
                            errors += 1
                    except Exception as e:
                        errors += 1
                
                results[collection] = {
                    'total': len(documents),
                    'inserted': inserted,
                    'errors': errors
                }
                
            except Exception as e:
                results[collection] = {
                    'error': str(e)
                }
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get database statistics for admin panel"""
    try:
        stats = {
            'sql_records': 0,
            'mongo_records': 0,
            'azure_sql_records': 0,
            'cosmos_records': 0,
            'sql_status': 'disconnected',
            'mongo_status': 'disconnected',
            'azure_sql_status': 'disconnected',
            'cosmos_status': 'disconnected'
        }
        
        if db_handler.connection and db_handler.cursor:
            stats['sql_status'] = 'connected'
            sql_stats = db_handler.get_stats()
            if sql_stats:
                stats['sql_records'] = sql_stats.get('total', 0)
        else:
            if db_handler.connect():
                stats['sql_status'] = 'connected'
                sql_stats = db_handler.get_stats()
                if sql_stats:
                    stats['sql_records'] = sql_stats.get('total', 0)
            
        if db_handler.mongo_client:
            try:
                db_handler.mongo_client.admin.command('ping')
                stats['mongo_status'] = 'connected'
                mongo_count = db_handler.get_mongo_document_count()
                if mongo_count is not None:
                    stats['mongo_records'] = mongo_count
            except:
                if db_handler.connect_mongo():
                    stats['mongo_status'] = 'connected'
                    mongo_count = db_handler.get_mongo_document_count()
                    if mongo_count is not None:
                        stats['mongo_records'] = mongo_count
            
        if cloud_handler:
            try:
                if hasattr(cloud_handler, 'test_azure_connection') and cloud_handler.test_azure_connection():
                    stats['azure_sql_status'] = 'connected'
                    azure_count = cloud_handler.get_azure_record_count()
                    stats['azure_sql_records'] = azure_count if azure_count else 0
            except Exception as e:
                print(f"[-] Azure SQL error: {e}")
            
            try:
                if hasattr(cloud_handler, 'test_cosmos_connection') and cloud_handler.test_cosmos_connection():
                    stats['cosmos_status'] = 'connected'
                    cosmos_count = cloud_handler.get_cosmos_document_count()
                    stats['cosmos_records'] = cosmos_count if cosmos_count else 0
            except Exception as e:
                print(f"[-] Cosmos DB error: {e}")
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'sql_records': 0,
            'mongo_records': 0,
            'azure_sql_records': 0,
            'cosmos_records': 0
        }), 500


@app.route('/api/admin/test-azure-sql', methods=['GET'])
def test_azure_sql():
    """Test Azure SQL connection"""
    try:
        if cloud_handler and hasattr(cloud_handler, 'test_azure_connection') and cloud_handler.test_azure_connection():
            return jsonify({
                'success': True,
                'message': 'Azure SQL connection successful',
                'status': 'connected'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Azure SQL connection failed',
                'status': 'disconnected'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'status': 'error'
        }), 500


@app.route('/api/admin/test-cosmos', methods=['GET'])
def test_cosmos():
    """Test Cosmos DB connection"""
    try:
        if cloud_handler and hasattr(cloud_handler, 'test_cosmos_connection') and cloud_handler.test_cosmos_connection():
            return jsonify({
                'success': True,
                'message': 'Cosmos DB connection successful',
                'status': 'connected'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Cosmos DB connection failed',
                'status': 'disconnected'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'status': 'error'
        }), 500


@app.route('/api/admin/sync-azure-sql', methods=['POST'])
@permission_required('sync')
def sync_azure_sql():
    """Sync data to Azure SQL"""
    try:
        if not cloud_handler:
            return jsonify({
                'success': False,
                'message': 'Cloud handler not initialized'
            }), 500
            
        result = cloud_handler.sync_all_to_azure_sql()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f"Synchronized {result.get('records', 0)} records to Azure SQL",
                'records': result.get('records', 0)
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Sync failed')
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/sync-cosmos', methods=['POST'])
@permission_required('sync')
def sync_cosmos():
    """Sync data to Cosmos DB"""
    try:
        if not cloud_handler:
            return jsonify({
                'success': False,
                'message': 'Cloud handler not initialized'
            }), 500
            
        result = cloud_handler.sync_all_to_cosmos()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f"Synchronized {result.get('records', 0)} records to Cosmos DB",
                'records': result.get('records', 0)
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Sync failed')
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f"Synchronized {result.get('documents', 0)} documents to Cosmos DB",
                'documents': result.get('documents', 0)
            })
        else:
            return jsonify({
                'success': False,
                'message': result.get('error', 'Sync failed')
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/admin/clear-azure-sql', methods=['POST'])
@permission_required('sync')
def clear_azure_sql():
    """Clear all data from Azure SQL"""
    try:
        if not cloud_handler:
            return jsonify({
                'success': False,
                'error': 'Cloud handler not initialized'
            }), 500
            
        result = cloud_handler.clear_azure_sql()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', 'Azure SQL wyczyszczony')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Czyszczenie nie powiodło się')
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/admin/clear-cosmos', methods=['POST'])
@permission_required('sync')
def clear_cosmos():
    """Clear all documents from Cosmos DB"""
    try:
        if not cloud_handler:
            return jsonify({
                'success': False,
                'error': 'Cloud handler not initialized'
            }), 500
            
        result = cloud_handler.clear_cosmos_db()
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', 'Cosmos DB wyczyszczony')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Czyszczenie nie powiodło się')
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



print("\n[*] Inicjalizacja połączenia z bazą danych...")
os.makedirs(DATA_DIR, exist_ok=True)
local_db_connected = init_database()
azure_sql, cosmos_db = init_cloud_connections()

# Inicjalizacja systemu uwierzytelniania
if azure_sql and cloud_handler.azure_sql_enabled:
    print("[*] Inicjalizacja systemu uwierzytelniania...")
    auth_module.auth_handler = AuthHandler(cloud_handler)
    print("[+] System uwierzytelniania gotowy")
else:
    print("[!] Azure SQL niedostępny - system uwierzytelniania wyłączony")
    print("[!] Aplikacja działa bez kontroli dostępu!")

if __name__ == '__main__':
    print("=" * 50)
    print(" GlobalVista Server")
    print("=" * 50)
    print(" Home: http://127.0.0.1:5000")
    print(" Dashboard: http://127.0.0.1:5000/dashboard")
    print(" API: /api/<db_type>/<resource>")
    print(f" Data directory: {DATA_DIR}")
    print("=" * 50)
    
    if local_db_connected:
        print("[+] Połączono z lokalną bazą danych")
    else:
        print("[-] Brak połączenia z lokalną bazą - aplikacja działa w trybie ograniczonym")
    
    if azure_sql:
        print("[+] Azure SQL Database połączony")
    if cosmos_db:
        print("[+] Azure Cosmos DB połączony")
    
    if not local_db_connected and not azure_sql and not cosmos_db:
        print("\n[!] UWAGA: Brak połączenia z jakąkolwiek bazą danych!")
        print("    Aplikacja będzie działać tylko z plikami JSON")
    
    print("=" * 50)
    print()
    print("\033[93m⚠️  OSTRZEŻENIE: To jest serwer deweloperski.\033[0m")
    print()
    
    app.run(debug=True, host='127.0.0.1', port=5000)
