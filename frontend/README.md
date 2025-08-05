# Frontend - LinkedIn Interview Prep AI

React-based frontend for the LinkedIn Interview Prep AI application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173

## Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Layout.jsx      # App layout with header/footer
│   │   ├── RoleCard.jsx    # Role selection card
│   │   ├── ResumeUpload.jsx # Resume upload component
│   │   ├── ChatInterface.jsx # Q&A chat interface
│   │   └── FeedbackModal.jsx # Interview feedback display
│   ├── pages/              # Page components
│   │   ├── HomePage.jsx    # Landing page with role selection
│   │   └── InterviewPage.jsx # Interview Q&A page
│   ├── services/           # API service layer
│   │   └── api.js         # Backend API calls
│   ├── App.jsx            # Main app component with routing
│   ├── main.jsx           # React entry point
│   └── index.css          # Global styles & Tailwind imports
├── public/                # Static assets
├── index.html            # HTML template
└── package.json          # Dependencies and scripts
```

## Key Features

### 1. Role Selection (HomePage)
- Choose from three roles: Software Engineer, Product Manager, Data Scientist
- Each role displays relevant skills and description
- Visual feedback for selected role

### 2. Resume Upload (ResumeUpload)
- Drag-and-drop or click to upload
- Supports PDF and DOCX files (max 10MB)
- Shows upload progress and extracted information
- Optional step for personalized questions

### 3. Interview Chat (ChatInterface)
- Real-time Q&A interface
- Auto-resizing text input
- Message history with sender identification
- Loading states and animations
- Keyboard shortcuts (Enter to send)

### 4. Feedback Display (FeedbackModal)
- Overall score with star rating
- Strengths and improvement areas
- Study flashcards for key concepts
- Clean modal presentation

## API Integration

All API calls are centralized in `src/services/api.js`:

- `uploadResume(file)` - Upload resume file
- `startInterview(role, resumeId)` - Start interview session
- `submitAnswer(sessionId, answer)` - Submit answer and get next question
- `getFeedback(sessionId)` - Get interview feedback

## Styling

- **Tailwind CSS** for utility-first styling
- **Custom components** defined in `index.css`
- **LinkedIn brand colors** configured in `tailwind.config.js`
- **Framer Motion** for smooth animations
- **Lucide React** for consistent icons

## State Management

- Local component state with React hooks
- Navigation state via React Router
- Toast notifications with react-hot-toast
- No global state management needed for this demo

## Development Tips

1. **Hot Module Replacement** is enabled for fast development
2. **Proxy configuration** in `vite.config.js` forwards `/api` to backend
3. **ESLint** is configured for code quality
4. **Responsive design** works on mobile and desktop

## Environment Variables

No frontend-specific environment variables are required. The app uses relative API paths that are proxied to the backend during development. 