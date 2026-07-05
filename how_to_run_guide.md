# 🚀 How to Run DevOps Knowledge Base (Windows Guide)

> **Tech Stack**: FastAPI + PostgreSQL + Vanilla HTML/JS
> **Project path**: `F:\Projects\IEEE_YOUNG_PROTEGE_2026\devops-knowledge-base-new`

---

## Prerequisites Checklist

| Item | Status |
|---|---|
| Python 3.10+ | ✅ Already installed (`C:\Program Files\Python310`) |
| PostgreSQL 18 | ✅ Already installed & running as Windows service |

---

## Step 1 — Verify PostgreSQL is Running

Open **PowerShell** and run:

```powershell
Get-Service -Name "postgresql*"
```

You should see `Status: Running`. If it shows `Stopped`, start it:

```powershell
Start-Service -Name "postgresql-x64-18"
```

---

## Step 2 — Create the Database and User

PostgreSQL binaries are at `C:\Program Files\PostgreSQL\18\bin\`. Run these commands (**replace `root123` with your actual postgres password**):

```powershell
# Create the app user
$env:PGPASSWORD="root123"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c `
  "DO `$`$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'devops_user') THEN CREATE USER devops_user WITH PASSWORD 'devops_pass'; END IF; END `$`$;"

# Create the database
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE devops_kb OWNER devops_user;"

# Grant privileges
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE devops_kb TO devops_user;"
```

> [!TIP]
> To make `psql` available globally, add `C:\Program Files\PostgreSQL\18\bin` to your **System PATH** in Windows Environment Variables.

---

## Step 3 — Navigate to Project Root

```powershell
cd "F:\Projects\IEEE_YOUNG_PROTEGE_2026\devops-knowledge-base-new"
```

---

## Step 4 — Create a Python Virtual Environment

```powershell
# Create the venv
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

> [!NOTE]
> If you see a script execution error, run: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

---

## Step 5 — Install Python Dependencies

```powershell
# With venv active:
pip install -r app\requirements.txt
```

This installs: FastAPI, Uvicorn, SQLAlchemy, psycopg2, Pydantic, Prometheus client, and more.

---

## Step 6 — Create the `.env` File

```powershell
Copy-Item .env.example .env
```

The `.env` file should contain:
```
DATABASE_URL=postgresql://devops_user:devops_pass@localhost:5432/devops_kb
```

No changes needed if you used the exact credentials from Step 2.

---

## Step 7 — Load Seed Data (Optional but Recommended)

```powershell
# Still from the project root, with venv active:
& ".\venv\Scripts\python.exe" app\seed_data.py
```

Expected output:
```
Seeded category 'Docker' with 4 snippets
Seeded category 'Linux' with 3 snippets
Seeded category 'Git' with 2 snippets
Seeded category 'Terraform' with 2 snippets
Seeded category 'AWS' with 2 snippets
```

> [!NOTE]
> If you see a `UnicodeEncodeError` at the very end — don't worry, the data was seeded successfully. It's just a terminal emoji encoding issue.

---

## Step 8 — Run the Application

```powershell
# From the project root:
& ".\venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Or navigate into `app\` first:
```powershell
cd app
..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

You'll see:
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

> [!TIP]
> Add `--reload` flag during development to auto-restart on code changes:
> ```powershell
> ..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
> ```

---

## Step 9 — Open in Browser

| What | URL |
|---|---|
| 🖥️ Frontend Dashboard | http://localhost:8000/ |
| 📖 Swagger API Docs | http://localhost:8000/docs |
| 💚 Health Check | http://localhost:8000/health |
| 📊 Prometheus Metrics | http://localhost:8000/metrics |

---

## Stopping the App

Press `Ctrl + C` in the terminal where uvicorn is running.

---

## Running Tests

```powershell
# From the project root, with venv active:
pytest tests/ -v
```

Tests use SQLite in-memory — **no PostgreSQL needed** for tests.

---

## Quick Restart (Next Time)

Once everything is set up, you only need these 3 commands next time:

```powershell
# 1. Go to project folder
cd "F:\Projects\IEEE_YOUNG_PROTEGE_2026\devops-knowledge-base-new"

# 2. Activate venv
.\venv\Scripts\Activate.ps1

# 3. Run the app (from inside app\ folder)
cd app
..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000/** in your browser. 🎉

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `psql` not recognized | Run the full path: `& "C:\Program Files\PostgreSQL\18\bin\psql.exe"` |
| `password authentication failed` | Make sure `$env:PGPASSWORD` matches your actual postgres password |
| `ModuleNotFoundError` | Make sure venv is activated before running `pip install` |
| Port 8000 already in use | Change the port: `--port 8080` |
| DB not connecting | Verify PostgreSQL service is running: `Get-Service "postgresql*"` |
