from fastapi import APIRouter

from app.api.v1.endpoints import recovery

api_router = APIRouter()
api_router.include_router(recovery.router)

