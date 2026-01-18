from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from .base import Base, TimestampMixin

class Assignment(Base, TimestampMixin):
    """Assignment model - links Section, Course, Faculty, Room, and Timeslot"""
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty.id"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    timeslot_id: Mapped[int] = mapped_column(ForeignKey("timeslots.id"), nullable=False)

    # Relationships
    section: Mapped["Section"] = relationship("Section")
    faculty: Mapped["Faculty"] = relationship("Faculty")
    course: Mapped["Course"] = relationship("Course")
    room: Mapped["Room"] = relationship("Room")
    timeslot: Mapped["Timeslot"] = relationship("Timeslot")

    def __repr__(self):
        return (f"<Assignment(id={self.id}, section={self.section_id}, "
                f"faculty={self.faculty_id}, room={self.room_id}, timeslot={self.timeslot_id})>")
