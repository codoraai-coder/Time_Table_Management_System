from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from .base import Base, TimestampMixin

class Course(Base, TimestampMixin):
    """Course/Subject model"""
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    def __repr__(self):
        return f"<Course(id={self.id}, code='{self.code}', name='{self.name}')>"
