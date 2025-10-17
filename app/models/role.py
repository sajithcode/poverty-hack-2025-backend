from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, SmallInteger
from app.core.db import Base

class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
