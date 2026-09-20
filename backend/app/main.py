from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, ensure_schema_columns
from .config import CORS_ORIGINS
from .api.auth_routes import router as auth_router
from .api.profile_routes import router as profile_router
from .api.scheme_routes import router as scheme_router
from .api.recommendation_routes import router as recommendation_router
from .api.calculator_routes import router as calculator_router
from .api.partner_routes import router as partner_router
from .api.application_routes import router as application_router
from .api.document_routes import router as document_router
from .api.admin_routes import router as admin_router
from .api.voice_routes import router as voice_router
from .api.workflow_routes import router as workflow_router
from .api.features_routes import router as features_router
from .api.offline_routes import router as offline_router
from .models import Scheme

Base.metadata.create_all(bind=engine)
ensure_schema_columns()

# Keep the local demo catalogue current across upgrades. seed_database() is idempotent.
try:
    from seed import seed_database
    seed_database()
except Exception as _seed_error:
    print(f"[AARAMBH] Demo seed skipped: {_seed_error}")

app=FastAPI(title="AARAMBH API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_credentials=True,
                   allow_methods=["*"],allow_headers=["*"])

for r in [auth_router,profile_router,scheme_router,recommendation_router,calculator_router,
          partner_router,application_router,document_router,admin_router,voice_router,workflow_router,
          features_router, offline_router]:
    app.include_router(r)

@app.get("/")
def root():
    return {"name":"AARAMBH","status":"running"}

@app.get("/health")
def health():
    return {"status":"ok"}
