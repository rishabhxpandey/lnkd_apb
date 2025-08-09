import os
from typing import Dict, Any, Optional, List
import faiss
import numpy as np
from openai import OpenAI
import json
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VectorStore:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI client: {e}")
            self.client = None
        self.embedding_model = "text-embedding-ada-002"
        self.dimension = 1536  # OpenAI embedding dimension
        
        # Initialize or load FAISS index
        self.index_path = os.getenv("VECTOR_STORE_PATH", "./vector_store")
        self.metadata_path = f"{self.index_path}_metadata.pkl"
        
        if not os.path.exists(self.index_path):
            os.makedirs(os.path.dirname(self.index_path) or ".", exist_ok=True)
        
        self._load_or_create_index()
        
    def _load_or_create_index(self):
        """Load existing index or create new one"""
        try:
            if os.path.exists(f"{self.index_path}.index"):
                self.index = faiss.read_index(f"{self.index_path}.index")
                with open(self.metadata_path, "rb") as f:
                    self.metadata = pickle.load(f)
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = {}
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = {}
    
    def _save_index(self):
        """Save index and metadata to disk"""
        try:
            faiss.write_index(self.index, f"{self.index_path}.index")
            with open(self.metadata_path, "wb") as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text using OpenAI"""
        if not self.client:
            print("No OpenAI client available for embeddings")
            return np.zeros(self.dimension, dtype=np.float32)
            
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero embedding as fallback when API is blocked
            return np.zeros(self.dimension, dtype=np.float32)
    
    def store_resume(self, resume_id: str, content: str, metadata: Dict[str, Any]):
        """Store resume content and metadata in vector store"""
        
        # Get embedding for resume content
        embedding = self._get_embedding(content[:8000])  # Limit content length
        
        # Add to FAISS index
        self.index.add(np.expand_dims(embedding, 0))
        
        # Store metadata
        index_id = self.index.ntotal - 1
        self.metadata[resume_id] = {
            "index_id": index_id,
            "content": content,
            "metadata": metadata
        }
        
        # Save to disk
        self._save_index()
    
    def get_resume(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Get resume by ID"""
        return self.metadata.get(resume_id)
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar resumes based on query"""
        
        if self.index.ntotal == 0:
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Search in FAISS
        distances, indices = self.index.search(
            np.expand_dims(query_embedding, 0), 
            min(k, self.index.ntotal)
        )
        
        # Get results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:  # Valid index
                # Find resume by index_id
                for resume_id, data in self.metadata.items():
                    if data["index_id"] == idx:
                        results.append({
                            "resume_id": resume_id,
                            "distance": float(distance),
                            "content": data["content"][:500],  # Preview
                            "metadata": data["metadata"]
                        })
                        break
        
        return results
    
    def delete_resume(self, resume_id: str):
        """Delete resume from vector store"""
        
        if resume_id in self.metadata:
            # Note: FAISS doesn't support deletion, so we just remove metadata
            # In production, you'd want to rebuild the index periodically
            del self.metadata[resume_id]
            self._save_index()
    
    def get_all_resumes(self) -> List[str]:
        """Get all resume IDs"""
        return [k for k, v in self.metadata.items() if not k.startswith("job_")]
    
    def store_job(self, job_id: str, job_data: Dict[str, Any]):
        """Store job description and metadata in vector store"""
        
        try:
            # Create searchable content from job data
            searchable_content = f"""
            {job_data.get('title', '')}
            {job_data.get('company', '')}
            {job_data.get('description', '')}
            """.strip()
            
            # Try to get embedding for job content
            try:
                embedding = self._get_embedding(searchable_content[:8000])  # Limit content length
                
                # Add to FAISS index
                self.index.add(np.expand_dims(embedding, 0))
                index_id = self.index.ntotal - 1
                print(f"Successfully created embedding for job {job_id}")
            except Exception as embed_error:
                print(f"Failed to create embedding for job {job_id}: {embed_error}")
                # Store without FAISS index when embeddings fail
                index_id = -1  # Special value indicating no embedding
            
            # Store metadata with job_ prefix to distinguish from resumes
            job_key = f"job_{job_id}"
            self.metadata[job_key] = {
                "index_id": index_id,
                "content": searchable_content,
                "job_data": job_data,
                "type": "job_description"
            }
            
            print(f"Stored job metadata for {job_id} with index_id: {index_id}")
            
            # Save to disk
            self._save_index()
            
        except Exception as e:
            print(f"Failed to store job {job_id}: {e}")
            raise e
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        job_key = f"job_{job_id}"
        job_entry = self.metadata.get(job_key)
        if job_entry:
            return job_entry.get("job_data")
        return None
    
    def search_similar_jobs(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar jobs based on query"""
        
        if self.index.ntotal == 0:
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Search in FAISS
        distances, indices = self.index.search(
            np.expand_dims(query_embedding, 0), 
            min(k, self.index.ntotal)
        )
        
        # Get job results only
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:  # Valid index
                # Find job by index_id
                for key, data in self.metadata.items():
                    if key.startswith("job_") and data["index_id"] == idx:
                        job_data = data["job_data"]
                        results.append({
                            "job_id": job_data["job_id"],
                            "distance": float(distance),
                            "title": job_data["title"],
                            "company": job_data["company"],
                            "description_preview": job_data["description"][:500],
                            "job_data": job_data
                        })
                        break
        
        return results
    
    def get_all_jobs(self) -> List[str]:
        """Get all job IDs"""
        return [k.replace("job_", "") for k in self.metadata.keys() if k.startswith("job_")]
    
    def delete_job(self, job_id: str):
        """Delete job from vector store"""
        job_key = f"job_{job_id}"
        if job_key in self.metadata:
            # Note: FAISS doesn't support deletion, so we just remove metadata
            # In production, you'd want to rebuild the index periodically
            del self.metadata[job_key]
            self._save_index() 