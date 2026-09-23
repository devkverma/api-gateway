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

Check the file created under Alembic's migration directory.

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
Continue development
```

**Alembic manages database schema changes. SQLAlchemy manages database operations.**