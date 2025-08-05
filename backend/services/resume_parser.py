import os
from typing import Dict, Any, Optional
import pdfplumber
from docx import Document
import re

class ResumeParser:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{4,6}')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    
    def parse(self, file_path: str) -> Optional[str]:
        """Parse resume file and extract text content"""
        
        if not os.path.exists(file_path):
            return None
        
        file_extension = file_path.split(".")[-1].lower()
        
        if file_extension == "pdf":
            return self._parse_pdf(file_path)
        elif file_extension == "docx":
            return self._parse_docx(file_path)
        else:
            return None
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
        
        return text.strip()
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return ""
        
        return text.strip()
    
    def extract_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from resume text"""
        
        info = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "skills": [],
            "education": [],
            "experience": [],
            "summary": ""
        }
        
        # Extract contact info
        email_match = self.email_pattern.search(text)
        if email_match:
            info["email"] = email_match.group()
        
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            info["phone"] = phone_match.group()
        
        # Extract URLs
        urls = self.url_pattern.findall(text)
        for url in urls:
            if "linkedin.com" in url:
                info["linkedin"] = url
            elif "github.com" in url:
                info["github"] = url
        
        # Extract sections (simple heuristic approach)
        lines = text.split("\n")
        
        # Look for skills section
        skills_keywords = ["skills", "technologies", "technical skills", "core competencies"]
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in skills_keywords):
                # Extract next few lines as skills
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and not any(kw in lines[j].lower() for kw in ["experience", "education", "projects"]):
                        # Split by common delimiters
                        potential_skills = re.split(r'[,;|•·]', lines[j])
                        info["skills"].extend([s.strip() for s in potential_skills if s.strip() and len(s.strip()) < 30])
                    else:
                        break
        
        # Extract summary (usually first paragraph)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        if paragraphs:
            # First substantial paragraph is often the summary
            for para in paragraphs[:3]:
                if len(para) > 100 and not self.email_pattern.search(para):
                    info["summary"] = para[:500]
                    break
        
        # Extract experience section headers
        exp_keywords = ["experience", "work history", "employment", "professional experience"]
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in exp_keywords):
                # Look for job titles in next lines
                for j in range(i+1, min(i+20, len(lines))):
                    if lines[j].strip() and len(lines[j].strip()) > 10:
                        # Simple heuristic: lines with dates might be job entries
                        if re.search(r'\d{4}', lines[j]):
                            info["experience"].append(lines[j].strip())
                        if len(info["experience"]) >= 3:
                            break
        
        # Extract education
        edu_keywords = ["education", "academic", "qualification"]
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in edu_keywords):
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and len(lines[j].strip()) > 10:
                        if "university" in lines[j].lower() or "college" in lines[j].lower() or "school" in lines[j].lower():
                            info["education"].append(lines[j].strip())
                        elif re.search(r'(B\.?S\.?|M\.?S\.?|Ph\.?D|Bachelor|Master|MBA)', lines[j], re.I):
                            info["education"].append(lines[j].strip())
                        if len(info["education"]) >= 2:
                            break
        
        return info 