from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, validator

class FacultyRow(BaseModel):
    """Schema for faculty.csv row"""
    faculty_id: str = Field(..., min_length=2, description="Faculty ID (e.g. F_001)")
    name: str = Field(..., min_length=2, description="Faculty full name")
    # Email removed as it's not in the source data

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

class CourseRow(BaseModel):
    """Schema for courses.csv row"""
    course_id: str = Field(..., min_length=2, description="Course ID")
    name: str = Field(..., min_length=2, description="Course name")
    type: str = Field(..., description="Course type (LECTURE/LAB)")
    weekly_periods: int = Field(..., gt=0, description="Weekly periods")
    needs_room_type: str = Field(..., description="Required room type")

class RoomRow(BaseModel):
    """Schema for rooms.csv row"""
    room_id: str = Field(..., min_length=2, description="Room ID")
    block: Optional[str] = Field(None, description="Block name")
    room_no: Optional[str] = Field(None, description="Room number")
    capacity: int = Field(..., gt=0, description="Student capacity")
    room_type: str = Field(..., description="Room type (LECTURE/LAB)")

class SectionRow(BaseModel):
    """Schema for sections.csv row"""
    section_id: str = Field(..., min_length=2, description="Section ID")
    dept: str = Field(..., description="Department")
    program: str = Field(..., description="Program (e.g. B.Tech)")
    year: int = Field(..., gt=0, description="Year")
    sem: str = Field(..., description="Semester")
    section_name: str = Field(..., description="Section Name (e.g. A)")
    shift: str = Field(..., description="Shift ID")
    student_count: int = Field(..., gt=0, description="Student count")
