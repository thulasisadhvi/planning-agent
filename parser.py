# parser.py
import pdfplumber
import re
from models import Course

def parse_transcript(file_path: str) -> list[Course]:
    completed_courses = []
    # Looks for: [2-4 Letters] [3-4 Numbers] [Any Title] [1-2 Digit Credits]
    # Example: "CS 101 Intro to Programming 3"
    course_pattern = re.compile(r'([A-Z]{2,4}\s\d{3,4})\s+(.+?)\s+(\d{1,2})$')

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        match = course_pattern.search(line.strip())
                        if match:
                            completed_courses.append(Course(
                                course_code=match.group(1).strip(),
                                title=match.group(2).strip(),
                                credits=int(match.group(3).strip()),
                                schedule=[] # Past courses don't strictly need schedules
                            ))
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        
    return completed_courses