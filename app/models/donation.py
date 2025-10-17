from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, DECIMAL, TIMESTAMP, TEXT
from app.core.db import Base

class Donation(Base):
    __tablename__ = "donations"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    campaign_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    amount: Mapped[float] = mapped_column(DECIMAL(14,2), nullable=False)
    donation_type: Mapped[str] = mapped_column(String(50), default='monetary')  # monetary, in_kind
    message: Mapped[str | None] = mapped_column(TEXT)
    is_anonymous: Mapped[int] = mapped_column(default=0)
    payment_method: Mapped[str | None] = mapped_column(String(50))
    payment_reference: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default='pending')  # pending, completed, failed, refunded
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    updated_at: Mapped[str | None] = mapped_column(TIMESTAMP)

class CampaignImage(Base):
    __tablename__ = "campaign_images"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str | None] = mapped_column(String(255))
    is_primary: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)

class CampaignDocument(Base):
    __tablename__ = "campaign_documents"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str | None] = mapped_column(String(100))  # medical_report, prescription, etc.
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)

class CampaignFollower(Base):
    __tablename__ = "campaign_followers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    followed_at: Mapped[str | None] = mapped_column(TIMESTAMP)