from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.models.role import Role

router = APIRouter()

@router.get("/roles")
async def list_roles(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Role))
    return [{"id": r.id, "name": r.name} for r in res.scalars().all()]
