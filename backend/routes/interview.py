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

@router.get("/start", response_model=InterviewStartResponse)
async def start_interview(
    role: str = Query(..., description="Role to interview for"),
    resume_id: Optional[str] = Query(None, description="Resume ID for personalization")
):
    """Start a new interview session"""
    
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
    
    # Generate first question
    first_question = await llm_service.generate_question(
        role=role,
        resume_context=resume_context,
        question_number=1
    )
    
    # Store session
    sessions[session_id] = {
        "id": session_id,
        "role": role,
        "resume_id": resume_id,
        "resume_context": resume_context,
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
        answer=request.answer
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