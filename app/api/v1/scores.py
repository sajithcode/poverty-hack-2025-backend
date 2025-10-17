from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.db import get_db

router = APIRouter()

@router.get("/campaigns")
async def campaign_scores(db: AsyncSession = Depends(get_db)):
    sql = text("SELECT * FROM vw_campaign_priority_scores ORDER BY weighted_score DESC LIMIT 100")
    rows = (await db.execute(sql)).mappings().all()
    return rows

@router.get("/hospitals")
async def hospital_scores(db: AsyncSession = Depends(get_db)):
    sql = text("SELECT * FROM vw_hospital_priority_scores ORDER BY priority_score DESC")
    rows = (await db.execute(sql)).mappings().all()
    return rows
