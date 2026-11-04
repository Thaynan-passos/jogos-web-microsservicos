from contextlib import asynccontextmanager

from app.api.v1.routers import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import AsyncSessionLocal, close_db, engine
from app.models.ranking import RankingEntry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

INITIAL_ENTRIES = [
    ("LucasMestre", "tic-tac-toe", 450, 42000, 18, "89%"),
    ("AnaMemoryQueen", "memory", 820, 28500, 24, "95%"),
    ("GabrielTactics", "rps", 380, 35000, 15, "80%"),
    ("Beatriz_Gamer", "tic-tac-toe", 390, 48000, 14, "78%"),
    ("DiegoCards", "memory", 690, 34000, 19, "84%"),
    ("Mariana_RPS", "rps", 340, 40000, 12, "75%"),
]


async def initialize_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        total = await session.scalar(select(func.count()).select_from(RankingEntry))
        if total:
            return

        session.add_all(
            [
                RankingEntry(
                    username=username,
                    game_slug=game_slug,
                    score=score,
                    duration_ms=duration_ms,
                    matches_played=matches_played,
                    win_rate=win_rate,
                )
                for username, game_slug, score, duration_ms, matches_played, win_rate in INITIAL_ENTRIES
            ]
        )
        await session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_database()
    yield
    await close_db()


app = FastAPI(title=settings.PROJECT_NAME, root_path="/api/rank", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
