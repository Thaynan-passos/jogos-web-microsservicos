from fastapi import FastAPI

from app.api.v1.routers import api_router

app = FastAPI(title="Rank Service")

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
