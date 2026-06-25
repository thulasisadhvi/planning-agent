# tools.py
from typing import List, Dict, Any
from langchain_core.tools import tool

# A small mock database to simulate the University Catalog MCP
MOCK_CATALOG = [
    {"course_code": "CS301", "title": "Intro to AI", "credits": 3, "schedule": [("Mon", "10:00", "11:30")]},
    {"course_code": "CS302", "title": "Machine Learning", "credits": 3, "schedule": [("Wed", "10:00", "11:30")]},
    {"course_code": "MATH201", "title": "Linear Algebra", "credits": 4, "schedule": [("Tue", "09:00", "10:30")]},
    {"course_code": "CS401", "title": "Advanced AI", "credits": 3, "schedule": [("Mon", "10:00", "11:30")]} # Intentional conflict with CS301
]

@tool
def search_courses(query: str, semester: str) -> List[Dict[str, Any]]:
    """Searches the university catalog for courses matching a query in a specific semester.
    
    Args:
        query (str): The search query (e.g., 'AI', 'Machine Learning', or 'CS301').
        semester (str): The semester to search in (e.g., 'Fall 2024').
        
    Returns:
        A list of courses, each as a dictionary with keys 'course_code', 'title', 'credits', 'schedule'.
    """
    # Mock implementation of searching the catalog
    results = []
    for course in MOCK_CATALOG:
        if query.lower() in course['title'].lower() or query.lower() in course['course_code'].lower():
            results.append(course)
    return results

# List of tools to bind to the agent
tools = [search_courses]