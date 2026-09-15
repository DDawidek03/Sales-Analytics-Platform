# Diagramy BPMN - Dokumentacja Procesów Systemu

## Przegląd Diagramów

Ten folder zawiera diagramy BPMN 2.0 przedstawiające kluczowe procesy systemu zarządzania danymi sprzedażowymi. Wszystkie diagramy mogą być otwarte i edytowane w edytorze [bpmn.io](https://demo.bpmn.io/).

## Lista Diagramów

### 1. Główny Proces Generowania Danych
**Plik:** `01_glowny_proces_generowania_danych.bpmn`

**Opis:** Wysokopoziomowy diagram przedstawiający kompletny przepływ procesu generowania danych od wyboru typu danych (SQL/NoSQL/oba) przez walidację, aż do załadowania danych do bazy.

**Elementy kluczowe:**
- Gateway rozdzielający przepływ na SQL/NoSQL/równolegle oba
- Równoległe generowanie obu typów danych
- Walidacja wygenerowanych danych
- Wybór docelowej bazy danych
- Obsługa błędów

**Zastosowanie w pracy:** Sekcja implementacji - Ogólny przepływ systemu

---

### 2. Proces Generowania Danych SQL
**Plik:** `02_proces_generowania_sql.bpmn`

**Opis:** Szczegółowy proces generowania danych relacyjnych przy użyciu skryptu `generate_sales_data.py`.

**Elementy kluczowe:**
- Walidacja liczby rekordów wejściowych
- Inicjalizacja bibliotek (Faker, numpy, pandas)
- Sekwencyjna generacja: regiony → kraje → kategorie → produkty → sprzedawcy → klienci → konta bankowe → wymiar czasu
- Zapis do plików CSV
- Generowanie statystyk

**Zastosowanie w pracy:** Sekcja implementacji - Moduł generowania danych relacyjnych

---

### 3. Proces Generowania Danych NoSQL
**Plik:** `03_proces_generowania_nosql.bpmn`

**Opis:** Proces transformacji danych CSV do struktury NoSQL (MongoDB) przy użyciu `generate_nosql_data.py`.

**Elementy kluczowe:**
- Sprawdzenie dostępności plików CSV
- Wczytanie i walidacja relacji między danymi
- Denormalizacja i agregacja danych
- Utworzenie kolekcji: SellerProfiles, PurchaseHistories, BankTransactionLogs, CustomerBehavior
- Zapis do plików JSON

**Zastosowanie w pracy:** Sekcja implementacji - Transformacja danych do modelu NoSQL

---

### 4. Proces Ładowania Danych do Bazy
**Plik:** `04_proces_ladowania_danych.bpmn`

**Opis:** Uniwersalny proces ładowania danych do różnych typów baz danych (MySQL, SQL Server, MongoDB, CosmosDB).

**Elementy kluczowe:**
- Gateway wyboru typu bazy danych
- Różne ścieżki połączenia dla SQL i NoSQL
- Weryfikacja schematu dla SQL
- Utworzenie indeksów
- Rollback w przypadku błędu
- Raport ładowania

**Zastosowanie w pracy:** Sekcja implementacji - Integracja z bazami danych

---

### 5. Przepływ Interfejsu Webowego
**Plik:** `05_przeplyw_interfejsu_webowego.bpmn`

**Opis:** Kompletna ścieżka użytkownika przez aplikację webową Flask.

**Elementy kluczowe:**
- Wybór między panelem administracyjnym a dashboardem
- Gateway akcji administratora (generowanie SQL/NoSQL, ładowanie, sprawdzanie)
- Wywołania API endpointów
- Strumieniowanie postępu w czasie rzeczywistym
- Renderowanie wykresów i wizualizacji
- Pętla interakcji z dashboardem

**Zastosowanie w pracy:** Sekcja implementacji - Warstwa prezentacji i interfejs użytkownika

---

### 6. Proces Integracji z Chmurą Azure
**Plik:** `06_proces_integracji_chmura_azure.bpmn`

**Opis:** Proces konfiguracji i przesyłania danych do usług chmurowych Azure (Azure SQL Database, CosmosDB).

**Elementy kluczowe:**
- Wybór usługi Azure (SQL/CosmosDB)
- Testowanie połączenia (pyodbc/pymongo)
- Retry mechanism w przypadku błędu połączenia
- Monitorowanie postępu przesyłania
- Konfiguracja indeksów w chmurze
- Setup monitorowania Azure

**Zastosowanie w pracy:** Sekcja implementacji - Integracja z chmurą Azure

---

### 7. Proces Walidacji i Weryfikacji Danych
**Plik:** `07_proces_walidacji_danych.bpmn`

**Opis:** Kompleksowy proces walidacji danych przy użyciu `data_validation.py`.

**Elementy kluczowe:**
- Sprawdzenie istnienia plików
- Walidacja struktury CSV (kolumny, typy)
- Sprawdzenie wartości NULL
- Walidacja zakresów wartości
- Weryfikacja kluczy obcych i relacji
- Detekcja duplikatów
- Walidacja reguł biznesowych
- Generowanie raportów błędów/sukcesu

**Zastosowanie w pracy:** Sekcja implementacji - Zapewnienie jakości danych

---

### 8. Architektura Systemu (Swimlanes)
**Plik:** `08_architektura_systemu_swimlanes.bpmn`

**Opis:** Diagram typu Collaboration pokazujący interakcje między różnymi warstwami systemu.

**Warstwy (Swimlanes):**
- **Użytkownik:** Żądania i interakcje
- **Aplikacja Webowa (Flask):** Obsługa HTTP, routing, renderowanie
- **Moduł Generowania Danych:** Skrypty Python (generowanie, transformacja)
- **Bazy Danych:** MySQL, SQL Server, MongoDB, CosmosDB

**Przepływy komunikatów:**
- HTTP Request/Response
- Wywołania subprocess Python
- Strumieniowanie stdout
- Zapytania SQL/NoSQL
- Zwracanie wyników

**Zastosowanie w pracy:** Sekcja implementacji - Architektura wielowarstwowa systemu

---

## Jak Użyć Diagramów

### Otwieranie w bpmn.io
1. Wejdź na [https://demo.bpmn.io/](https://demo.bpmn.io/)
2. Kliknij "Open File" lub przeciągnij plik `.bpmn`
3. Diagram zostanie wyrenderowany z możliwością edycji

### Eksport Diagramów
W bpmn.io możesz eksportować diagramy jako:
- **SVG** - do dokumentów i publikacji (wektorowy, wysoka jakość)
- **PNG** - do prezentacji (rastrowy)
- **BPMN XML** - do dalszej edycji

### Zalecenia dla Pracy Inżynierskiej

**Rozdział Implementacja - Struktura:**

1. **3.1 Architektura Systemu**
   - Użyj: `08_architektura_systemu_swimlanes.bpmn`
   - Wyjaśnij interakcje między warstwami

2. **3.2 Moduł Generowania Danych**
   - Użyj: `02_proces_generowania_sql.bpmn`
   - Użyj: `03_proces_generowania_nosql.bpmn`
   - Opisz algorytmy generowania

3. **3.3 Walidacja i Weryfikacja**
   - Użyj: `07_proces_walidacji_danych.bpmn`
   - Opisz mechanizmy kontroli jakości

4. **3.4 Integracja z Bazami Danych**
   - Użyj: `04_proces_ladowania_danych.bpmn`
   - Opisz strategie ładowania danych

5. **3.5 Interfejs Użytkownika**
   - Użyj: `05_przeplyw_interfejsu_webowego.bpmn`
   - Opisz user experience i UX flow

6. **3.6 Integracja Chmurowa**
   - Użyj: `06_proces_integracji_chmura_azure.bpmn`
   - Opisz deployment w Azure

7. **3.7 Przepływ Kompletny**
   - Użyj: `01_glowny_proces_generowania_danych.bpmn`
   - Podsumowanie end-to-end procesu

---

## Konwencje Notacji BPMN

### Wykorzystane Elementy

**Zdarzenia:**
- ⭕ **Start Event** (zielony) - początek procesu
- ⭕ **End Event** (czerwony) - zakończenie procesu

**Aktywności:**
- ▭ **Task** - pojedyncze zadanie systemowe
- ▭ **User Task** - zadanie wymagające interakcji użytkownika

**Bramy (Gateways):**
- ◇ **Exclusive Gateway** - wybór jednej ścieżki (XOR)
- ◇ **Parallel Gateway** - równoległe wykonanie (AND)

**Przepływy:**
- → **Sequence Flow** - kolejność wykonania w obrębie procesu
- ⟿ **Message Flow** - komunikacja między uczestnikami

**Uczestnicy:**
- ▬ **Pool** - reprezentuje organizację/system
- ▬ **Lane** - reprezentuje rolę/moduł w systemie

---

## Technologie Wspierane przez Diagramy

- **Backend:** Python 3.x, Flask
- **Generowanie danych:** Faker, numpy, pandas
- **Bazy SQL:** MySQL, Microsoft SQL Server, Azure SQL Database
- **Bazy NoSQL:** MongoDB, Azure CosmosDB
- **Frontend:** HTML5, JavaScript, CSS (Tailwind)
- **Chmura:** Microsoft Azure
- **Format danych:** CSV, JSON

---

## Autor i Data Utworzenia

**Utworzone:** 14 grudnia 2025  
**Narzędzie:** VS Code GitHub Copilot  
**Format:** BPMN 2.0 XML  
**Kompatybilność:** bpmn.io, Camunda Modeler, inne edytory BPMN 2.0

---

## Notatki dla Recenzenta

Diagramy przedstawiają faktyczną implementację systemu zgodną z kodem źródłowym w folderach:
- `src/tools/` - skrypty generowania i walidacji
- `src/web/` - aplikacja Flask
- `src/database/` - schematy baz danych

Wszystkie procesy zostały zweryfikowane pod kątem zgodności z rzeczywistą logiką biznesową aplikacji.
