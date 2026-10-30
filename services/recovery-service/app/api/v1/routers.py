from app.api.v1.endpoints import recovery
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(recovery.router)
