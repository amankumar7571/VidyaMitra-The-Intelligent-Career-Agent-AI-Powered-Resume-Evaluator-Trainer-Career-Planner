import pandas as pd
import numpy as np
import random
import os

# Ensure directories exist
os.makedirs("data", exist_ok=True)

# Define our role labels
ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Frontend Developer",
    "Backend Developer",
    "Machine Learning Engineer",
    "DevOps Engineer"
]

# Base skills mapped loosely to roles
SKILLS_MAP = {
    "Software Engineer": ["Java", "C++", "Python", "Problem Solving", "Data Structures", "Algorithms", "Git", "SQL"],
    "Data Scientist": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Tableau", "Statistics"],
    "Frontend Developer": ["JavaScript", "HTML", "CSS", "React", "Vue", "TypeScript", "TailwindCSS"],
    "Backend Developer": ["Python", "Java", "Node.js", "Express", "Django", "SQL", "PostgreSQL", "REST API", "Docker"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "AWS", "SQL"],
    "DevOps Engineer": ["Linux", "Bash", "Docker", "Kubernetes", "AWS", "Azure", "Git", "CI/CD"]
}

# ALL possible skills for one-hot encoding feature vectors later
ALL_SKILLS = sorted(list(set(skill for skills in SKILLS_MAP.values() for skill in skills)))

def generate_synthetic_data(num_samples=1000):
    data = []
    for _ in range(num_samples):
        # Pick a target role
        target_role = random.choice(ROLES)
        
        # Pick 3 to 7 skills from the target role's core skills
        core_skills = SKILLS_MAP[target_role]
        num_skills = random.randint(3, len(core_skills))
        user_skills = random.sample(core_skills, num_skills)
        
        # Optionally add 0-2 random noise skills
        noise_skills = random.sample(ALL_SKILLS, random.randint(0, 2))
        final_skills = list(set(user_skills + noise_skills))
        
        # Random numerical features
        cgpa = round(random.uniform(6.0, 10.0), 2)
        project_count = random.randint(0, 5)
        
        # Encode skills as 0 or 1 for ML training ease
        row = {
            "Role": target_role,
            "CGPA": cgpa,
            "Project_Count": project_count
        }
        for skill in ALL_SKILLS:
            row[skill] = 1 if skill in final_skills else 0
            
        data.append(row)
        
    df = pd.DataFrame(data)
    df.to_csv("data/synthetic_career_data.csv", index=False)
    print(f"Generated {num_samples} records in data/synthetic_career_data.csv")
    return df

if __name__ == "__main__":
    generate_synthetic_data(1500)
