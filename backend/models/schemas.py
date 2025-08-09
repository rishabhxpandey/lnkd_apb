from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Interview Models
class InterviewStartResponse(BaseModel):
    session_id: str
    role: str
    question: str
    question_type: str = Field(default="behavioral")

class AnswerRequest(BaseModel):
    session_id: str
    answer: str = Field(..., min_length=1, max_length=5000)

class AnswerResponse(BaseModel):
    session_id: str
    is_complete: bool
    question: Optional[str] = None
    question_type: Optional[str] = None
    question_number: Optional[int] = None
    message: Optional[str] = None

class Flashcard(BaseModel):
    front: str
    back: str

class FeedbackResponse(BaseModel):
    session_id: str
    overall_score: float = Field(..., ge=0, le=10)
    strengths: List[str]
    improvements: List[str]
    flashcards: List[Flashcard]
    completed_at: datetime

# Resume Models
class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    content_preview: str
    extracted_info: Dict[str, Any]
    message: str

class ResumeInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    skills: List[str] = []
    education: List[str] = []
    experience: List[str] = []
    summary: str = ""

# Job Models
class JobUploadRequest(BaseModel):
    url: str = Field(..., description="LinkedIn job posting URL")

class JobUploadResponse(BaseModel):
    job_id: str
    url: str
    title: str
    company: str
    description_preview: str
    post_date: Optional[str] = None
    message: str

class JobData(BaseModel):
    job_id: str
    url: str
    title: str
    company: str
    description: str
    post_date: Optional[str] = None
    scraped_at: str
    source: str = "linkedin"

# Error Models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int 