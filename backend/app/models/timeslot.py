import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Time
from .base import Base, TimestampMixin

class Timeslot(Base, TimestampMixin):
    """Timeslot model representing time periods"""
    __tablename__ = "timeslots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)

    def __repr__(self):
        return f"<Timeslot(id={self.id}, day={self.day}, {self.start_time}-{self.end_time})>"
