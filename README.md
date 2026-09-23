# API Gateway

A configurable API Gateway built with **FastAPI**. The initial goal is to implement a reverse proxy that allows users to register and manage upstream APIs.

## Tech Stack

- **Python** - Programming language
- **FastAPI** - API framework
- **Uvicorn** - ASGI server
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **asyncpg** - Async PostgreSQL driver
- **Alembic** - Database migrations
- **psycopg** - PostgreSQL driver used by Alembic
- **uv** - Python package management
- **SonarQube** - Code quality and static analysis
- **PySonar** - SonarQube scanner

## Setup

Install dependencies:

```bash
uv add fastapi uvicorn
uv add sqlalchemy asyncpg
uv add alembic
uv add "psycopg[binary]"
```

Start PostgreSQL:

```bash
sudo systemctl enable --now postgresql
```

Check PostgreSQL:

```bash
pg_isready
```

Run the application:

```bash
uv run uvicorn api_gateway.main:app --app-dir src --reload
```

## Database

Application connection:

```text
postgresql+asyncpg://postgres:<password>@localhost:5432/api_gateway
```

Alembic connection:

```text
postgresql+psycopg://postgres:<password>@localhost:5432/api_gateway
```

`asyncpg` is used by the application for asynchronous database access. `psycopg` is used by Alembic for migrations.

## Database Migrations

Whenever you **create or modify a SQLAlchemy model**:

### 1. Generate a migration

```bash
uv run alembic revision --autogenerate -m "describe change"
```

### 2. Review the generated migration

Check the generated migration before applying it.

### 3. Apply the migration

```bash
uv run alembic upgrade head
```

Useful commands:

```bash
# Current database revision
uv run alembic current

# Migration history
uv run alembic history

# Roll back one migration
uv run alembic downgrade -1
```

## Code Quality

The project uses **SonarQube** for static code analysis.

### Start SonarQube

SonarQube runs locally using Docker.

Create persistent volumes:

```bash
docker volume create sonarqube_data
docker volume create sonarqube_logs
docker volume create sonarqube_extensions
```

Start SonarQube:

```bash
docker run -d \
  --name sonarqube \
  -p 9000:9000 \
  -v sonarqube_data:/opt/sonarqube/data \
  -v sonarqube_logs:/opt/sonarqube/logs \
  -v sonarqube_extensions:/opt/sonarqube/extensions \
  sonarqube:community
```

Check the container:

```bash
docker ps
```

SonarQube will be available at:

```text
http://localhost:9000
```

### Configure SonarQube

Create a project in SonarQube and generate a project analysis token.

Store the token in `.env`:

```env
SONAR_TOKEN=<your-token>
```

Make sure `.env` is included in `.gitignore`.

The project configuration is stored in:

```text
sonar-project.properties
```

Example:

```properties
sonar.projectKey=API-Gateway
sonar.projectName=API Gateway
sonar.sources=src
sonar.tests=tests
sonar.python.version=3.14
```

### Run Code Analysis

Once SonarQube is running:

```bash
uv run sonar
```

This runs PySonar using the project configuration and sends the analysis results to the local SonarQube server.

Results can be viewed at:

```text
http://localhost:9000
```

### SonarQube Docker Commands

```bash
# Start
docker start sonarqube

# Stop
docker stop sonarqube

# Restart
docker restart sonarqube

# View logs
docker logs -f sonarqube

# Check status
docker ps
```

## Development Workflow

```text
Change SQLAlchemy model
        ↓
Generate Alembic migration
        ↓
Review migration
        ↓
Apply migration
        ↓
Write/update tests
        ↓
Run SonarQube analysis
        ↓
Continue development
```

**Alembic manages database schema changes. SQLAlchemy manages database operations. SonarQube analyzes code quality.**