import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, Bot, User } from 'lucide-react'

const ChatInterface = ({ messages, onSubmitAnswer, isLoading, isComplete }) => {
  const [answer, setAnswer] = useState('')
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (answer.trim() && !isLoading && !isComplete) {
      onSubmitAnswer(answer)
      setAnswer('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleTextareaChange = (e) => {
    setAnswer(e.target.value)
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="card h-[600px] flex flex-col">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto scrollbar-hide p-4 space-y-4">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${message.type === 'answer' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] ${
                message.type === 'answer'
                  ? 'bg-linkedin-blue text-white'
                  : 'bg-gray-100 text-gray-900'
              } rounded-lg p-4`}
            >
              <div className="flex items-center space-x-2 mb-2">
                {message.type === 'question' ? (
                  <>
                    <Bot className="h-5 w-5" />
                    <span className="font-semibold">AI Interviewer</span>
                    {message.questionType && (
                      <span className="text-xs opacity-80">
                        ({message.questionType})
                      </span>
                    )}
                  </>
                ) : (
                  <>
                    <User className="h-5 w-5" />
                    <span className="font-semibold">You</span>
                  </>
                )}
              </div>
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
          </motion.div>
        ))}
        
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Bot className="h-5 w-5 text-gray-600" />
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="border-t p-4">
        {isComplete ? (
          <div className="text-center py-4">
            <p className="text-green-600 font-semibold">
              🎉 Interview Complete! Your feedback is being generated...
            </p>
          </div>
        ) : (
          <div className="flex space-x-4">
            <textarea
              ref={textareaRef}
              value={answer}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder="Type your answer here..."
              className="flex-1 input-field resize-none min-h-[50px] max-h-[150px]"
              rows="1"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!answer.trim() || isLoading}
              className="btn-primary self-end px-4 py-2"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        )}
        
        {!isComplete && (
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        )}
      </form>
    </div>
  )
}

export default ChatInterface 