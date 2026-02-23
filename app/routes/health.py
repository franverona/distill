from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import ollama

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """
    Check if api is healthy.
    """
    try:
        db.execute(text("SELECT 1"))
        db_connectivity = True
    except Exception:
        db_connectivity = False

    ollama_connectivity = await ollama.check_health()
    status_code = 200 if db_connectivity and ollama_connectivity else 503
    response = {
        "status": "ok" if db_connectivity and ollama_connectivity else "error",
        "db": "ok" if db_connectivity else "unreachable",
        "ollama": "ok" if ollama_connectivity else "unreachable",
    }
    return JSONResponse(content=response, status_code=status_code)
