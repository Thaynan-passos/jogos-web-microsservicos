from fastapi import APIRouter

from app.api.v1.endpoints import rankings

api_router = APIRouter()
api_router.include_router(rankings.router)
