from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List
import models
from auth import get_current_user

router = APIRouter()

# Skill requirements per career role
SKILLS_MAP = {
    "Software Engineer": ["Java", "C++", "Python", "Problem Solving", "Data Structures", "Algorithms", "Git", "SQL"],
    "Data Scientist": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Tableau", "Statistics"],
    "Frontend Developer": ["JavaScript", "HTML", "CSS", "React", "Vue", "TypeScript", "TailwindCSS"],
    "Backend Developer": ["Python", "Java", "Node.js", "Express", "Django", "SQL", "PostgreSQL", "REST API", "Docker"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "AWS", "SQL"],
    "DevOps Engineer": ["Linux", "Bash", "Docker", "Kubernetes", "AWS", "Azure", "Git", "CI/CD"]
}

COURSE_RECOMMENDATIONS = {
    "Java": "Java Programming Masterclass – Udemy",
    "Python": "100 Days of Code: The Complete Python Pro Bootcamp – Udemy",
    "React": "React – The Complete Guide (incl Hooks, React Router, Redux) – Udemy",
    "Machine Learning": "Machine Learning A-Z: AI, Python & R – Udemy",
    "Docker": "Docker Mastery: with Kubernetes +Swarm – Udemy",
    "AWS": "Ultimate AWS Certified Solutions Architect Associate – Udemy",
    "SQL": "The Complete SQL Bootcamp – Udemy",
    "JavaScript": "The Complete JavaScript Course – Udemy",
    "TypeScript": "Understanding TypeScript – Udemy",
    "Node.js": "Node.js – The Complete Guide – Udemy",
    "Kubernetes": "Kubernetes Mastery – Udemy",
    "TensorFlow": "TensorFlow Developer Certificate in 2024 – Udemy",
    "PyTorch": "PyTorch for Deep Learning Bootcamp – Udemy",
    "Data Structures": "Data Structures and Algorithms Bootcamp – Coursera",
    "Algorithms": "Algorithms Specialization – Coursera (Stanford)",
    "Linux": "Linux Command Line Basics – Coursera",
    "Deep Learning": "Deep Learning Specialization – Coursera (Andrew Ng)",
    "C++": "Beginning C++ Programming – Udemy",
    "PostgreSQL": "The Complete PostgreSQL Bootcamp – Udemy",
    "Pandas": "Data Analysis with Python – freeCodeCamp",
    "NumPy": "NumPy Tutorial for Beginners – YouTube / Coursera",
    "Scikit-Learn": "Machine Learning with scikit-learn – Coursera",
    "Tableau": "Tableau 2024 A-Z: Hands-On Tableau Training – Udemy",
}

@router.post("/generate")
def generate_roadmap(
    predicted_role: str = Query(..., description="The predicted career role"),
    user_skills: List[str] = Body(..., description="List of the user's current skills"),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a personalized learning roadmap based on the predicted career role
    and the user's current skill set.
    """
    if predicted_role not in SKILLS_MAP:
        raise HTTPException(
            status_code=404,
            detail=f"No roadmap defined for role: '{predicted_role}'. Available roles: {list(SKILLS_MAP.keys())}"
        )

    required_skills = set(SKILLS_MAP[predicted_role])
    current_skills = set(user_skills)

    # Case-insensitive skill gap calculation
    required_lower = {s.lower(): s for s in required_skills}
    current_lower = {s.lower() for s in current_skills}

    missing_keys = set(required_lower.keys()) - current_lower
    missing_skills = [required_lower[k] for k in missing_keys]

    courses = []
    for skill in missing_skills:
        course = COURSE_RECOMMENDATIONS.get(skill, f"Introductory {skill} Course on Coursera/Udemy")
        courses.append({"skill": skill, "course": course})

    match_pct = round(
        (len(required_skills) - len(missing_skills)) / len(required_skills) * 100, 1
    ) if required_skills else 0

    return {
        "role": predicted_role,
        "required_skills": sorted(list(required_skills)),
        "existing_skills": sorted(list(current_skills)),
        "missing_skills": sorted(missing_skills),
        "recommended_courses": courses,
        "match_percentage": match_pct
    }
