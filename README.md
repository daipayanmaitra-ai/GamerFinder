# GamerFinder

Find gaming buddies by game, rank, playstyle, and schedule.

---

## Project Structure

```text
GamerFinder/
├── app/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration loader from .env using Pydantic Settings
│   ├── database.py         # SQLAlchemy engine, session maker, Base, and DB session dependency
│   ├── models.py           # SQLAlchemy ORM models (empty placeholder, ready for entities)
│   ├── schemas.py          # Pydantic schemas for data validation and serialization
│   ├── main.py             # FastAPI entrypoint, middleware, and router registration
│   └── routers/
│       ├── __init__.py     # Package initialization for API routers
│       └── health.py       # Health check route (/health)
├── tests/
│   ├── __init__.py         # Package initialization for test suite
│   └── test_health.py      # Health endpoint automated tests
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules (includes .env and SQLite db files)
├── requirements.txt        # Python project dependencies
├── SPEC.md                 # Project specifications document
└── README.md               # Setup and usage documentation
```

---

## File Explanations

| File | Purpose |
| --- | --- |
| `app/main.py` | The main FastAPI application entrypoint. Initializes the application instance, registers routers, and sets up high-level endpoints. |
| `app/database.py` | Configures the SQLAlchemy database engine (SQLite by default), `SessionLocal` factory, declarative `Base`, and the `get_db` FastAPI dependency for database sessions. |
| `app/models.py` | Defines SQLAlchemy ORM database models representing tables and relationships. Currently holds base structure without feature entities. |
| `app/schemas.py` | Defines Pydantic data models for request body validation and response serialization (e.g., `HealthCheck`). |
| `app/config.py` | Manages environment variables and application settings using `pydantic-settings`, reading from `.env`. |
| `app/routers/` | Directory containing modular API route handlers. |
| `app/routers/health.py` | Router providing the `/health` endpoint for monitoring application status. |
| `tests/` | Contains test suites (using `pytest` and `httpx`/`TestClient`) to verify application endpoints and behavior. |
| `requirements.txt` | Lists Python package dependencies for FastAPI, SQLAlchemy, Uvicorn, Pydantic, and testing tools. |
| `.env.example` | Template demonstrating required and optional environment variables. Never commit actual `.env` files. |

---

## Getting Started

### 1. Prerequisites

- Python 3.10+ (tested with Python 3.14)
- `pip` or virtual environment manager (`venv`)

### 2. Clone & Setup Environment

Create and activate a virtual environment:

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to create your local `.env`:

**On Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**On Linux / macOS:**
```bash
cp .env.example .env
```

You can customize values in `.env` as needed:
```env
PROJECT_NAME=GamerFinder
DEBUG=True
API_V1_STR=/api/v1
DATABASE_URL=sqlite:///./gamerfinder.db
```

*(Note: `.env` is listed in `.gitignore` and should never be committed to version control.)*

---

## Running the Application

Start the development server with live reload:

```bash
uvicorn app.main:app --reload
# Or via python module:
python -m uvicorn app.main:app --reload
```

The API will be accessible at:
- **Root**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Running Tests

Execute the automated test suite:

```bash
pytest
# Or via python module:
python -m pytest
```
