import os
import shutil
import pdfplumber
import docx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import models
from database import get_db
from auth import get_current_user
from nlp_service import extract_skills_from_text

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are allowed.")
        
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.user_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    extracted_text = ""
    try:
        if file.filename.endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            extracted_text = extract_text_from_docx(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")
        
    new_resume = models.Resume(
        user_id=current_user.user_id,
        file_path=file_path,
        parsed_text=extracted_text
    )
    
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    # Run NLP skills extraction
    extracted_skills = extract_skills_from_text(extracted_text)
    
    return {
        "message": "Resume uploaded and parsed successfully",
        "resume_id": new_resume.resume_id,
        "extracted_skills": extracted_skills,
        "parsed_text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
    }
