from app.api.v1.endpoints import rankings
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(rankings.router)
