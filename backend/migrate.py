"""Small idempotent MySQL migration for existing AARAMBH prototype databases."""
from sqlalchemy import text
from app.database import engine

TABLE_COLUMNS = {
    "schemes": {
        "moratorium_months": "INT DEFAULT 0",
        "coverage_percent": "FLOAT DEFAULT 90",
        "max_project_cost": "FLOAT DEFAULT 0",
        "benefit_type": "VARCHAR(80) DEFAULT 'Loan'",
        "eligibility_summary": "TEXT",
        "data_source": "VARCHAR(500)",
        "verification_status": "VARCHAR(40) DEFAULT 'Unverified'",
        "verified_at": "DATETIME",
        "verified_by": "INT",
        "next_review_date": "VARCHAR(30)",
    },
    "entrepreneur_profiles": {
        "name": "VARCHAR(120)",
        "age": "INT",
        "gender": "VARCHAR(30)",
        "contact": "VARCHAR(30)",
        "existing_loan": "VARCHAR(30)",
        "education_level": "VARCHAR(120)",
        "course_type": "VARCHAR(150)",
        "institution": "VARCHAR(200)",
        "course_fee": "FLOAT",
        "study_location": "VARCHAR(50)",
        "course_duration_months": "INT",
    },
    "partners": {
        "phone": "VARCHAR(30)",
        "rating": "FLOAT DEFAULT 4.0",
        "fund_utilization_percent": "FLOAT DEFAULT 100",
        "npa_percent": "FLOAT DEFAULT 0",
        "overdue_percent": "FLOAT DEFAULT 0",
        "supported_scheme_types": "VARCHAR(100) DEFAULT 'business,education'",
        "source_url": "VARCHAR(500)",
        "data_source": "VARCHAR(500)",
        "verification_status": "VARCHAR(40) DEFAULT 'Unverified'",
        "verified_at": "DATETIME",
        "verified_by": "INT",
        "next_review_date": "VARCHAR(30)",
    },
    "applications": {
        "is_eligible": "BOOLEAN",
        "document_verified_at": "DATETIME",
        "partner_review_at": "DATETIME",
        "decision_date": "DATETIME",
    },
}

with engine.begin() as conn:
    for table, columns in TABLE_COLUMNS.items():
        existing = {r[0] for r in conn.execute(text(f"SHOW COLUMNS FROM `{table}`"))}
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE `{table}` ADD COLUMN `{name}` {definition}"))
print("Migration complete.")
