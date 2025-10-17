from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, or_, and_

from app.core.db import get_db
from app.core.deps import (
    get_current_active_user,
    require_hospital_contact,
    require_admin,
    generate_uuid
)
from app.models.user import User
from app.models.campaign import Campaign
from app.models.donation import CampaignImage, CampaignDocument, CampaignFollower
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    Campaign as CampaignSchema,
    CampaignList,
    CampaignImage as CampaignImageSchema,
    CampaignImageCreate,
    CampaignDocument as CampaignDocumentSchema,
    CampaignDocumentCreate,
    CampaignFollower as CampaignFollowerSchema,
    CampaignFollowerCreate
)

router = APIRouter()


@router.get("/", response_model=List[CampaignList])
async def list_campaigns(
    q: str | None = Query(default=None, description="Search query"),
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Get list of campaigns with optional search and filtering."""
    if q:
        # Use fulltext search for MySQL
        stmt = text("""
            SELECT id, uuid, slug, title, short_description, urgency, 
                   target_amount, amount_raised, verified, status, published_at
            FROM campaigns
            WHERE MATCH(title, short_description, full_description) AGAINST (:q IN BOOLEAN MODE)
              AND deleted_at IS NULL
            ORDER BY published_at DESC NULLS LAST, id DESC
            LIMIT :limit OFFSET :skip
        """)
        result = await db.execute(stmt, {"q": q, "limit": limit, "skip": skip})
        rows = result.mappings().all()
        return [CampaignList.model_validate(dict(row)) for row in rows]
    
    # Regular filtering
    stmt = select(Campaign).where(Campaign.deleted_at.is_(None))
    
    if status:
        stmt = stmt.where(Campaign.status == status)
    
    stmt = stmt.order_by(Campaign.published_at.desc(), Campaign.id.desc())
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    campaigns = result.scalars().all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignSchema)
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific campaign by ID or UUID."""
    query = select(Campaign).where(Campaign.deleted_at.is_(None))
    
    if campaign_id.isdigit():
        query = query.where(Campaign.id == int(campaign_id))
    else:
        query = query.where(Campaign.uuid == campaign_id)
    
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign


@router.post("/", response_model=CampaignSchema)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: Annotated[User, Depends(require_hospital_contact)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign. Requires admin/superadmin/hospital_contact role."""
    # Generate slug from title if not provided
    import re
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', campaign_data.title.lower())
    slug = re.sub(r'\s+', '-', slug)
    
    # Check if slug is unique
    counter = 1
    original_slug = slug
    while True:
        result = await db.execute(
            select(Campaign).where(
                Campaign.slug == slug,
                Campaign.deleted_at.is_(None)
            )
        )
        if not result.scalar_one_or_none():
            break
        slug = f"{original_slug}-{counter}"
        counter += 1
    
    # Create new campaign
    new_campaign = Campaign(
        uuid=generate_uuid(),
        slug=slug,
        created_by=current_user.id,
        **campaign_data.model_dump()
    )
    
    db.add(new_campaign)
    await db.commit()
    await db.refresh(new_campaign)
    
    return new_campaign


@router.patch("/{campaign_id}", response_model=CampaignSchema)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user: Annotated[User, Depends(require_hospital_contact)],
    db: AsyncSession = Depends(get_db)
):
    """Update a campaign. Requires admin/superadmin/hospital_contact role."""
    # Find campaign
    query = select(Campaign).where(Campaign.deleted_at.is_(None))
    
    if campaign_id.isdigit():
        query = query.where(Campaign.id == int(campaign_id))
    else:
        query = query.where(Campaign.uuid == campaign_id)
    
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update fields
    update_data = campaign_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a campaign. Requires admin/superadmin role."""
    # Find campaign
    query = select(Campaign).where(Campaign.deleted_at.is_(None))
    
    if campaign_id.isdigit():
        query = query.where(Campaign.id == int(campaign_id))
    else:
        query = query.where(Campaign.uuid == campaign_id)
    
    result = await db.execute(query)
    campaign = result.scalar_one_or_none()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Soft delete
    from datetime import datetime
    campaign.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Campaign deleted successfully"}


# Campaign Images endpoints
@router.get("/{campaign_id}/images", response_model=List[CampaignImageSchema])
async def get_campaign_images(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all images for a campaign."""
    # First verify campaign exists
    await get_campaign(campaign_id, db)
    
    # Get campaign numeric ID
    if campaign_id.isdigit():
        numeric_id = int(campaign_id)
    else:
        campaign_result = await db.execute(
            select(Campaign.id).where(Campaign.uuid == campaign_id)
        )
        numeric_id = campaign_result.scalar_one()
    
    result = await db.execute(
        select(CampaignImage).where(CampaignImage.campaign_id == numeric_id)
    )
    images = result.scalars().all()
    return images


@router.post("/{campaign_id}/images", response_model=CampaignImageSchema)
async def add_campaign_image(
    campaign_id: str,
    image_data: CampaignImageCreate,
    current_user: Annotated[User, Depends(require_hospital_contact)],
    db: AsyncSession = Depends(get_db)
):
    """Add an image to a campaign."""
    # Verify campaign exists and get numeric ID
    campaign = await get_campaign(campaign_id, db)
    
    new_image = CampaignImage(
        campaign_id=campaign.id,
        **image_data.model_dump()
    )
    
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    
    return new_image


# Campaign Documents endpoints
@router.get("/{campaign_id}/documents", response_model=List[CampaignDocumentSchema])
async def get_campaign_documents(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for a campaign."""
    # First verify campaign exists
    await get_campaign(campaign_id, db)
    
    # Get campaign numeric ID
    if campaign_id.isdigit():
        numeric_id = int(campaign_id)
    else:
        campaign_result = await db.execute(
            select(Campaign.id).where(Campaign.uuid == campaign_id)
        )
        numeric_id = campaign_result.scalar_one()
    
    result = await db.execute(
        select(CampaignDocument).where(CampaignDocument.campaign_id == numeric_id)
    )
    documents = result.scalars().all()
    return documents


@router.post("/{campaign_id}/documents", response_model=CampaignDocumentSchema)
async def add_campaign_document(
    campaign_id: str,
    document_data: CampaignDocumentCreate,
    current_user: Annotated[User, Depends(require_hospital_contact)],
    db: AsyncSession = Depends(get_db)
):
    """Add a document to a campaign."""
    # Verify campaign exists and get numeric ID
    campaign = await get_campaign(campaign_id, db)
    
    new_document = CampaignDocument(
        campaign_id=campaign.id,
        **document_data.model_dump()
    )
    
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    
    return new_document


# Campaign Followers endpoints
@router.get("/{campaign_id}/followers", response_model=List[CampaignFollowerSchema])
async def get_campaign_followers(
    campaign_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all followers for a campaign."""
    # First verify campaign exists
    await get_campaign(campaign_id, db)
    
    # Get campaign numeric ID
    if campaign_id.isdigit():
        numeric_id = int(campaign_id)
    else:
        campaign_result = await db.execute(
            select(Campaign.id).where(Campaign.uuid == campaign_id)
        )
        numeric_id = campaign_result.scalar_one()
    
    result = await db.execute(
        select(CampaignFollower).where(CampaignFollower.campaign_id == numeric_id)
    )
    followers = result.scalars().all()
    return followers


@router.post("/{campaign_id}/followers", response_model=CampaignFollowerSchema)
async def follow_campaign(
    campaign_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db)
):
    """Follow a campaign. Requires authentication."""
    # Verify campaign exists and get numeric ID
    campaign = await get_campaign(campaign_id, db)
    
    # Check if already following
    existing = await db.execute(
        select(CampaignFollower).where(
            and_(
                CampaignFollower.campaign_id == campaign.id,
                CampaignFollower.user_id == current_user.id
            )
        )
    )
    
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this campaign"
        )
    
    new_follower = CampaignFollower(
        campaign_id=campaign.id,
        user_id=current_user.id
    )
    
    db.add(new_follower)
    await db.commit()
    await db.refresh(new_follower)
    
    return new_follower
