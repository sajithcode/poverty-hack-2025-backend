from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.db import get_db
from app.core.deps import (
    get_current_active_user,
    require_hospital_contact,
    require_admin,
    generate_uuid
)
from app.models.user import User
from app.models.hospital import Hospital
from app.schemas.hospital import (
    HospitalCreate,
    HospitalUpdate,
    Hospital as HospitalSchema,
    HospitalList
)

router = APIRouter()


@router.get("/", response_model=List[HospitalList])
async def list_hospitals(
    city: str | None = None,
    district: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get list of all hospitals."""
    stmt = select(Hospital).where(Hospital.deleted_at.is_(None))
    
    if city:
        stmt = stmt.where(Hospital.city == city)
    if district:
        stmt = stmt.where(Hospital.district == district)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    hospitals = result.scalars().all()
    return hospitals


@router.get("/{hospital_id}", response_model=HospitalSchema)
async def get_hospital(
    hospital_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific hospital by ID or UUID."""
    # Try to find by UUID first, then by ID
    query = select(Hospital).where(Hospital.deleted_at.is_(None))
    
    if hospital_id.isdigit():
        query = query.where(Hospital.id == int(hospital_id))
    else:
        query = query.where(Hospital.uuid == hospital_id)
    
    result = await db.execute(query)
    hospital = result.scalar_one_or_none()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    return hospital


@router.post("/", response_model=HospitalSchema)
async def create_hospital(
    hospital_data: HospitalCreate,
    current_user: Annotated[User, Depends(require_hospital_contact)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new hospital. Requires admin/superadmin/hospital_contact role."""
    # Check if hospital with same name already exists
    result = await db.execute(
        select(Hospital).where(
            Hospital.name == hospital_data.name,
            Hospital.deleted_at.is_(None)
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital with this name already exists"
        )
    
    # Create new hospital
    new_hospital = Hospital(
        uuid=generate_uuid(),
        **hospital_data.model_dump()
    )
    
    db.add(new_hospital)
    await db.commit()
    await db.refresh(new_hospital)
    
    return new_hospital


@router.patch("/{hospital_id}", response_model=HospitalSchema)
async def update_hospital(
    hospital_id: str,
    hospital_data: HospitalUpdate,
    current_user: Annotated[User, Depends(require_hospital_contact)],
    db: AsyncSession = Depends(get_db)
):
    """Update a hospital. Requires admin/superadmin/hospital_contact role."""
    # Find hospital
    query = select(Hospital).where(Hospital.deleted_at.is_(None))
    
    if hospital_id.isdigit():
        query = query.where(Hospital.id == int(hospital_id))
    else:
        query = query.where(Hospital.uuid == hospital_id)
    
    result = await db.execute(query)
    hospital = result.scalar_one_or_none()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Update fields
    update_data = hospital_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hospital, field, value)
    
    await db.commit()
    await db.refresh(hospital)
    
    return hospital


@router.delete("/{hospital_id}")
async def delete_hospital(
    hospital_id: str,
    current_user: Annotated[User, Depends(require_admin)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a hospital. Requires admin/superadmin role."""
    # Find hospital
    query = select(Hospital).where(Hospital.deleted_at.is_(None))
    
    if hospital_id.isdigit():
        query = query.where(Hospital.id == int(hospital_id))
    else:
        query = query.where(Hospital.uuid == hospital_id)
    
    result = await db.execute(query)
    hospital = result.scalar_one_or_none()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Soft delete - set deleted_at timestamp
    from datetime import datetime
    hospital.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Hospital deleted successfully"}
