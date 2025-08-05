import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import ChatInterface from '../components/ChatInterface'
import FeedbackModal from '../components/FeedbackModal'
import { submitAnswer, getFeedback } from '../services/api'

const InterviewPage = () => {
  const location = useLocation()
  const navigate = useNavigate()
  
  const [sessionId, setSessionId] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [questionType, setQuestionType] = useState('')
  const [questionNumber, setQuestionNumber] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [messages, setMessages] = useState([])

  useEffect(() => {
    if (!location.state?.sessionId) {
      navigate('/')
      return
    }

    setSessionId(location.state.sessionId)
    setCurrentQuestion(location.state.firstQuestion)
    setQuestionType(location.state.questionType)
    
    // Add initial question to messages
    setMessages([{
      id: 1,
      type: 'question',
      content: location.state.firstQuestion,
      questionType: location.state.questionType,
      timestamp: new Date()
    }])
  }, [location.state, navigate])

  const handleAnswerSubmit = async (answer) => {
    if (!answer.trim() || isLoading) return

    // Add user answer to messages
    const userMessage = {
      id: messages.length + 1,
      type: 'answer',
      content: answer,
      timestamp: new Date()
    }
    setMessages([...messages, userMessage])

    setIsLoading(true)
    try {
      const response = await submitAnswer(sessionId, answer)
      
      if (response.is_complete) {
        setIsComplete(true)
        // Fetch feedback
        const feedbackData = await getFeedback(sessionId)
        setFeedback(feedbackData)
        setShowFeedback(true)
      } else {
        // Add AI question to messages
        const aiMessage = {
          id: messages.length + 2,
          type: 'question',
          content: response.question,
          questionType: response.question_type,
          timestamp: new Date()
        }
        setMessages([...messages, userMessage, aiMessage])
        
        setCurrentQuestion(response.question)
        setQuestionType(response.question_type)
        setQuestionNumber(response.question_number)
      }
    } catch (error) {
      toast.error('Failed to submit answer. Please try again.')
      console.error(error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEndInterview = () => {
    navigate('/')
  }

  if (!sessionId) {
    return null
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Interview in Progress
          </h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              Question {questionNumber} of 5
            </span>
            <button
              onClick={handleEndInterview}
              className="text-red-600 hover:text-red-700 font-medium"
            >
              End Interview
            </button>
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-800">
            <span className="font-semibold">Current Question Type:</span> {' '}
            {questionType === 'technical' ? '🔧 Technical' : '💭 Behavioral'}
          </p>
        </div>
      </motion.div>

      <ChatInterface
        messages={messages}
        onSubmitAnswer={handleAnswerSubmit}
        isLoading={isLoading}
        isComplete={isComplete}
      />

      {showFeedback && feedback && (
        <FeedbackModal
          feedback={feedback}
          onClose={() => {
            setShowFeedback(false)
            navigate('/')
          }}
        />
      )}
    </div>
  )
}

export default InterviewPage 