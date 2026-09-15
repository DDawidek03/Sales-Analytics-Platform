import requests
import json

try:
    print("[*] Testowanie endpoint /api/sql/stats...")
    response = requests.get('http://127.0.0.1:5000/api/sql/stats')
    print(f"[*] Status code: {response.status_code}")
    print(f"[*] Headers: {response.headers.get('Content-Type')}")
    print(f"[*] Raw response: {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[+] Response type: {type(data)}")
        print(f"[+] Response data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"[-] Błąd: {response.status_code}")
        
except Exception as e:
    print(f"[-] Exception: {e}")
    import traceback
    traceback.print_exc()
