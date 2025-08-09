from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from models.schemas import (
    InterviewStartResponse,
    AnswerRequest,
    AnswerResponse,
    FeedbackResponse
)
from services.llm_service import LLMService
from services.vector_store import VectorStore

router = APIRouter()

# In-memory session storage (use Redis/DB in production)
sessions: Dict[str, Dict[str, Any]] = {}

llm_service = LLMService()
vector_store = VectorStore()

@router.get("/debug/jobs")
async def debug_jobs():
    """Debug endpoint to see all stored jobs"""
    all_jobs = vector_store.get_all_jobs()
    jobs_detail = []
    for job_id in all_jobs:
        job_data = vector_store.get_job(job_id)
        if job_data:
            jobs_detail.append({
                "job_id": job_id,
                "title": job_data.get("title", ""),
                "company": job_data.get("company", ""),
                "description_preview": job_data.get("description", "")[:200]
            })
    
    # Also check metadata directly
    metadata_info = []
    for key, value in vector_store.metadata.items():
        if key.startswith("job_"):
            metadata_info.append({
                "key": key,
                "has_job_data": "job_data" in value,
                "index_id": value.get("index_id", "unknown")
            })
    
    return {
        "total_jobs": len(all_jobs),
        "job_ids": all_jobs,
        "jobs": jobs_detail,
        "metadata_debug": metadata_info
    }

@router.get("/start", response_model=InterviewStartResponse)
async def start_interview(
    role: str = Query(..., description="Role to interview for"),
    resume_id: Optional[str] = Query(None, description="Resume ID for personalization"),
    job_id: Optional[str] = Query(None, description="Job ID for job-specific questions")
):
    """Start a new interview session"""
    
    print(f"Starting interview - Role: {role}, Resume ID: {resume_id}, Job ID: {job_id}")
    
    # Validate role
    valid_roles = ["software_engineer", "product_manager", "data_scientist"]
    if role not in valid_roles:
        raise HTTPException(400, f"Invalid role. Choose from: {valid_roles}")
    
    # Create session
    session_id = str(uuid.uuid4())
    
    # Get resume context if provided
    resume_context = ""
    if resume_id:
        resume_data = vector_store.get_resume(resume_id)
        if resume_data:
            resume_context = resume_data.get("content", "")
    
    # Get job context if provided
    job_requirements = ""
    skills = ""
    if job_id:
        print(f"Looking for job with ID: {job_id}")
        # Debug: Show all available job IDs
        all_jobs = vector_store.get_all_jobs()
        print(f"Available job IDs: {all_jobs}")
        
        job_data = vector_store.get_job(job_id)
        if job_data:
            job_requirements = job_data.get("description", "")
            # Extract skills from job title and description for more targeted questions
            skills = f"{job_data.get('title', '')} at {job_data.get('company', '')}"
            print(f"Found job: {skills}")
            print(f"Job requirements length: {len(job_requirements)} characters")
        else:
            print(f"No job found with ID: {job_id}")
            print("Trying to debug job storage...")
            # Try different ID formats
            alt_job_id = job_id.replace("linkedin_", "") if job_id.startswith("linkedin_") else f"linkedin_{job_id}"
            alt_job_data = vector_store.get_job(alt_job_id)
            if alt_job_data:
                print(f"Found job with alternative ID: {alt_job_id}")
                job_data = alt_job_data
                job_requirements = job_data.get("description", "")
                skills = f"{job_data.get('title', '')} at {job_data.get('company', '')}"
    else:
        print("No job ID provided")
    
    # Generate first question
    first_question = await llm_service.generate_question(
        role=role,
        resume_context=resume_context,
        question_number=1,
        skills=skills,
        job_requirements=job_requirements
    )
    
    # Store session
    sessions[session_id] = {
        "id": session_id,
        "role": role,
        "resume_id": resume_id,
        "job_id": job_id,
        "resume_context": resume_context,
        "job_requirements": job_requirements,
        "skills": skills,
        "started_at": datetime.utcnow(),
        "questions": [first_question],
        "answers": [],
        "current_question": 0
    }
    
    return InterviewStartResponse(
        session_id=session_id,
        role=role,
        question=first_question.get("question"),
        question_type=first_question.get("type", "behavioral")
    )

@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest):
    """Submit an answer and get the next question or complete the session"""
    
    # Get session
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    # Store answer
    session["answers"].append({
        "question": session["questions"][session["current_question"]],
        "answer": request.answer,
        "answered_at": datetime.utcnow()
    })
    
    # Check if interview is complete (5 questions)
    if len(session["answers"]) >= 5:
        return AnswerResponse(
            session_id=request.session_id,
            is_complete=True,
            message="Interview complete! Get your feedback at /api/interview/feedback/{session_id}"
        )
    
    # Generate follow-up question based on the answer
    follow_up = await llm_service.generate_follow_up(
        role=session["role"],
        resume_context=session["resume_context"],
        previous_qa=session["answers"],
        answer=request.answer,
        job_requirements=session.get("job_requirements", ""),
        skills=session.get("skills", "")
    )
    
    # Add to questions
    session["questions"].append(follow_up)
    session["current_question"] += 1
    
    return AnswerResponse(
        session_id=request.session_id,
        is_complete=False,
        question=follow_up.get("question"),
        question_type=follow_up.get("type", "technical"),
        question_number=len(session["answers"]) + 1
    )

@router.get("/feedback/{session_id}", response_model=FeedbackResponse)
async def get_feedback(session_id: str):
    """Get interview feedback and improvement suggestions"""
    
    # Get session
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    # Check if interview is complete
    if len(session["answers"]) < 5:
        raise HTTPException(400, "Interview not yet complete")
    
    # Generate feedback
    feedback_data = await llm_service.generate_feedback(
        role=session["role"],
        qa_pairs=session["answers"]
    )
    
    return FeedbackResponse(
        session_id=session_id,
        overall_score=feedback_data.get("score", 7.5),
        strengths=feedback_data.get("strengths", []),
        improvements=feedback_data.get("improvements", []),
        flashcards=feedback_data.get("flashcards", []),
        completed_at=datetime.utcnow()
    ) 