from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal


class HospitalBase(BaseModel):
    name: str
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    latitude: float
    longitude: float


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HospitalInDBBase(HospitalBase):
    id: int
    uuid: str
    verification_status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Hospital(HospitalInDBBase):
    pass


class HospitalList(BaseModel):
    id: int
    uuid: str
    name: str
    city: Optional[str] = None
    district: Optional[str] = None
    verification_status: str

    class Config:
        from_attributes = True