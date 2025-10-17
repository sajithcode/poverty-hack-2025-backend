from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, DECIMAL, Enum, TIMESTAMP
from app.core.db import Base

class Hospital(Base):
    __tablename__ = "hospitals"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str | None] = mapped_column(String(120))
    address: Mapped[str | None]
    contact_name: Mapped[str | None] = mapped_column(String(150))
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(DECIMAL(9, 6), nullable=False)
    # location POINT (SRID 4326) is maintained by DB triggers, not mapped here
    verification_status: Mapped[str] = mapped_column(
        Enum('unverified','verified','flagged'), default='unverified'
    )
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    updated_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[str | None] = mapped_column(TIMESTAMP)
