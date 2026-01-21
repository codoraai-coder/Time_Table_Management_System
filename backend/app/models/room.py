from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from .base import Base, TimestampMixin

class Room(Base, TimestampMixin):
    """Room/Classroom model"""
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'Lecture', 'Lab'

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}', type='{self.type}')>"
