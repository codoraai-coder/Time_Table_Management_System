from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, JSON
from .base import Base, TimestampMixin

class TimetableVersion(Base, TimestampMixin):
    """TimetableVersion model - stores immutable snapshots of complete timetables"""
    __tablename__ = "timetable_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    snapshot_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    def __repr__(self):
        return f"<TimetableVersion(id={self.id}, v={self.version_number}, published={self.is_published})>"
