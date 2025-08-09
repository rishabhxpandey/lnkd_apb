import os
import base64
import json
from typing import Dict, Any, Optional
import pdfplumber
from docx import Document
from openai import OpenAI
import httpx
from dotenv import load_dotenv
import asyncio
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

# Load environment variables
load_dotenv()

class GPTResumeParser:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Using fallback text extraction mode.")
        
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
        
        self.model = "gpt-4o-mini"
    
    async def parse(self, file_path: str) -> Optional[str]:
        """Parse resume file using Vision API and return extracted text"""
        
        if not os.path.exists(file_path):
            return None
        
        if not self.client:
            raise ValueError("OpenAI API key is required for GPTResumeParser. Please set OPENAI_API_KEY environment variable.")
        
        file_extension = file_path.split(".")[-1].lower()
        
        if file_extension not in ["pdf", "docx"]:
            raise ValueError(f"Unsupported file format: {file_extension}. Only PDF and DOCX are supported.")
        
        # Use Vision API to extract text from the document
        return await self._extract_text_with_vision(file_path)
    
    async def _extract_text_with_vision(self, file_path: str) -> str:
        """Extract text from document using Vision API"""
        
        try:
            # Convert file to base64 image
            image_base64 = self._convert_file_to_image_base64(file_path)
            
            if not image_base64:
                raise ValueError(f"Failed to convert {file_path} to image for Vision API")
            
            system_prompt = """You are an expert document reader. Extract ALL text content from this resume document image.
            
Return the complete text exactly as it appears in the document, maintaining the original structure and formatting as much as possible.
            Do not add any commentary, analysis, or formatting - just return the raw text content."""
            
            # Use Vision API to extract text
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all text from this resume document."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error extracting text with Vision API: {e}")
            raise
    
    def _convert_file_to_image_base64(self, file_path: str) -> Optional[str]:
        """Convert PDF/DOCX file to base64 image for Vision API"""
        
        try:
            if file_path.lower().endswith('.pdf'):
                return self._convert_pdf_to_image(file_path)
            elif file_path.lower().endswith('.docx'):
                return self._convert_docx_to_image(file_path)
            else:
                return None
                
        except Exception as e:
            print(f"Error converting file to image: {e}")
            return None
    
    def _convert_pdf_to_image(self, file_path: str) -> Optional[str]:
        """Convert PDF first page to base64 image"""
        try:
            with pdfplumber.open(file_path) as pdf:
                if pdf.pages:
                    # Get first page as image
                    page = pdf.pages[0]
                    img = page.within_bbox((0, 0, page.width, page.height)).to_image()
                    
                    # Convert PIL Image to base64
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    img_bytes = buffer.getvalue()
                    return base64.b64encode(img_bytes).decode('utf-8')
            return None
        except Exception as e:
            print(f"Error converting PDF to image: {e}")
            return None
    
    def _convert_docx_to_image(self, file_path: str) -> Optional[str]:
        """Convert DOCX to image using python-docx and additional libraries"""
        try:
            # For DOCX files, we need to convert to image
            # This requires additional libraries like python-docx2txt and PIL
            # For now, we'll extract text and create a simple text image
            
            doc = Document(file_path)
            text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])
            
            # Create a simple text image using PIL
            
            # Create image with text
            img_width, img_height = 800, 1200
            img = Image.new('RGB', (img_width, img_height), color='white')
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a better font
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
            
            # Wrap text and draw it
            wrapped_text = textwrap.fill(text_content[:2000], width=80)  # Limit text length
            
            y_position = 10
            for line in wrapped_text.split('\n'):
                if y_position > img_height - 30:
                    break
                draw.text((10, y_position), line, fill='black', font=font)
                y_position += 20
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            return base64.b64encode(img_bytes).decode('utf-8')
            
        except Exception as e:
            print(f"Error converting DOCX to image: {e}")
            return None
    
    async def extract_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from resume text using GPT"""
        
        if not self.client:
            raise ValueError("OpenAI API key is required for GPTResumeParser. Please set OPENAI_API_KEY environment variable.")
        
        try:
            # Use GPT-4o-mini to extract structured information from text
            system_prompt = """You are an expert resume parser. Extract structured information from the provided resume text and return it as JSON.

Extract the following information:
- email: Email address (string or null)
- phone: Phone number (string or null) 
- linkedin: LinkedIn URL (string or null)
- github: GitHub URL (string or null)
- skills: Array of technical skills (array of strings)
- education: Array of education entries with degree, institution, and year if available (array of strings)
- experience: Array of work experience entries with role, company, and duration if available (array of strings)
- summary: Professional summary or objective (string, max 500 chars)

Return only valid JSON without any markdown formatting or additional text."""
            
            user_prompt = f"""Parse this resume text and extract structured information:

{text[:4000]}  # Truncate to avoid token limits

Return the information as JSON matching this structure:
{{
    "email": "email@example.com or null",
    "phone": "+1234567890 or null", 
    "linkedin": "https://linkedin.com/in/username or null",
    "github": "https://github.com/username or null",
    "skills": ["Python", "JavaScript", "etc"],
    "education": ["Bachelor of Science in Computer Science, University Name, 2020"],
    "experience": ["Software Engineer at Company Name (2020-2023)"],
    "summary": "Professional summary here"
}}"""
            
            # Use sync client in async context
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all required fields are present with proper defaults
            structured_info = {
                "email": result.get("email"),
                "phone": result.get("phone"),
                "linkedin": result.get("linkedin"),
                "github": result.get("github"),
                "skills": result.get("skills", []),
                "education": result.get("education", []),
                "experience": result.get("experience", []),
                "summary": result.get("summary", "")
            }
            
            return structured_info
            
        except Exception as e:
            print(f"Error with GPT extraction: {e}")
            raise
    
    async def extract_info_from_image(self, file_path: str) -> Dict[str, Any]:
        """Extract structured information directly from resume image using GPT Vision"""
        
        if not self.client:
            raise ValueError("OpenAI API key is required for GPTResumeParser. Please set OPENAI_API_KEY environment variable.")
        
        # Convert file to base64 image
        image_base64 = self._convert_file_to_image_base64(file_path)
        
        if not image_base64:
            raise ValueError(f"Failed to convert {file_path} to image for Vision API")
        
        try:
            system_prompt = """You are an expert resume parser with vision capabilities. Analyze the resume image and extract structured information.

Extract the following information:
- email: Email address (string or null)
- phone: Phone number (string or null)
- linkedin: LinkedIn URL (string or null) 
- github: GitHub URL (string or null)
- skills: Array of technical skills (array of strings)
- education: Array of education entries (array of strings)
- experience: Array of work experience entries (array of strings)
- summary: Professional summary or objective (string, max 500 chars)

Return only valid JSON without any markdown formatting."""
            
            # Use sync client in async context
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this resume image and extract the structured information as JSON."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all required fields are present
            structured_info = {
                "email": result.get("email"),
                "phone": result.get("phone"),
                "linkedin": result.get("linkedin"),
                "github": result.get("github"),
                "skills": result.get("skills", []),
                "education": result.get("education", []),
                "experience": result.get("experience", []),
                "summary": result.get("summary", "")
            }
            
            return structured_info
            
        except Exception as e:
            print(f"Error with GPT Vision extraction: {e}")
            raise
    

