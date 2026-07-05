# DevOps Knowledge Base

> IEEE Young Protégé 2026 — DevOps Domain
> **Engineers:** Hirusha Sipsara & Shabeeha Miftha
> **Mentor:** Mr. Achintha Balasooriya · Senior DevOps Engineer, CMS (Pvt) Ltd

A simple CRUD application for storing and managing DevOps commands, tools, and snippets — built with FastAPI and PostgreSQL. The application is intentionally minimal; the DevOps pipeline built around it (Docker, GitHub Actions, AWS ECR, AWS ECS, Terraform) is the real focus of this project.

---

## 🛠️ Tech Stack

| Layer       | Tool                                    |
| ----------- | --------------------------------------- |
| Application | FastAPI + Python 3.11                   |
| Database    | PostgreSQL                              |
| Frontend    | Vanilla HTML/CSS/JS (served by FastAPI) |
| ORM         | SQLAlchemy                              |
| Monitoring  | Prometheus client (metrics endpoint)    |

> Docker, Nginx, CI/CD, and cloud deployment are being set up separately with guidance from the mentor and are **not included in this manual setup guide**.

---

## 🚀 Run It Manually (No Docker)

### Prerequisites

- Python 3.11+
- PostgreSQL installed and running locally

### Step 1 — Install PostgreSQL (if not already installed)

**macOS:**

```bash
brew install postgresql@16
brew services start postgresql@16
```

**Windows:** Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

### Step 2 — Create the Database and User

Open the PostgreSQL shell:

```bash
psql postgres
```

> **Windows users:** Open psql via PowerShell:
>
> ```powershell
> $env:PGPASSWORD="your_postgres_password"
> & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres
> ```

Run these SQL commands:

```sql
-- 1. Create the user (skip if already exists)
CREATE USER devops_user WITH PASSWORD 'devops_pass';

-- 2. Create the database
CREATE DATABASE devops_kb OWNER devops_user;

-- 3. Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE devops_kb TO devops_user;

-- 4. Connect to the new database
\c devops_kb

-- 5. Grant schema permission ← REQUIRED on PostgreSQL 15+ (fixes 'permission denied for schema public')
GRANT ALL ON SCHEMA public TO devops_user;

-- 6. Exit
\q
```

### Step 3 — Clone the Repo and Install Dependencies

```bash
git clone https://github.com/YOUR_USERNAME/devops-knowledge-base
cd devops-knowledge-base

# Install dependencies
pip install -r app/requirements.txt
```

> **Optional (recommended for multi-project setups):** Use a virtual environment to isolate dependencies:
>
> ```bash
> python -m venv venv
> source venv/bin/activate   # macOS/Linux
> venv\Scripts\activate      # Windows
> pip install -r app/requirements.txt
> ```

### Step 4 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and confirm the connection string matches what you set up in Step 2:

```
DATABASE_URL=postgresql://devops_user:devops_pass@localhost:5432/devops_kb
```

### Step 5 — Load Seed Data (Optional but Recommended)

This pre-loads useful DevOps snippets (Docker, Linux, Git, Terraform, AWS commands) so the app isn't empty on first run.

```bash
cd app
python seed_data.py
```

You should see output confirming categories and snippets were created.

### Step 6 — Run the Application

```bash
# from inside the app/ folder
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# On Windows (PowerShell, as Admin)
python -m uvicorn main:app --host [IP_ADDRESS] --port 8000 --reload
 -- or --
python -m uvicorn main:app --port 8000
```

### Step 7 — Open It

| What               | URL                           |
| ------------------ | ----------------------------- |
| Frontend Dashboard | http://localhost:8000/        |
| Swagger API Docs   | http://localhost:8000/docs    |
| Health Check       | http://localhost:8000/health  |
| Prometheus Metrics | http://localhost:8000/metrics |

---

## 🧪 Run Tests

Tests use an in-memory SQLite database, so no PostgreSQL connection is needed to run them.

```bash
# from the project root, with venv activated
pip install pytest httpx
pytest tests/ -v
```

---

## 📁 Project Structure

```
devops-knowledge-base/
├── app/
│   ├── main.py          # FastAPI routes
│   ├── models.py         # SQLAlchemy models (Category, Snippet)
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── database.py       # DB connection + session handling
│   ├── seed_data.py       # Pre-loads useful DevOps snippets
│   ├── static/
│   │   └── index.html    # Frontend dashboard UI
│   └── requirements.txt
├── tests/
│   └── test_app.py       # pytest test suite (12 tests)
├── .env.example
├── .gitignore
└── README.md
```

---

## 📡 API Endpoints

### System

| Method | Endpoint   | Description                 |
| ------ | ---------- | --------------------------- |
| GET    | `/health`  | App + database health check |
| GET    | `/metrics` | Prometheus metrics          |

### Categories

| Method | Endpoint           | Description         |
| ------ | ------------------ | ------------------- |
| GET    | `/categories`      | List all categories |
| POST   | `/categories`      | Create a category   |
| DELETE | `/categories/{id}` | Delete a category   |

### Snippets

| Method | Endpoint              | Description                                |
| ------ | --------------------- | ------------------------------------------ |
| GET    | `/snippets`           | List all snippets (`?category=` to filter) |
| GET    | `/snippets/search?q=` | Search by title, command, description, tag |
| POST   | `/snippets`           | Create a snippet                           |
| GET    | `/snippets/{id}`      | Get a single snippet                       |
| PUT    | `/snippets/{id}`      | Update a snippet                           |
| DELETE | `/snippets/{id}`      | Delete a snippet                           |

---

## 🖥️ Frontend

A single-page dashboard (`app/static/index.html`) — no build step, no framework. It's served directly by FastAPI at `/`. Features:

- Browse snippets by category (sidebar)
- Search across titles, commands, descriptions, and tags
- Create, edit, and delete snippets and categories
- One-click copy for any command
- Live health status indicator

---

## 🔜 What Comes Next (With Mentor Guidance)

- [ ] Dockerize the application
- [ ] Push image to AWS ECR
- [ ] Deploy to AWS ECS
- [ ] Build GitHub Actions CI/CD pipeline
- [ ] Provision infrastructure with Terraform

---

## 👤 Author

**Hirusha Sipsara** — IEEE Young Protégé 2026, DevOps Domain
Mentor: Mr. Achintha Balasooriya, Senior DevOps Engineer at CMS (Pvt) Ltd
