import os
from typing import List, Dict, Any
import openai
from openai import OpenAI  # Change to sync client
import json
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Using fallback mode.")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = "gpt-4o-mini"  # Using mini for demo, switch to gpt-4o for production
    
    async def generate_question(
        self, 
        role: str, 
        resume_context: str = "",
        question_number: int = 1
    ) -> Dict[str, Any]:
        """Generate an interview question based on role and resume"""
        
        if not self.client:
            return self._get_fallback_question(role, question_number)
        
        system_prompt = f"""You are an expert {role.replace('_', ' ')} interviewer at LinkedIn.
        Generate thoughtful interview questions that assess both technical skills and cultural fit.
        Mix behavioral and technical questions appropriately."""
        
        user_prompt = f"""Generate interview question #{question_number} for a {role.replace('_', ' ')} candidate.
        
        {'Resume context: ' + resume_context[:1000] if resume_context else 'No resume provided.'}
        
        Return a JSON object with:
        - question: The interview question
        - type: Either "behavioral" or "technical"
        - difficulty: "easy", "medium", or "hard"
        - hints: Array of 2-3 hints for answering well
        """
        
        try:
            # Use sync client in async context
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating question: {e}")
            return self._get_fallback_question(role, question_number)
    
    def _get_fallback_question(self, role: str, question_number: int) -> Dict[str, Any]:
        """Fallback questions when API is unavailable"""
        # Fallback question
        return {
            "question": "Tell me about a challenging project you've worked on recently.",
            "type": "behavioral",
            "difficulty": "medium",
            "hints": ["Use STAR method", "Be specific about your role", "Highlight the outcome"]
        }
    
    async def generate_follow_up(
        self,
        role: str,
        resume_context: str,
        previous_qa: List[Dict],
        answer: str
    ) -> Dict[str, Any]:
        """Generate a follow-up question based on the candidate's answer"""
        
        if not self.client:
            return {
                "question": "Can you elaborate on that with a specific example?",
                "type": "behavioral",
                "rationale": "Seeking more concrete details"
            }
        
        system_prompt = f"""You are an expert {role.replace('_', ' ')} interviewer at LinkedIn.
        Based on the candidate's previous answers, ask relevant follow-up questions that dig deeper."""
        
        # Format previous Q&A
        qa_history = "\n".join([
            f"Q{i+1}: {qa['question']['question']}\nA{i+1}: {qa['answer']}"
            for i, qa in enumerate(previous_qa[-3:])  # Last 3 Q&As for context
        ])
        
        user_prompt = f"""Based on this interview so far, generate a follow-up question.
        
        Role: {role.replace('_', ' ')}
        Recent Q&A:
        {qa_history}
        
        Latest answer: {answer}
        
        Generate a thoughtful follow-up that explores their answer deeper or transitions to a new relevant topic.
        
        Return a JSON object with:
        - question: The follow-up question
        - type: "behavioral" or "technical"
        - rationale: Why you're asking this question
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            return {
                "question": "Can you elaborate on that with a specific example?",
                "type": "behavioral",
                "rationale": "Seeking more concrete details"
            }
    
    async def generate_feedback(
        self,
        role: str,
        qa_pairs: List[Dict]
    ) -> Dict[str, Any]:
        """Generate comprehensive interview feedback"""
        
        if not self.client:
            # Return default feedback
            return {
                "score": 7.0,
                "strengths": [
                    "Good communication skills",
                    "Structured answers",
                    "Relevant examples"
                ],
                "improvements": [
                    "Provide more specific technical details",
                    "Quantify impact when possible",
                    "Ask clarifying questions"
                ],
                "flashcards": [
                    {
                        "front": "STAR Method",
                        "back": "Situation, Task, Action, Result - structure for behavioral answers"
                    },
                    {
                        "front": "Active Listening",
                        "back": "Fully understand the question before answering, ask for clarification if needed"
                    }
                ]
            }
        
        system_prompt = """You are an expert interview coach providing constructive feedback.
        Analyze the interview performance and provide actionable insights."""
        
        # Format all Q&A pairs
        qa_text = "\n\n".join([
            f"Question {i+1}: {qa['question']['question']}\nAnswer: {qa['answer']}"
            for i, qa in enumerate(qa_pairs)
        ])
        
        user_prompt = f"""Analyze this {role.replace('_', ' ')} interview and provide feedback.
        
        Interview transcript:
        {qa_text}
        
        Provide a JSON response with:
        - score: Overall score out of 10
        - strengths: Array of 3-4 key strengths observed
        - improvements: Array of 3-4 areas for improvement
        - flashcards: Array of 3-5 flashcard objects, each with "front" (concept/question) and "back" (key points to remember)
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            # Fallback feedback
            return {
                "score": 7.0,
                "strengths": [
                    "Good communication skills",
                    "Structured answers",
                    "Relevant examples"
                ],
                "improvements": [
                    "Provide more specific technical details",
                    "Quantify impact when possible",
                    "Ask clarifying questions"
                ],
                "flashcards": [
                    {
                        "front": "STAR Method",
                        "back": "Situation, Task, Action, Result - structure for behavioral answers"
                    },
                    {
                        "front": "Active Listening",
                        "back": "Fully understand the question before answering, ask for clarification if needed"
                    }
                ]
            } 