import os
from typing import List, Dict, Any
import openai
from openai import OpenAI  # Change to sync client
import json
from dotenv import load_dotenv
import asyncio
import httpx
from jinja2 import Environment, FileSystemLoader

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Using fallback mode.")
        
        # Create OpenAI client with custom HTTP client to avoid proxy issues
        if api_key:
            # Create httpx client without proxy for OpenAI API calls
            http_client = httpx.Client(
                proxies=None,  # Explicitly disable proxy for OpenAI
                trust_env=False  # Don't use environment proxy settings
            )
            self.client = OpenAI(
                api_key=api_key,
                http_client=http_client
            )
        else:
            self.client = None
        self.model = "gpt-4o-mini"  # Using mini for demo, switch to gpt-4o for production
        
        # Setup Jinja2 environment for templates
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def generate_question(
        self, 
        role: str, 
        resume_context: str = "",
        question_number: int = 1,
        skills: str = "",
        job_requirements: str = ""
    ) -> Dict[str, Any]:
        """Generate an interview question based on role and resume"""
        
        if not self.client:
            return self._get_fallback_question(role, question_number)
        
        # Load and render the Jinja2 template
        template = self.jinja_env.get_template('base_question.jinja')
        user_prompt = template.render(
            role=role,
            question_number=question_number,
            resume_context=resume_context,
            skills=skills,
            job_requirements=job_requirements
        )
        
        system_prompt = "You are an expert interviewer. Follow the instructions carefully."
        
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