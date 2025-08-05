import os
import re
from typing import Tuple
from fastapi import UploadFile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MAX_FILE_SIZE_MB = int(os.getenv("UPLOAD_MAX_SIZE_MB", "10"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx").split(",")

def validate_file(file: UploadFile) -> Tuple[bool, str]:
    """Validate uploaded file for security and format"""
    
    # Check filename
    if not file.filename:
        return False, "No filename provided"
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    if not safe_filename:
        return False, "Invalid filename"
    
    # Check extension
    extension = safe_filename.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check content type
    allowed_content_types = {
        "pdf": ["application/pdf"],
        "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    }
    
    if file.content_type not in allowed_content_types.get(extension, []):
        return False, f"Invalid content type for {extension} file"
    
    # File size will be checked during upload
    return True, ""

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other attacks"""
    
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove special characters except dots and hyphens
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Ensure it has an extension
    if '.' not in filename:
        return ""
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1)
        filename = name[:90] + '.' + ext
    
    return filename

def sanitize_text(text: str) -> str:
    """Sanitize text input to prevent injection attacks"""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x01-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Limit length
    if len(text) > 100000:  # 100KB limit
        text = text[:100000]
    
    return text.strip()

def validate_role(role: str) -> bool:
    """Validate role parameter"""
    valid_roles = ["software_engineer", "product_manager", "data_scientist"]
    return role in valid_roles

def mask_pii(text: str) -> str:
    """Mask potential PII in text for logging"""
    
    # Mask email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Mask phone numbers
    text = re.sub(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{4,6}', '[PHONE]', text)
    
    # Mask SSN-like patterns
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Mask credit card-like patterns
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
    
    return text 