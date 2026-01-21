from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, validator

class FacultyRow(BaseModel):
    """Schema for faculty.csv row"""
    name: str = Field(..., min_length=2, description="Faculty full name")
    email: EmailStr = Field(..., description="Official email address")

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

class CourseRow(BaseModel):
    """Schema for courses.csv row"""
    code: str = Field(..., min_length=2, description="Course code (e.g. CS101)")
    name: str = Field(..., min_length=2, description="Course name")
    credit_hours: int = Field(..., gt=0, le=10, description="Credit hours (1-10)")
    type: Literal['lecture', 'lab'] = Field(..., description="Course type: lecture or lab")

class RoomRow(BaseModel):
    """Schema for rooms.csv row"""
    name: str = Field(..., min_length=2, description="Room number/name")
    capacity: int = Field(..., gt=0, description="Student capacity")
    type: Literal['lecture', 'lab'] = Field(..., description="Room type: lecture or lab")

class SectionRow(BaseModel):
    """Schema for sections.csv row"""
    name: str = Field(..., min_length=2, description="Section name (e.g. CS-A)")
    strength: int = Field(..., gt=0, description="Total student count")
