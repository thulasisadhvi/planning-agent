# models.py
from pydantic import BaseModel, Field, validator
from typing import List, Tuple

class Course(BaseModel):
    course_code: str = Field(..., description="The unique code for the course, e.g., 'CS101'.")
    title: str
    credits: int
    # Example: [('Mon', '10:00', '11:30'), ('Wed', '10:00', '11:30')]
    schedule: List[Tuple[str, str, str]] = []

class Semester(BaseModel):
    semester_name: str # e.g., "Fall 2024"
    courses: List[Course] = []
    max_credits: int = 18

    @validator('courses')
    def check_credit_limit(cls, v, values):
        total_credits = sum(course.credits for course in v)
        if total_credits > values.get('max_credits', 18):
            raise ValueError(f"Total credits ({total_credits}) exceed the limit of {values.get('max_credits')}.")
        return v

    @validator('courses')
    def check_schedule_conflicts(cls, v):
        def time_to_minutes(t_str: str) -> int:
            """Converts 'HH:MM' string to minutes from midnight."""
            h, m = map(int, t_str.split(':'))
            return h * 60 + m

        # Check every pair of courses in the semester for overlap
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                course1, course2 = v[i], v[j]
                
                for day1, start1, end1 in course1.schedule:
                    for day2, start2, end2 in course2.schedule:
                        if day1 == day2: # Only check if they are on the same day
                            s1, e1 = time_to_minutes(start1), time_to_minutes(end1)
                            s2, e2 = time_to_minutes(start2), time_to_minutes(end2)
                            
                            # Overlap condition
                            if max(s1, s2) < min(e1, e2):
                                raise ValueError(f"Schedule conflict between {course1.course_code} and {course2.course_code} on {day1}.")
        return v

class DegreePlan(BaseModel):
    student_id: str
    completed_courses: List[Course]
    planned_semesters: List[Semester] = []