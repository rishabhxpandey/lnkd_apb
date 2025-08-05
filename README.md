# LinkedIn Interview Prep AI

An AI-powered interview preparation tool designed for LinkedIn's APB program. This demo application helps users practice technical and behavioral interviews with personalized questions based on their resume.

## 🚀 Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Tailwind CSS
- **AI**: OpenAI GPT-4o
- **Vector Store**: FAISS for resume embeddings
- **Resume Parsing**: PDFPlumber + python-docx

## 📁 Project Structure

```
linkedin-interview-prep-ai/
├── backend/          # FastAPI backend service
├── frontend/         # React frontend application
├── docs/            # Project documentation
├── startup.sh       # Quick start script
└── README.md        # This file
```

## 🏃‍♂️ Quick Start

1. Clone the repository:
```bash
git clone https://github.com/rishabhxpandey/lnkd_apb.git
cd lnkd_apb
```

2. Set up environment variables:
```bash
cp backend/.env.example backend/.env
# Add your OpenAI API key to backend/.env
```

3. Run the application:
```bash
chmod +x startup.sh
./startup.sh
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🎯 Features

- **Role Selection**: Choose from Software Engineer, Product Manager, or Data Scientist roles
- **Resume Upload**: Upload PDF/DOCX resumes for personalized questions
- **AI-Powered Questions**: Get role-specific interview questions based on your experience
- **Dynamic Follow-ups**: Receive contextual follow-up questions based on your answers
- **Interview Feedback**: Get detailed feedback and flashcards for improvement

## 📚 Documentation

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [Security Considerations](./docs/SECURITY.md)
- [Demo Script](./docs/DEMO_PLAN.md)

## 🛠️ Development

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📝 License

This is a demo project for LinkedIn's APB program. 