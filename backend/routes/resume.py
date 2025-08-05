from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import uuid
import os
from datetime import datetime

from services.resume_parser import ResumeParser
from services.vector_store import VectorStore
from utils.security import validate_file
from models.schemas import ResumeUploadResponse

router = APIRouter()

resume_parser = ResumeParser()
vector_store = VectorStore()

UPLOAD_DIR = "uploads"

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """Upload and parse a resume file"""
    
    # Validate file
    is_valid, error = validate_file(file)
    if not is_valid:
        raise HTTPException(400, error)
    
    # Generate unique ID
    resume_id = str(uuid.uuid4())
    
    # Save file
    file_extension = file.filename.split(".")[-1].lower()
    file_path = os.path.join(UPLOAD_DIR, f"{resume_id}.{file_extension}")
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Parse resume
        parsed_content = resume_parser.parse(file_path)
        
        if not parsed_content:
            raise HTTPException(400, "Failed to parse resume content")
        
        # Extract key information
        extracted_info = resume_parser.extract_info(parsed_content)
        
        # Store in vector store
        vector_store.store_resume(
            resume_id=resume_id,
            content=parsed_content,
            metadata={
                "filename": file.filename,
                "uploaded_at": datetime.utcnow(),
                "extracted_info": extracted_info
            }
        )
        
        return ResumeUploadResponse(
            resume_id=resume_id,
            filename=file.filename,
            content_preview=parsed_content[:500] + "..." if len(parsed_content) > 500 else parsed_content,
            extracted_info=extracted_info,
            message="Resume uploaded and parsed successfully"
        )
        
    except Exception as e:
        # Clean up file if error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Error processing resume: {str(e)}")

@router.get("/{resume_id}")
async def get_resume(resume_id: str):
    """Get resume details by ID"""
    
    resume_data = vector_store.get_resume(resume_id)
    
    if not resume_data:
        raise HTTPException(404, "Resume not found")
    
    return {
        "resume_id": resume_id,
        "content": resume_data.get("content"),
        "metadata": resume_data.get("metadata")
    }

@router.delete("/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete a resume and its associated data"""
    
    # Check if resume exists
    resume_data = vector_store.get_resume(resume_id)
    if not resume_data:
        raise HTTPException(404, "Resume not found")
    
    # Delete from vector store
    vector_store.delete_resume(resume_id)
    
    # Delete file if exists
    for ext in ["pdf", "docx"]:
        file_path = os.path.join(UPLOAD_DIR, f"{resume_id}.{ext}")
        if os.path.exists(file_path):
            os.remove(file_path)
            break
    
    return {
        "message": "Resume deleted successfully",
        "resume_id": resume_id
    } 