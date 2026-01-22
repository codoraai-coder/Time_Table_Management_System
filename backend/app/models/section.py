from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from .base import Base, TimestampMixin

class Section(Base, TimestampMixin):
    """Section/Class group model"""
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False) # e.g. CSE_2A
    name: Mapped[str] = mapped_column(String, nullable=False)  # e.g. 2A
    dept: Mapped[str] = mapped_column(String, nullable=True) # e.g. CSE
    program: Mapped[str] = mapped_column(String, nullable=True) # e.g. B.Tech
    year: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    sem: Mapped[str] = mapped_column(String, nullable=True) # e.g. Even
    shift: Mapped[str] = mapped_column(String, nullable=True) # e.g. SHIFT_8_4
    student_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Note: Removed direct course_id FK. Sections take multiple courses via Assignment table.

    def __repr__(self):
        return f"<Section(id={self.id}, code='{self.code}', count={self.student_count})>"
