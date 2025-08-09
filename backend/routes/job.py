from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import datetime

from models.schemas import (
    JobUploadRequest,
    JobUploadResponse,
    JobData,
    ErrorResponse
)
from services.job_scraper import JobScraper
from services.vector_store import VectorStore

router = APIRouter()

# Initialize services
job_scraper = JobScraper()
vector_store = VectorStore()

@router.post("/upload", response_model=JobUploadResponse)
async def upload_job(request: JobUploadRequest):
    """Scrape and store LinkedIn job posting"""
    
    try:
        # Validate URL format
        if not request.url.strip():
            raise HTTPException(400, "Job URL is required")
        
        url = request.url.strip()
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        print(f"Starting job scrape for: {url}")
        
        # Scrape job data using Playwright
        scraped_data = await job_scraper.scrape_job(url)
        
        # Use the LinkedIn job ID if available, otherwise use our UUID
        linkedin_job_id = scraped_data.get("job_id", job_id)
        final_job_id = f"linkedin_{linkedin_job_id}"
        
        # Prepare job data for storage
        job_data = {
            "job_id": final_job_id,
            "url": scraped_data["url"],
            "title": scraped_data["title"],
            "company": scraped_data["company"],
            "description": scraped_data["description"],
            "post_date": scraped_data.get("post_date"),
            "scraped_at": scraped_data["scraped_at"],
            "source": scraped_data.get("source", "linkedin"),
            "original_job_id": linkedin_job_id
        }
        
        # Store in vector store
        vector_store.store_job(final_job_id, job_data)
        
        print(f"Job stored successfully with ID: {final_job_id}")
        
        return JobUploadResponse(
            job_id=final_job_id,
            url=job_data["url"],
            title=job_data["title"],
            company=job_data["company"],
            description_preview=job_data["description"][:500] + "..." if len(job_data["description"]) > 500 else job_data["description"],
            post_date=job_data.get("post_date"),
            message="Job posting scraped and stored successfully"
        )
        
    except ValueError as e:
        # Handle validation errors from scraper
        raise HTTPException(400, str(e))
    
    except Exception as e:
        print(f"Error processing job upload: {e}")
        raise HTTPException(500, f"Failed to process job posting: {str(e)}")

@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get job details by ID"""
    
    job_data = vector_store.get_job(job_id)
    if not job_data:
        raise HTTPException(404, "Job not found")
    
    return {
        "job_id": job_data["job_id"],
        "url": job_data["url"],
        "title": job_data["title"],
        "company": job_data["company"],
        "description": job_data["description"],
        "post_date": job_data.get("post_date"),
        "scraped_at": job_data["scraped_at"],
        "source": job_data.get("source", "linkedin")
    }

@router.get("/")
async def list_jobs():
    """List all stored jobs"""
    
    job_ids = vector_store.get_all_jobs()
    jobs = []
    
    for job_id in job_ids:
        job_data = vector_store.get_job(job_id)
        if job_data:
            jobs.append({
                "job_id": job_data["job_id"],
                "title": job_data["title"],
                "company": job_data["company"],
                "url": job_data["url"],
                "post_date": job_data.get("post_date"),
                "scraped_at": job_data["scraped_at"]
            })
    
    return {
        "jobs": jobs,
        "total": len(jobs)
    }

@router.post("/search")
async def search_jobs(query: dict):
    """Search for similar jobs based on query"""
    
    search_query = query.get("query", "")
    limit = min(query.get("limit", 5), 20)  # Max 20 results
    
    if not search_query:
        raise HTTPException(400, "Search query is required")
    
    results = vector_store.search_similar_jobs(search_query, k=limit)
    
    return {
        "query": search_query,
        "results": results,
        "total": len(results)
    }

@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job posting"""
    
    # Check if job exists
    job_data = vector_store.get_job(job_id)
    if not job_data:
        raise HTTPException(404, "Job not found")
    
    # Delete from vector store
    vector_store.delete_job(job_id)
    
    return {"message": f"Job {job_id} deleted successfully"}

@router.post("/test-scraper")
async def test_scraper():
    """Test endpoint for scraper functionality"""
    
    try:
        test_result = await job_scraper.test_scraper()
        return {
            "status": "success",
            "message": "Scraper test completed",
            "test_data": test_result
        }
    except Exception as e:
        raise HTTPException(500, f"Scraper test failed: {str(e)}")
