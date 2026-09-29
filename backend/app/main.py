from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.models.user import User
import app.models.finance

#Import Router
from app.routers import finance as finance_api
from app.routers import transfer as transfer_api
from app.routers import admin as admin_api

from app.core.config_loader import load_config

# Config Datei Laden
config = load_config()
defaults = config.get("defaults", {})

def init_db():
    Base.metadata.create_all(bind=engine)
    # Prüfen, ob der Admin-Benutzer existiert, wenn nicht, erstellen
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == defaults.get("admin_username", "admin")).first()
        if not existing_user:
            admin_user = User(
                username=defaults.get("admin_username", "admin"),
                email=defaults.get("admin_email", "admin@example.com"),
                hashed_password=defaults.get("admin_password", "admin")
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    init_db()
    yield
    # Shutdown code

app = FastAPI(
    title="PocketFlow API",
    description="BackendAPI für virutelle Unterkonten und CSV-Import",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Entwicklung only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routen hinzufügen
app.include_router(finance_api.router)
app.include_router(transfer_api.router)
app.include_router(admin_api.router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "PocketFlow API is running and DB initialized! Reload is activated!"}