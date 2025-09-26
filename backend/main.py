from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv, find_dotenv
from fastapi import HTTPException

from .routes import stocks, users
from .database.database import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

# Environment-based CORS configuration
def get_cors_origins():
    """Get CORS origins based on environment"""
    environment = os.getenv("APP_ENV")
    
    if environment.lower() == "development":
        return [
            "http://localhost:3000",   # React dev server
            "http://localhost:5173",   # Vite dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]
    
    else:  # production
        # Get from environment variable
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if cors_origins:
            return [origin.strip() for origin in cors_origins.split(",")]
        
        return []  # No origins allowed if not configured


origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(stocks.router)
app.include_router(users.router)


def main():
    load_dotenv(find_dotenv())
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("APP_ENV", "")

    if environment == "development":
        logging.getLogger().setLevel(logging.DEBUG)
        uvicorn.run(
            "backend.main:app", 
            host=host, 
            port=port, 
            reload=True,
            log_level="debug"
        )

    else:
        logging.getLogger().setLevel(logging.INFO)
        uvicorn.run(
            "backend.main:app", 
            host=host, 
            port=port, 
            log_level="info"
        )