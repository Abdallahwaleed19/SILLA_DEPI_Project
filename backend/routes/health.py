"""
backend/routes/health.py
========================
Health Check Route for SILLA Backend API.
"""

from fastapi import APIRouter
from backend.config import ENVIRONMENT
from backend.schemas.schemas import HealthResponse
from backend.services.db_service import get_db_stats

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    Health check endpoint returning system status, environment,
    database connectivity & row counts, and module readiness.
    """
    db_stats = get_db_stats()
    
    # Check module availability
    nlp_ready = False
    rec_ready = False
    ds_ready = False

    try:
        import SILLA_NLP
        nlp_ready = True
    except Exception:
        nlp_ready = False

    try:
        import SILLA_Recommendation
        rec_ready = True
    except Exception:
        rec_ready = False

    try:
        import SILLA_Data_Science
        ds_ready = True
    except Exception:
        ds_ready = False

    return HealthResponse(
        status="ok" if db_stats.get("connected") else "degraded",
        version="1.0.0",
        environment=ENVIRONMENT,
        database=db_stats,
        modules={
            "data_engineering": db_stats.get("connected", False),
            "nlp": nlp_ready,
            "recommendation": rec_ready,
            "data_science": ds_ready,
        }
    )
