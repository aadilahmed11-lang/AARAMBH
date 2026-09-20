import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DATABASE_URL


def _make_engine(url):
    kwargs = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


# Beginner-friendly behavior: SQLite is the default and, when enabled, the app
# automatically falls back to SQLite if a configured MySQL server is unavailable.
ACTIVE_DATABASE_URL = DATABASE_URL
engine = _make_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")
except Exception as exc:
    if os.getenv("DB_FALLBACK_SQLITE", "true").lower() == "true" and not DATABASE_URL.startswith("sqlite"):
        ACTIVE_DATABASE_URL = "sqlite:///./aarambh.db"
        engine = _make_engine(ACTIVE_DATABASE_URL)
        print("[AARAMBH] MySQL connection unavailable; using local SQLite database for this run.")
        print(f"[AARAMBH] Database detail: {exc}")
    else:
        raise

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema_columns():
    """Add columns introduced by newer AARAMBH versions without destroying local data."""
    required = {
        "entrepreneur_profiles": {
            "marital_status": "VARCHAR(50)", "residence_type": "VARCHAR(50)",
            "minority_status": "VARCHAR(50)", "employment_status": "VARCHAR(80)",
            "disability_status": "VARCHAR(80)", "disability_percent": "FLOAT",
            "disability_type": "VARCHAR(120)", "aadhaar_available": "VARCHAR(20)",
            "caste_certificate_available": "VARCHAR(20)", "income_certificate_available": "VARCHAR(20)"
        },
        "schemes": {
            "target_categories": "VARCHAR(300)", "target_disability": "VARCHAR(80)",
            "target_income_max": "FLOAT", "target_states": "VARCHAR(500)",
            "target_keywords": "VARCHAR(800)", "target_age_min": "INTEGER", "target_age_max": "INTEGER"
        }
    }
    from sqlalchemy import inspect
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, columns in required.items():
            if not inspector.has_table(table):
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            for name, sql_type in columns.items():
                if name not in existing:
                    qtable = engine.dialect.identifier_preparer.quote(table)
                    qname = engine.dialect.identifier_preparer.quote(name)
                    conn.exec_driver_sql(f"ALTER TABLE {qtable} ADD COLUMN {qname} {sql_type}")
