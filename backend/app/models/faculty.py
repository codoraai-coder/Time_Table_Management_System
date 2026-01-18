from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from .base import Base, TimestampMixin

class Faculty(Base, TimestampMixin):
    """Faculty/Teacher model"""
    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Faculty(id={self.id}, name='{self.name}')>"
