from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Enum, DECIMAL, TIMESTAMP
from app.core.db import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    slug: Mapped[str | None] = mapped_column(String(255), unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(280))
    full_description: Mapped[str | None]
    hospital_id: Mapped[int | None] = mapped_column(BigInteger)
    city: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str | None] = mapped_column(String(120))
    category: Mapped[str | None] = mapped_column(String(80))
    urgency: Mapped[str] = mapped_column(Enum('low','medium','high','critical'), default='medium')
    cost_estimate: Mapped[float] = mapped_column(DECIMAL(14,2), default=0)
    target_amount: Mapped[float] = mapped_column(DECIMAL(14,2), default=0)
    amount_raised: Mapped[float] = mapped_column(DECIMAL(14,2), default=0)
    verified: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(
        Enum('draft','pending_review','published','paused','funded','rejected'), default='draft'
    )
    published_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    created_by: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    updated_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[str | None] = mapped_column(TIMESTAMP)
