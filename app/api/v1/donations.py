from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_db
from app.models.donation import Donation
from app.schemas.donation import Donation as DonationSchema, DonationList

router = APIRouter()


@router.get("/by-campaign/{campaign_id}", response_model=List[DonationList])
async def get_donations_by_campaign(
    campaign_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all donations for a specific campaign."""
    result = await db.execute(
        select(Donation)
        .where(Donation.campaign_id == campaign_id)
        .order_by(Donation.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    donations = result.scalars().all()
    return donations


@router.get("/by-user/{user_id}", response_model=List[DonationList])
async def get_donations_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all donations made by a specific user."""
    result = await db.execute(
        select(Donation)
        .where(Donation.user_id == user_id)
        .order_by(Donation.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    donations = result.scalars().all()
    return donations