# DevOps Knowledge Base

> **IEEE Young Protégé 2026 — DevOps Domain**  
> **Engineers:** Hirusha Sipsara & Shabeeha Miftha  
> **Mentor:** Mr. Achintha Balasooriya · Senior DevOps Engineer, CMS (Pvt) Ltd  

A containerized CRUD web application for storing and managing DevOps commands, tools, and snippets — built with FastAPI and PostgreSQL. The application is intentionally lightweight because the **DevOps engineering workflow** around it (Docker, Docker Compose, GitHub Actions CI/CD, and Terraform-managed AWS infrastructure with an S3 backend) is the core highlight of this project.

---

## 🎯 Current Project Architecture

```text
                     Developer
                         │
                         ▼
                       GitHub
                         │
                         ▼
                  GitHub Actions CI
                  ┌──────┴──────┐
                  │             │
                pytest      Docker Build
                  │             │
                  └──────┬──────┘
                         │
                         ▼
                DevOps Knowledge Base
                ┌───────────────────┐
                │ HTML + FastAPI    │
                │ PostgreSQL        │
                └───────────────────┘


                Infrastructure as Code (Terraform)

                      Terraform CLI
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
      AWS EC2 (Docker Host)   AWS S3 (Remote State)
```

### Milestone Progress Tracker

| Component / Layer | Status | Description |
| ----------------- | :---: | ----------- |
| **Web Application** | ✅ Complete | FastAPI REST API with CRUD and live search |
| **Reverse Proxy** | ✅ Complete | Nginx Alpine reverse proxy with gzip & proxy headers |
| **Database** | ✅ Complete | PostgreSQL database with SQLAlchemy ORM |
| **Automated Tests** | ✅ Complete | pytest suite with in-memory SQLite isolation |
| **Dockerization** | ✅ Complete | Optimized Python 3.11 slim Dockerfile |
| **Docker Compose** | ✅ Complete | Multi-container setup (Nginx + FastAPI + PostgreSQL) |
| **GitHub Actions CI** | ✅ Complete | Automated testing & Docker image build on push/PR |
| **Terraform IaC** | ✅ Complete | EC2 Container Host + Security Group provisioning |
| **Terraform S3 Backend** | ⚠️ Configured | S3 backend and lockfile configuration are present; current AWS state access must be verified with configured AWS CLI credentials |
| **AWS Deployment Automation** | ✅ Implemented | `Dev` pipeline tests the application and deploys it to the staging EC2 host through SSH |
| **AWS ECR / ECS** | ⏭️ Future Scope | Not implemented; retained as an optional future container-orchestration phase |

---

## 🛠️ Tech Stack

| Layer | Technology |
| ----- | ---------- |
| **Reverse Proxy** | Nginx 1.27 Alpine |
| **Application** | FastAPI + Python 3.11 |
| **Database** | PostgreSQL 16+ |
| **Frontend** | Vanilla HTML5 / CSS3 / Modern JavaScript (Served by FastAPI) |
| **ORM** | SQLAlchemy 2.0 |
| **Containerization** | Docker Engine & Docker Compose |
| **CI / CD Pipeline** | GitHub Actions |
| **Infrastructure as Code** | Terraform (AWS Provider) |
| **Cloud Provider** | Amazon Web Services (AWS EC2 & S3) |
| **Monitoring** | Prometheus Client Metrics (`/metrics`) |

---

## 🐳 Running with Docker & Docker Compose (Recommended)

### 1. Run with Docker Compose (Full Stack: Nginx + App + Database)
To run the full stack (Nginx reverse proxy, FastAPI application, and PostgreSQL database) with a single command:

```bash
docker compose up --build
```
- Access via Nginx (Port 80): [http://localhost](http://localhost)
- Direct FastAPI App (Port 8000): [http://localhost:8000](http://localhost:8000)
- Interactive Swagger API Docs: [http://localhost/docs](http://localhost/docs) (or [http://localhost:8000/docs](http://localhost:8000/docs))
- Health Check: [http://localhost/health](http://localhost/health) (or [http://localhost:8000/health](http://localhost:8000/health))

To stop the containers:
```bash
docker compose down
```

### 2. Build and Run Standalone Docker Image
```bash
# Build the Docker image
docker build -t devops-knowledge-base .

# Run the container
docker run -d -p 8000:8000 --name devops-kb-app devops-knowledge-base
```

---

## 🔄 GitHub Actions CI/CD Pipelines

The project contains two GitHub Actions workflows:

- [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs tests and verifies the Docker image on pushes and pull requests to `main` or `master`.
- [`.github/workflows/staging-workflow.yml`](.github/workflows/staging-workflow.yml) runs tests and deploys successful pushes from the exact `Dev` branch to the staging EC2 host.

### CI Pipeline Workflow:
1. **Trigger**: Automatically runs on every `push` and `pull_request` to `main` / `master`.
2. **Job 1: Unit & Integration Tests**:
   - Spawns a Python 3.11 environment.
   - Installs all dependencies from `app/requirements.txt`.
   - Runs `pytest tests/ -v` to verify application health, database operations, and endpoint contracts.
3. **Job 2: Docker Build & Verification**:
   - Executes after tests pass.
   - Sets up Docker Buildx and builds the container image to guarantee that the `Dockerfile` is always functional and deployable.

### Staging Deployment Workflow:

1. Runs the pytest suite with an isolated in-memory SQLite database.
2. Connects to the configured EC2 host using GitHub Secrets and strict SSH known-host verification.
3. Pulls the latest `Dev` branch on the server.
4. Builds the Docker image on EC2.
5. Stops and removes the previous `devops-kb-app` container.
6. Starts the replacement container on the existing `devops-kb-network` Docker network.

The latest verified staging workflow run completed successfully on **22 August 2026**. The deployed `/health` and `/metrics` endpoints were reachable during the Week 10 review on **6 September 2026**.

---

## ☁️ Infrastructure as Code (Terraform)

All AWS infrastructure is declared in the [`terraform/`](terraform/) directory.

### Directory Structure:
```text
terraform/
├── main.tf                  # AWS Provider, VPC lookup, AMI data source
├── variables.tf             # Parameterized region, instance type, environment
├── ec2.tf                   # EC2 Instance & Security Group with Docker cloud-init
├── backend.tf               # AWS S3 remote state and S3 lockfile configuration
├── outputs.tf               # Public IP, DNS, and application URLs
└── terraform.tfvars.example # Example variable definitions
```

### How to Provision AWS Infrastructure:

1. **Navigate to the terraform directory**:
   ```bash
   cd terraform
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Validate the Configuration**:
   ```bash
   terraform validate
   ```

4. **Review the Execution Plan**:
   ```bash
   terraform plan
   ```

5. **Apply Infrastructure**:
   ```bash
   terraform apply
   ```

6. **Clean Up / Destroy Resources**:
   ```bash
   terraform destroy
   ```

### 🗄️ AWS S3 Remote State Management
Terraform state is configured for remote management in [`terraform/backend.tf`](terraform/backend.tf).
- **Why Remote State?** It centralizes state for collaboration, uses an S3 lockfile to reduce concurrent state changes, and keeps state files with sensitive metadata out of Git.
- The S3 backend block is already active and uses `use_lockfile = true`; this project does not use DynamoDB locking.
- Before running `terraform plan` or applying changes, configure the AWS CLI, verify access with `aws sts get-caller-identity`, then run `terraform init`, `terraform state list`, and `terraform plan` to confirm the expected state and avoid creating duplicate resources.

---

## 🚀 Manual Local Setup (Without Docker)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL installed and running locally

### 2. Database Setup
```sql
CREATE USER devops_user WITH PASSWORD 'devops_pass';
CREATE DATABASE devops_kb OWNER devops_user;
GRANT ALL PRIVILEGES ON DATABASE devops_kb TO devops_user;
\c devops_kb
GRANT ALL ON SCHEMA public TO devops_user;
```

### 3. Environment & Dependencies
```bash
cp .env.example .env
pip install -r app/requirements.txt
```

### 4. Seed Data & Run
```bash
# Seed initial DevOps snippets
cd app
python seed_data.py

# Start application server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Running Automated Tests Locally

```bash
# Run complete test suite (uses fast in-memory SQLite isolation)
pytest tests/ -v
```

---

## 📁 Project Structure

```text
devops-knowledge-base/
├── .github/
│   └── workflows/
│       ├── ci.yml               # Main/master CI and Docker build verification
│       └── staging-workflow.yml # Dev branch CI and EC2 deployment
├── app/
│   ├── main.py                  # FastAPI application & API endpoints
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic validation schemas
│   ├── database.py              # Database connection & session factory
│   ├── seed_data.py             # Pre-loaded DevOps snippets & categories
│   ├── static/
│   │   └── index.html           # Single-Page Frontend Dashboard
│   └── requirements.txt         # Application dependencies
├── terraform/
│   ├── main.tf                  # Provider & data sources
│   ├── variables.tf             # Configurable input variables
│   ├── ec2.tf                   # EC2 instance & Security Group
│   ├── backend.tf               # AWS S3 Remote State configuration
│   ├── outputs.tf               # Output variables (Public IP, URL)
│   └── terraform.tfvars.example # Sample variables template
├── tests/
│   └── test_app.py              # Automated test suite (pytest)
├── .dockerignore                # Excluded build paths
├── .env.example                 # Sample environment variables
├── .gitignore                   # Git exclusions (Terraform state, .env, venv)
├── Dockerfile                   # Application container definition
├── docker-compose.yml           # Multi-container local orchestration
└── README.md                    # Project documentation
```

---

## 📡 Key Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `GET` | `/` | Frontend Knowledge Base Dashboard |
| `GET` | `/health` | System & Database Health Check |
| `GET` | `/metrics` | Prometheus Metrics Endpoint |
| `GET` | `/categories` | List all categories |
| `POST` | `/categories` | Create new category |
| `GET` | `/snippets` | List snippets (`?category=` filter supported) |
| `GET` | `/snippets/search?q=` | Full-text search across titles, tags & commands |
| `POST` | `/snippets` | Create a snippet |
| `PUT` | `/snippets/{id}` | Update snippet |
| `DELETE` | `/snippets/{id}` | Delete snippet |

---

## 👥 Authors & Credits

- **Hirusha Sipsara** & **Shabeeha Miftha** — IEEE Young Protégé 2026, DevOps Domain
- **Mentor:** Mr. Achintha Balasooriya, Senior DevOps Engineer at CMS (Pvt) Ltd
