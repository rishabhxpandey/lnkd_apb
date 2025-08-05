# Backend - LinkedIn Interview Prep AI

FastAPI backend service for the LinkedIn Interview Prep AI application.

## Setup

1. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. Run the server:
```bash
uvicorn app:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Resume Management

- **POST** `/api/resume/upload`
  - Upload a PDF or DOCX resume
  - Body: multipart/form-data with file field
  - Returns: Resume ID and parsed content

### Interview Flow

- **GET** `/api/interview/start?role={role}`
  - Start an interview session
  - Roles: software_engineer, product_manager, data_scientist
  - Returns: Session ID and first question

- **POST** `/api/interview/answer`
  - Submit an answer and get follow-up question
  - Body: `{ "session_id": string, "answer": string }`
  - Returns: Next question or session completion

- **GET** `/api/interview/feedback/{session_id}`
  - Get interview feedback and flashcards
  - Returns: Performance analysis and improvement suggestions

## Project Structure

```
backend/
├── app.py              # FastAPI application entry point
├── routes/
│   ├── interview.py    # Interview flow endpoints
│   └── resume.py       # Resume upload/parsing endpoints
├── services/
│   ├── llm_service.py      # GPT-4o integration
│   ├── resume_parser.py    # PDF/DOCX text extraction
│   └── vector_store.py     # FAISS embeddings management
├── models/
│   └── schemas.py      # Pydantic data models
└── utils/
    └── security.py     # Input validation & sanitization
```

## Environment Variables

Create a `.env` file with:

```
OPENAI_API_KEY=your_api_key_here
UPLOAD_MAX_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,docx
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
```

### Type Checking
```bash
mypy .
``` 