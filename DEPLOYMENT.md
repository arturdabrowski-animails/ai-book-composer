# Deployment Guide - Render.com

## Problem: "Checking" bez końca

Jeśli frontend pokazuje "checking..." bez końca, to oznacza że:
1. Backend nie odpowiada (śpi, crashed, lub nie jest wdrożony)
2. Frontend ma zły URL backendu
3. Problem z CORS

## Szybka diagnoza

```bash
# Sprawdź czy backend działa:
curl https://aibookcomposer-backend.onrender.com/health

# Powinno zwrócić: {"status":"healthy"}
# Jeśli zwraca "Access denied" = backend nie działa
```

## Rozwiązanie krok po kroku

### 1. Wejdź na Render Dashboard
https://dashboard.render.com/

### 2. Sprawdź status usług

Powinieneś mieć 3 usługi:
- **aibookcomposer-backend** (Web Service) - musi być 🟢 Active
- **aibookcomposer-frontend** (Static Site) - musi być 🟢 Active
- **aibookcomposer-db** (PostgreSQL) - musi być 🟢 Available

### 3. Jeśli backend jest 🔴 Suspended lub 🟡 Deploying

**Suspend = free tier zasnął po 15 min bezczynności**

Rozwiązania:
- Kliknij "Manual Deploy" -> "Deploy latest commit"
- Poczekaj 2-3 minuty aż się uruchomi
- Odśwież frontend

**Jeśli backend pokazuje "Build failed" lub "Deploy failed":**
- Sprawdź logi (Logs tab)
- Upewnij się że environment variables są ustawione:
  - `DATABASE_URL` - połączenie z bazą (automatyczne z render.yaml)
  - `SECRET_KEY` - klucz JWT (automatyczne)
  - `PYTHON_VERSION` = "3.11"

### 4. Jeśli frontend ma zły URL backendu

Sprawdź w Render Dashboard -> aibookcomposer-frontend -> Environment:

Musi być:
```
VITE_API_URL = https://aibookcomposer-backend.onrender.com
```

Jeśli nie ma lub jest inny - dodaj/zmień i zrób "Clear build cache & deploy"

### 5. Redeploy po zmianach w kodzie

Po każdym `git push` do main brancha:

1. Render **automatycznie** deployuje jeśli masz ustawione Auto-Deploy
2. Jeśli nie - ręcznie kliknij "Manual Deploy" dla:
   - backend (najpierw!)
   - frontend (potem)

### 6. Pierwsze wdrożenie (jeśli usługi nie istnieją)

1. W Render Dashboard: "New" -> "Blueprint"
2. Connect repository: `ai-book-composer`
3. Render wykryje `render.yaml` i utworzy wszystkie usługi automatycznie
4. Poczekaj 5-10 minut na deployment
5. Sprawdź czy wszystkie 3 usługi są 🟢

## Najczęstsze problemy

### "Access denied" przy curl
= Backend nie działa (suspended, crashed, nie wdrożony)
✅ Idź do dashboard i redeploy backend

### "CORS error" w konsoli przeglądarki
= Backend działa ale nie ma frontendu w CORS allowed origins
✅ Jest już naprawione w kodzie (`config.py` ma `aibookcomposer-frontend.onrender.com`)

### Frontend ładuje się ale pokazuje "checking..."
= Frontend nie może połączyć się z backendem
✅ Sprawdź czy VITE_API_URL jest poprawny w environment variables

### Database connection errors
= Backend nie może połączyć się z bazą
✅ Sprawdź czy DATABASE_URL environment variable jest ustawiony z bazy danych

## Free Tier Limity Render.com

⚠️ **WAŻNE dla darmowego planu:**

- Backend **zasypia po 15 minutach** bezczynności
- Pierwsze uruchomienie po sleep = **30-60 sekund** rozruchu
- **750 godzin/miesiąc** czasu działania
- Baza danych: **1GB storage**, **1 month retention**

**Tip:** Jeśli aplikacja "nie działa", zaczekaj 60 sekund - to może być rozruch z sleep mode!

## Monitoring

Dodaj ten link do zakładek:
```
https://aibookcomposer-backend.onrender.com/health
```

Powinno zawsze zwracać:
```json
{"status":"healthy"}
```

Jeśli nie - backend nie działa!
