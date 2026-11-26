"""
backend/config.py
=================
Configuration settings for SILLA Backend API.
Reads from environment variables with sensible production & development defaults.
"""

import os
from pathlib import Path
from typing import List

# Root project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database paths
DEFAULT_SQLITE_PATH = BASE_DIR / "SILLA_Data_Engineering" / "database" / "silla_staging.db"
DB_PATH = Path(os.getenv("SILLA_DB_PATH", str(DEFAULT_SQLITE_PATH)))

# PostgreSQL URL if available
DATABASE_URL = os.getenv("DATABASE_URL", None)

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CORS settings
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
]
EXTRA_CORS = os.getenv("CORS_ORIGINS")
if EXTRA_CORS:
    CORS_ORIGINS.extend([origin.strip() for origin in EXTRA_CORS.split(",") if origin.strip()])

# Frontend build path (for single-container production serving)
DEFAULT_FRONTEND_DIST = BASE_DIR / "silla-project (1)" / "silla" / "dist"
FRONTEND_DIST_DIR = Path(os.getenv("FRONTEND_DIST_DIR", str(DEFAULT_FRONTEND_DIST)))
