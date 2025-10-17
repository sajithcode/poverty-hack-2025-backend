from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal


class DonationBase(BaseModel):
    amount: Decimal
    donation_type: str = "monetary"
    message: Optional[str] = None
    is_anonymous: bool = False
    payment_method: Optional[str] = None


class DonationCreate(DonationBase):
    campaign_id: int


class DonationInDBBase(DonationBase):
    id: int
    uuid: str
    campaign_id: int
    user_id: Optional[int] = None
    payment_reference: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Donation(DonationInDBBase):
    pass


class DonationList(BaseModel):
    id: int
    uuid: str
    amount: Decimal
    donation_type: str
    is_anonymous: bool
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True