# Architecture Overview

## System Design

LinkedIn Interview Prep AI is built with a modern microservices architecture focusing on scalability, maintainability, and user experience.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Role Select │  │Resume Upload │  │ Chat Interface     │    │
│  └─────────────┘  └──────────────┘  └────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────┴────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │   Routes    │  │   Services   │  │     Models         │    │
│  │ • Interview │  │ • LLM        │  │ • Pydantic Schemas │    │
│  │ • Resume    │  │ • Parser     │  │ • Validation       │    │
│  └─────────────┘  │ • Vector DB  │  └────────────────────┘    │
│                   └──────────────┘                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │              External Services           │
        │  ┌─────────────┐    ┌────────────────┐ │
        │  │ OpenAI API  │    │  FAISS Vector  │ │
        │  │  (GPT-4o)   │    │     Store      │ │
        │  └─────────────┘    └────────────────┘ │
        └─────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **React 18** - UI framework with hooks
- **Vite** - Build tool for fast development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type hints
- **OpenAI SDK** - GPT-4o integration
- **FAISS** - Facebook AI Similarity Search for embeddings
- **PDFPlumber & python-docx** - Resume parsing

### Infrastructure
- **CORS** - Configured for frontend-backend communication
- **File Storage** - Local filesystem (can be replaced with S3)
- **Vector Store** - FAISS with persistence

## Data Flow

### 1. Interview Initialization
```
User → Select Role → Upload Resume (Optional) → Start Interview
         │                │                          │
         └────────────────┴──────────────────────────┘
                                │
                          Backend Processing:
                          1. Create session
                          2. Parse resume (if uploaded)
                          3. Generate embeddings
                          4. Store in vector DB
                          5. Generate first question
```

### 2. Q&A Flow
```
User Answer → Backend → LLM Service → Generate Follow-up
     │           │           │              │
     │           │           └──────────────┘
     │           │                 │
     │           └─────────────────┘
     │                   │
     └───────────────────┘
         Chat Interface
```

### 3. Feedback Generation
```
Interview Complete → Analyze All Q&A → Generate Feedback
                           │                  │
                           │                  ├─ Score
                           │                  ├─ Strengths
                           │                  ├─ Improvements
                           │                  └─ Flashcards
                           │
                     LLM Processing
```

## Key Design Decisions

### 1. Stateless API Design
- Sessions stored in-memory (Redis in production)
- RESTful endpoints for clear separation
- JWT authentication ready (not implemented in demo)

### 2. Resume Processing Pipeline
- Async file upload with progress tracking
- Text extraction preserves formatting
- Embeddings for semantic search
- PII detection and masking

### 3. LLM Integration
- Structured JSON responses
- Fallback responses for reliability
- Token limit management
- Response caching potential

### 4. Frontend Architecture
- Component-based design
- Centralized API service
- Optimistic UI updates
- Error boundaries (to be added)

## Scalability Considerations

### Horizontal Scaling
- Stateless backend allows multiple instances
- Load balancer ready architecture
- Session storage can move to Redis
- Vector store can use Pinecone/Weaviate

### Performance Optimizations
- Frontend code splitting
- API response caching
- Lazy loading components
- WebSocket potential for real-time

### Security Enhancements
- Rate limiting endpoints
- File upload restrictions
- Input sanitization
- API key rotation

## Future Enhancements

1. **Multi-language Support**
   - i18n for frontend
   - Multi-language LLM prompts

2. **Advanced Analytics**
   - Interview performance tracking
   - Aggregate insights
   - Progress tracking

3. **Enhanced Features**
   - Voice input/output
   - Video mock interviews
   - Peer review system
   - Custom question banks

4. **Integration Points**
   - LinkedIn profile import
   - Calendar scheduling
   - Email notifications
   - Export to PDF report 