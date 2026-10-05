# Tour Package Management API

FastAPI + PostgreSQL backend module for managing tour packages.

## Main Features

- Create tour package
- Get package by UUID
- Partial update
- Soft deactivation
- Duplicate prevention
- Search by name/destination
- Filtering by destination, category, price range, duration and availability
- Validation
- Automated tests

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Pydantic
- Alembic
- Docker Compose
- Pytest

## Architecture

The API follows a compact layered structure:

```text
Route -> Service -> Repository -> PostgreSQL
```

Routes handle HTTP concerns, services hold business rules, repositories perform SQLAlchemy database access, and PostgreSQL stores tour package data.

## Local Setup

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

## Swagger

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint |
| --- | --- |
| POST | `/api/v1/tour-packages/` |
| GET | `/api/v1/tour-packages/` |
| GET | `/api/v1/tour-packages/{package_id}` |
| PATCH | `/api/v1/tour-packages/{package_id}` |
| PATCH | `/api/v1/tour-packages/{package_id}/deactivate` |

## Search And Filters

`GET /api/v1/tour-packages/` supports these optional query parameters:

- `search`: partial case-insensitive match against name or destination
- `destination`: case-insensitive exact destination match
- `category`: case-insensitive exact category match
- `min_price`: minimum price, must be greater than or equal to 0
- `max_price`: maximum price, must be greater than or equal to 0
- `duration_days`: exact duration match, must be greater than 0
- `availability_status`: case-insensitive exact availability status match

Results return active packages only. Deactivation is a soft delete using `is_active=false`.

## Testing

```powershell
python -m pytest -q
```

The current suite contains 15 passing tests.
