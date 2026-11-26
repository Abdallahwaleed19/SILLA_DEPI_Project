"""
backend/routes/catalog.py
=========================
Catalog Lookup Routes for Ingredients, Supermarket Products, and Stores.
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.services.db_service import list_ingredients, list_products, list_stores

router = APIRouter()


@router.get("/ingredients")
def get_ingredients():
    """Retrieve all canonical ingredients with dietary tags and default units."""
    return list_ingredients()


@router.get("/stores")
def get_stores():
    """Retrieve all available grocery store chains."""
    return list_stores()


@router.get("/products")
def get_products(
    store_id: Optional[str] = Query(None),
    ingredient_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Retrieve supermarket products with optional store and ingredient filtering."""
    return list_products(
        store_id=store_id,
        ingredient_id=ingredient_id,
        limit=limit,
        offset=offset
    )
