from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# We replace asyncpg with psycopg2 for synchronous execution if needed
raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./upie.db")

# Fix passwords containing unencoded '@' by splitting on the LAST '@'
if "://" in raw_db_url and "@" in raw_db_url:
    scheme_part, rest = raw_db_url.split("://", 1)
    if rest.count("@") > 1:
        # Split by the last '@'
        credentials, host_path = rest.rsplit("@", 1)
        # URL encode any '@' in credentials
        credentials = credentials.replace("@", "%40")
        raw_db_url = f"{scheme_part}://{credentials}@{host_path}"

SQLALCHEMY_DATABASE_URL = raw_db_url
if "postgresql+asyncpg" in SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
