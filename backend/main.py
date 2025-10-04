from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv, find_dotenv
# from fastapi import HTTPException

from .routes.users import router as users_router
from .routes.exchanges import router as exchanges_router
from .routes.stocks import router as stocks_router
from .routes.reference_data import router as reference_router
from .database import create_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
# Suppress noisy loggers
logging.getLogger("watchfiles").setLevel(logging.WARNING)
# logging.getLogger("uvicorn.access").setLevel(logging.INFO)

# # Keep important loggers at INFO level
# logging.getLogger("uvicorn.error").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # Suppress SQL queries


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
            "http://localhost:3000",
            "http://127.0.0.1:3000"
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
logging.info(f"CORS origins set to: {origins if origins else 'None'}")


app.include_router(stocks_router)
app.include_router(users_router)
app.include_router(exchanges_router)
app.include_router(reference_router)

def main():
    load_dotenv(find_dotenv())
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("APP_ENV", "")
    logging.getLogger().setLevel(logging.INFO)

    if environment == "development":
        uvicorn.run(
            "backend.main:app", 
            host=host, 
            port=port, 
            reload=True,
            reload_excludes=["app.log", "*.log", "*.pyc", "__pycache__"],
            log_level="info"
        )

    else:
        uvicorn.run(
            "backend.main:app", 
            host=host, 
            port=port, 
            log_level="info"
        )