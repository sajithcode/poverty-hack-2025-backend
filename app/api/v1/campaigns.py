from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.db import get_db
from app.models.campaign import Campaign

router = APIRouter()

@router.get("")
async def list_campaigns(
    q: str | None = Query(default=None, description="fulltext search"),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if q:
        # Use FULLTEXT index (BOOLEAN MODE) — safe for MySQL 8+
        stmt = text("""
            SELECT id, uuid, slug, title, short_description, hospital_id, status
            FROM campaigns
            WHERE MATCH(title, short_description, full_description) AGAINST (:q IN BOOLEAN MODE)
            ORDER BY published_at DESC NULLS LAST, id DESC
            LIMIT 50
        """)
        rows = (await db.execute(stmt, {"q": q})).mappings().all()
        return rows
    stmt = select(Campaign)
    if status:
        from sqlalchemy import literal_column
        stmt = stmt.where(Campaign.status == status)
    rows = (await db.execute(stmt)).scalars().all()
    return [{"id": c.id, "slug": c.slug, "title": c.title, "status": c.status} for c in rows]
