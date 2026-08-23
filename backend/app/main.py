from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env if present

from app.api import jobs
from app.db.database import engine, Base
from app.db.models import JobModel, JobRowModel
import socket
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

db_url = os.getenv("DATABASE_URL")
if db_url:
    try:
        parsed = urlparse(db_url)
        logger.info(f"DB Hostname: {parsed.hostname}")
        logger.info(f"DB Port: {parsed.port}")
        logger.info(f"DB Username format: {parsed.username}")
        logger.info(f"DB Name: {parsed.path.lstrip('/')}")
        
        target_host = "aws-0-ap-southeast-2.pooler.supabase.com"
        logger.info(f"Testing DNS resolution for: {target_host}")
        try:
            ip = socket.gethostbyname(target_host)
            logger.info(f"DNS resolved {target_host} to {ip}")
        except Exception as e:
            logger.error(f"DNS resolution failed for {target_host}: {e}")
            
    except Exception as e:
        logger.error(f"Error parsing DATABASE_URL: {e}")

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

app = FastAPI(title="UniHack Product Intelligence (UPIE)", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "UPIE Backend"}
