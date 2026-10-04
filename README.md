# PhotoShare REST API

REST API for sharing photos built with FastAPI.

## Features

- JWT authentication
- Roles: user, moderator, admin
- Upload and manage photos
- Tags and photo search
- Cloudinary image transformations
- QR codes
- Comments
- Photo ratings
- User profiles
- PostgreSQL database
- Docker support
- Tests with more than 90% coverage

## Technologies

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Cloudinary
- Docker
- Pytest

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` using `.env.example` as a template.

Run database migrations:

```bash
alembic upgrade head
```

Start the application:

```bash
uvicorn main:app --reload
```

## Docker

Run the project with:

```bash
docker compose up --build
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Tests

Run tests:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest --cov=. --cov-report=term-missing
```