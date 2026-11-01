from app.api.v1.endpoints import games, sessions
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(games.router)
api_router.include_router(sessions.router)
