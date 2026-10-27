from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("/")
async def list_rankings() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ranking endpoint not implemented",
    )
