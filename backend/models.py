from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    cgpa = Column(Float, nullable=True)
    interests = Column(Text, nullable=True)

    resumes = relationship("Resume", back_populates="user")
    skills = relationship("UserSkill", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"
    resume_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    file_path = Column(String)
    parsed_text = Column(Text, nullable=True)
    upload_date = Column(Date, default=datetime.date.today)

    user = relationship("User", back_populates="resumes")

class Skill(Base):
    __tablename__ = "skills"
    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, unique=True, index=True)
    category = Column(String, nullable=True)

class UserSkill(Base):
    __tablename__ = "user_skills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    proficiency = Column(String, nullable=True)

    user = relationship("User", back_populates="skills")
    skill = relationship("Skill")

class CareerRole(Base):
    __tablename__ = "career_roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)

class RoleSkill(Base):
    __tablename__ = "role_skills"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("career_roles.role_id"))
    skill_id = Column(Integer, ForeignKey("skills.skill_id"))
    importance_level = Column(Integer, nullable=True)

    role = relationship("CareerRole")
    skill = relationship("Skill")

class Prediction(Base):
    __tablename__ = "predictions"
    prediction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    predicted_role = Column(String)
    confidence_score = Column(Float)
    prediction_date = Column(Date, default=datetime.date.today)

    user = relationship("User", back_populates="predictions")

class Roadmap(Base):
    __tablename__ = "roadmaps"
    roadmap_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("career_roles.role_id"))
    skills_to_learn = Column(Text)
    courses = Column(Text)
    projects = Column(Text)

    role = relationship("CareerRole")
