import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/finance.db")
# Mehrere Threads können gleichzeitig auf die Datenbank zugreifen
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependecy für FastAPI, um bei jedem Request eine DB-Session zu erstellen und zu schließen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()