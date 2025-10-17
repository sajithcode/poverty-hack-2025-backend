from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.models.hospital import Hospital

router = APIRouter()

@router.get("")
async def list_hospitals(
    city: str | None = None,
    district: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Hospital)
    if city:
        stmt = stmt.where(Hospital.city == city)
    if district:
        stmt = stmt.where(Hospital.district == district)
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": h.id, "name": h.name, "city": h.city, "district": h.district,
            "lat": float(h.latitude), "lng": float(h.longitude),
            "verification_status": h.verification_status
        } for h in rows
    ]
