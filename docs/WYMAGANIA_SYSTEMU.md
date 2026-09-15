# Specyfikacja Wymagań Systemu GlobalVista Analytics

**Data:** 4 stycznia 2026  
**Wersja:** 1.1  
**Projekt:** System Monitorowania i Analizy Sprzedaży oraz Danych Bankowych  
**Autor:** Damian Dawidek

---

## Spis treści

1. [Wprowadzenie](#1-wprowadzenie)
2. [Zakres systemu](#2-zakres-systemu)
3. [Architektura wysokiego poziomu](#3-architektura-wysokiego-poziomu)
4. [Wymagania funkcjonalne](#4-wymagania-funkcjonalne)
5. [Wymagania niefunkcjonalne](#5-wymagania-niefunkcjonalne)
6. [Ograniczenia i założenia](#6-ograniczenia-i-założenia)

---

## 1. Wprowadzenie

### 1.1 Cel dokumentu

Dokument ten stanowi kompleksową specyfikację wymagań dla systemu GlobalVista Analytics - zaawansowanej platformy analitycznej zaprojektowanej dla fikcyjnej globalnej korporacji działającej w sektorze e-commerce i bankowości. Celem jest precyzyjne zdefiniowanie funkcjonalności systemu oraz parametrów wydajnościowych, bezpieczeństwa i użyteczności.

### 1.2 Zakres projektu

GlobalVista Analytics to wielowarstwowy system informatyczny obejmujący:
- **Generowanie i walidację** syntetycznych danych biznesowych
- **Hybrydowe przechowywanie danych** (SQL/NoSQL, on-premise/cloud)
- **Interfejs webowy** do zarządzania i wizualizacji danych
- **System uwierzytelniania** z kontrolą dostępu opartą na rolach
- **Integrację z ekosystemem Microsoft Azure** (Azure SQL, Cosmos DB)
- **Mechanizmy ETL** i synchronizacji danych

### 1.3 Definicje i akronimy

| Akronim | Znaczenie |
|---------|-----------|
| **ETL** | Extract, Transform, Load - proces pobierania, transformacji i ładowania danych |
| **CRUD** | Create, Read, Update, Delete - podstawowe operacje na danych |
| **RBAC** | Role-Based Access Control - kontrola dostępu oparta na rolach |
| **KPI** | Key Performance Indicator - kluczowy wskaźnik wydajności |
| **API** | Application Programming Interface - interfejs programowania aplikacji |
| **ODBC** | Open Database Connectivity - standard dostępu do baz danych |
| **PBKDF2** | Password-Based Key Derivation Function 2 - funkcja do bezpiecznego hashowania haseł |

### 1.4 Interesariusze

- **Administratorzy systemu** - zarządzanie użytkownikami, generowanie danych, synchronizacja
- **Analitycy biznesowi** - dostęp do dashboardów, analiza KPI, generowanie raportów
- **Zwykli użytkownicy** - odczyt i podstawowa manipulacja danymi
- **Goście** - ograniczony dostęp tylko do odczytu

---

## 2. Zakres systemu

### 2.1 Funkcje w zakresie

✅ **Moduł uwierzytelniania i autoryzacji**
- Logowanie/wylogowanie użytkowników
- Rejestracja nowych użytkowników z weryfikacją
- Zarządzanie rolami (admin, user, guest)
- System uprawnień dla poszczególnych operacji

✅ **Moduł generowania danych**
- Generowanie syntetycznych danych sprzedażowych (klienci, produkty, zamówienia)
- Generowanie danych bankowych (konta, transakcje)
- Obsługa 24 lokalizacji geograficznych z odpowiednimi walutami
- Generowanie do 500,000 rekordów jednorazowo

✅ **Moduł walidacji i oczyszczania danych**
- Walidacja formatów (email, telefon, IBAN)
- Detekcja i usuwanie duplikatów
- Imputacja brakujących wartości
- Sanityzacja danych wejściowych (ochrona przed SQL Injection, XSS)

✅ **Moduł baz danych lokalnych**
- SQL Server - 13 tabel relacyjnych
- MongoDB - 4 kolekcje NoSQL
- Operacje CRUD na wszystkich encjach
- Transakcje ACID w SQL Server

✅ **Moduł integracji chmurowej**
- Synchronizacja z Azure SQL Database
- Synchronizacja z Azure Cosmos DB
- Automatyczna obsługa błędów połączenia

✅ **Panel administracyjny webowy**
- Dashboard z wizualizacją KPI
- Formularze do zarządzania danymi
- Interfejs generowania i ładowania danych
- Panel zarządzania użytkownikami

✅ **API RESTful**
- Endpointy dla wszystkich operacji CRUD
- JSON jako format wymiany danych
- Obsługa błędów z kodami HTTP

### 2.2 Funkcje poza zakresem

❌ Moduł Power BI (wykorzystywany jako zewnętrzne narzędzie)  
❌ Mobilna aplikacja natywna  
❌ Integracja z rzeczywistymi systemami bankowymi  
❌ Przetwarzanie płatności rzeczywistych  
❌ Wsparcie dla innych platform chmurowych (AWS, GCP)

---

## 3. Architektura wysokiego poziomu

### 3.1 Warstwy systemu

```
┌─────────────────────────────────────────────────────────┐
│           WARSTWA PREZENTACJI                            │
│  (HTML5, CSS3, JavaScript, Flask Templates)             │
└─────────────────────────────────────────────────────────┘
                          ↓↑
┌─────────────────────────────────────────────────────────┐
│           WARSTWA APLIKACJI                              │
│  (Flask Framework, Flask-Login, RESTful API)            │
└─────────────────────────────────────────────────────────┘
                          ↓↑
┌─────────────────────────────────────────────────────────┐
│           WARSTWA LOGIKI BIZNESOWEJ                      │
│  (Generatory danych, Walidatory, ETL, Handlery)        │
├──────────────────────┴──────────────────────────────────┘
                          ↓↑
┌──────────────────────┬──────────────────────────────────┐
│   WARSTWA DANYCH     │    WARSTWA CHMUROWA              │
│   LOKALNYCH          │    (Microsoft Azure)             │
│                      │                                  │
│  • SQL Server        │    • Azure SQL Database          │
│  • MongoDB           │    • Azure Cosmos DB             │
└──────────────────────┴──────────────────────────────────┘
```

### 3.2 Technologie kluczowe

**Backend:**
- Python 3.x
- Flask 2.x
- Flask-Login
- pyodbc (SQL Server)
- pymongo (MongoDB)
- pandas (manipulacja danych)
- Faker (generowanie danych)

**Frontend:**
- HTML5, CSS3
- JavaScript (ES6+)
- Tailwind CSS

**Bazy danych:**
- Microsoft SQL Server (lokalnie)
- MongoDB 4.x+ (lokalnie)
- Azure SQL Database (chmura)
- Azure Cosmos DB - MongoDB API (chmura)

---

## 4. Wymagania funkcjonalne

