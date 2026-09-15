import pyodbc

server = 'localhost'
database = 'SalesDB'

print("Dostępne sterowniki ODBC:")
drivers = [driver for driver in pyodbc.drivers()]
for driver in drivers:
    print(f"  - {driver}")

if 'ODBC Driver 17 for SQL Server' in drivers:
    driver = 'ODBC Driver 17 for SQL Server'
elif 'ODBC Driver 13 for SQL Server' in drivers:
    driver = 'ODBC Driver 13 for SQL Server'
elif 'ODBC Driver 11 for SQL Server' in drivers:
    driver = 'ODBC Driver 11 for SQL Server'
else:
    driver = 'SQL Server'

print(f"\nUżywam sterownika: {driver}\n")

connection_string = (
    f'DRIVER={{{driver}}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
)

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    print("Połączenie z bazą danych powiodło się!")

    cursor.execute("SELECT @@VERSION")
    row = cursor.fetchone()
    print("Wersja SQL Server:", row[0])

    print("\nTabele w bazie danych:")
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    tables = cursor.fetchall()
    if not tables:
        print("Brak tabel w bazie danych.")
    else:
        for table in tables:
            print(table[0])

except Exception as e:
    print(f"Błąd podczas połączenia z bazą danych: {e}")

finally:
    if 'connection' in locals():
        cursor.close()
        connection.close()
        print("Połączenie z bazą danych zostało zamknięte.")