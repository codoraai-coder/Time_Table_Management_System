from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from .base import Base, TimestampMixin

class Room(Base, TimestampMixin):
    """Room/Classroom model"""
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False) # e.g. AB_101
    block: Mapped[str] = mapped_column(String, nullable=True)
    room_no: Mapped[str] = mapped_column(String, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    type: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'LECTURE', 'LAB'

    def __repr__(self):
        return f"<Room(id={self.id}, code='{self.code}', type='{self.type}', capacity={self.capacity})>"
