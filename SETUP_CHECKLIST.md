# Setup Checklist

## Essential Setup (Required for Demo)

- [ ] **OpenAI API Key**
  ```bash
  cd backend
  cp env.example .env
  # Add your OpenAI API key to .env
  ```

- [ ] **Backend Dependencies**
  ```bash
  cd backend
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- [ ] **Frontend Dependencies**
  ```bash
  cd frontend
  npm install
  ```

- [ ] **Test the Application**
  ```bash
  ./startup.sh
  # Visit http://localhost:5173
  ```

## What Works Out of the Box

✅ **Full User Flow**
- Role selection (3 roles)
- Resume upload and parsing
- 5-question interview session
- Dynamic follow-up questions
- Feedback generation with scores

✅ **With OpenAI API Key**
- Intelligent, contextual questions
- Personalized based on resume
- Detailed feedback analysis

✅ **Without OpenAI API Key**
- Fallback questions (generic)
- Basic functionality preserved
- UI/UX fully functional

## Known Limitations

### Data Persistence
- Sessions lost on server restart
- Uploaded files stored locally
- No user accounts/history

### Scalability
- Single-server only
- In-memory session storage
- No caching layer

### Security (Demo Only)
- Basic file validation
- No authentication
- HTTP only (no HTTPS)

## Optional Enhancements

### For Better Demo
1. Add sample resumes in `frontend/public/samples/`
2. Increase GPT model to `gpt-4o` in `backend/services/llm_service.py`
3. Add more interview questions by changing limit in routes

### For Production
1. Add PostgreSQL for persistence
2. Implement Redis for sessions
3. Add authentication (JWT)
4. Deploy with HTTPS
5. Add monitoring (Sentry)
6. Implement rate limiting

## Troubleshooting

**"Failed to start interview"**
- Check OpenAI API key is set correctly
- Verify backend is running (port 8000)

**"Failed to upload resume"**
- Check file is PDF or DOCX
- Ensure file is under 10MB
- Verify `uploads/` directory exists

**Slow AI responses**
- Normal for GPT-4 (5-10 seconds)
- Consider using gpt-3.5-turbo for speed

**Frontend won't load**
- Check if port 5173 is available
- Try `npm run dev` manually
- Clear browser cache 