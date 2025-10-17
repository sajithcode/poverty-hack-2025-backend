from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, JSON, SmallInteger, TIMESTAMP
from app.core.db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    role_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    is_email_verified: Mapped[int] = mapped_column(default=0)
    is_phone_verified: Mapped[int] = mapped_column(default=0)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    metadata: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    updated_at: Mapped[str | None] = mapped_column(TIMESTAMP)
    deleted_at: Mapped[str | None] = mapped_column(TIMESTAMP)
