import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import RoleCard from '../components/RoleCard'
import ResumeUpload from '../components/ResumeUpload'
import { startInterview } from '../services/api'

const roles = [
  {
    id: 'software_engineer',
    title: 'Software Engineer',
    description: 'Technical interviews focusing on coding, system design, and problem-solving',
    icon: '💻',
    skills: ['Data Structures', 'Algorithms', 'System Design', 'Coding']
  },
  {
    id: 'product_manager',
    title: 'Product Manager',
    description: 'Case studies, product sense, and strategic thinking questions',
    icon: '📊',
    skills: ['Product Strategy', 'Analytics', 'User Research', 'Leadership']
  },
  {
    id: 'data_scientist',
    title: 'Data Scientist',
    description: 'Statistics, machine learning, and data analysis scenarios',
    icon: '📈',
    skills: ['Machine Learning', 'Statistics', 'Python/R', 'Data Visualization']
  }
]

const HomePage = () => {
  const navigate = useNavigate()
  const [selectedRole, setSelectedRole] = useState(null)
  const [resumeId, setResumeId] = useState(null)
  const [isStarting, setIsStarting] = useState(false)

  const handleRoleSelect = (roleId) => {
    setSelectedRole(roleId)
  }

  const handleResumeUpload = (uploadedResumeId) => {
    setResumeId(uploadedResumeId)
    toast.success('Resume uploaded successfully!')
  }

  const handleStartInterview = async () => {
    if (!selectedRole) {
      toast.error('Please select a role first')
      return
    }

    setIsStarting(true)
    try {
      const response = await startInterview(selectedRole, resumeId)
      navigate('/interview', { 
        state: { 
          sessionId: response.session_id,
          role: selectedRole,
          firstQuestion: response.question,
          questionType: response.question_type
        }
      })
    } catch (error) {
      toast.error('Failed to start interview. Please try again.')
      console.error(error)
    } finally {
      setIsStarting(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Ace Your LinkedIn Interview
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Practice with AI-powered mock interviews tailored to your resume and role.
          Get real-time feedback and improve your interview skills.
        </p>
      </motion.div>

      {/* Role Selection */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="mb-12"
      >
        <h2 className="text-2xl font-semibold mb-6 text-center">
          Step 1: Choose Your Role
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {roles.map((role) => (
            <RoleCard
              key={role.id}
              role={role}
              isSelected={selectedRole === role.id}
              onSelect={handleRoleSelect}
            />
          ))}
        </div>
      </motion.div>

      {/* Resume Upload */}
      {selectedRole && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-semibold mb-6 text-center">
            Step 2: Upload Your Resume (Optional)
          </h2>
          <ResumeUpload onUpload={handleResumeUpload} />
        </motion.div>
      )}

      {/* Start Interview Button */}
      {selectedRole && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <button
            onClick={handleStartInterview}
            disabled={isStarting}
            className="btn-primary text-lg px-8 py-4 inline-flex items-center"
          >
            {isStarting ? (
              <>
                <div className="loading-dots mr-2">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                Starting Interview...
              </>
            ) : (
              'Start Interview'
            )}
          </button>
          
          {!resumeId && (
            <p className="text-sm text-gray-500 mt-4">
              Tip: Upload your resume for more personalized questions
            </p>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default HomePage 