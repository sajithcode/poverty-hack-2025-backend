from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal


class CampaignBase(BaseModel):
    title: str
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    hospital_id: Optional[int] = None
    city: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    urgency: str = "medium"
    cost_estimate: Decimal = Decimal("0")
    target_amount: Decimal = Decimal("0")


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    hospital_id: Optional[int] = None
    city: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    urgency: Optional[str] = None
    cost_estimate: Optional[Decimal] = None
    target_amount: Optional[Decimal] = None
    status: Optional[str] = None


class CampaignInDBBase(CampaignBase):
    id: int
    uuid: str
    slug: Optional[str] = None
    amount_raised: Decimal
    verified: int
    status: str
    published_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Campaign(CampaignInDBBase):
    pass


class CampaignList(BaseModel):
    id: int
    uuid: str
    slug: Optional[str] = None
    title: str
    short_description: Optional[str] = None
    urgency: str
    target_amount: Decimal
    amount_raised: Decimal
    verified: int
    status: str
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Campaign media schemas
class CampaignImage(BaseModel):
    id: int
    campaign_id: int
    url: str
    caption: Optional[str] = None
    is_primary: bool = False

    class Config:
        from_attributes = True


class CampaignImageCreate(BaseModel):
    url: str
    caption: Optional[str] = None
    is_primary: bool = False


class CampaignDocument(BaseModel):
    id: int
    campaign_id: int
    title: str
    url: str
    document_type: Optional[str] = None

    class Config:
        from_attributes = True


class CampaignDocumentCreate(BaseModel):
    title: str
    url: str
    document_type: Optional[str] = None


class CampaignFollower(BaseModel):
    id: int
    campaign_id: int
    user_id: int
    followed_at: datetime

    class Config:
        from_attributes = True


class CampaignFollowerCreate(BaseModel):
    pass  # user_id will come from authentication