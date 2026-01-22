from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from .base import Base, TimestampMixin

class Section(Base, TimestampMixin):
    """Section/Class group model"""
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # e.g., 'A', 'B', 'L1'
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    faculty_id: Mapped[Optional[int]] = mapped_column(ForeignKey("faculty.id"), nullable=True)
    student_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    room_type: Mapped[str] = mapped_column(String, nullable=False, default="Lecture")
    shift: Mapped[str] = mapped_column(String, nullable=False, default="SHIFT_8_4")

    # Relationships
    course: Mapped["Course"] = relationship("Course")
    faculty: Mapped[Optional["Faculty"]] = relationship("Faculty")

    def __repr__(self):
        return f"<Section(id={self.id}, name='{self.name}', course_id={self.course_id})>"
