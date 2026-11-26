"""
backend/main.py
===============
SILLA Platform — Unified FastAPI Backend Server.
Integrates Data Engineering, NLP Retrieval, Data Science, and Smart Recommendation.
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure root workspace is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.config import (
    CORS_ORIGINS,
    FRONTEND_DIST_DIR,
    HOST,
    PORT,
    ENVIRONMENT,
    DB_PATH
)

from backend.routes import (
    health,
    recipes,
    search,
    cart,
    recommendations,
    catalog,
    assistant
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle manager."""
    print(f"🚀 SILLA Backend starting in '{ENVIRONMENT}' mode...")
    print(f"📁 Database path: {DB_PATH}")
    
    # Pre-warm NLP singleton model for zero-latency first search
    try:
        from SILLA_NLP.api import SillaRecipeMatcher
        print("🧠 Pre-warming SILLA NLP hybrid retrieval engine...")
        matcher = SillaRecipeMatcher.get_instance(db_path=DB_PATH)
        # Warmup probe
        _ = matcher.match("كشري مصري", top_k=1)
        print("✅ NLP retrieval engine pre-warmed successfully!")
    except Exception as e:
        print(f"⚠️ NLP pre-warming notice: {e}")

    yield

    print("🛑 SILLA Backend shutting down...")


app = FastAPI(
    title="SILLA API — Smart Food-Craving-to-Shopping-Cart Platform",
    description="Official REST API integrating Egyptian NLP query parsing, recipe discovery, smart cart optimization, and grocery price comparison.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(recipes.router, prefix="/api", tags=["Recipes"])
app.include_router(search.router, prefix="/api", tags=["NLP Search"])
app.include_router(cart.router, prefix="/api", tags=["Smart Cart"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(catalog.router, prefix="/api", tags=["Catalog"])
app.include_router(assistant.router, prefix="/api", tags=["Assistant"])


# Serve React Frontend in Production (Single Container deployment)
if FRONTEND_DIST_DIR.exists():
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """SPA Fallback: Serve index.html for client-side routing, or static file if exists."""
        if full_path.startswith("api/"):
            return {"error": "API route not found", "status_code": 404}
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        index_file = FRONTEND_DIST_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend build not found. Run 'npm run build'."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
