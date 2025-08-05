import axios from 'axios'

const API_BASE_URL = '/api'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Resume APIs
export const uploadResume = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const getResume = async (resumeId) => {
  const response = await api.get(`/resume/${resumeId}`)
  return response.data
}

// Interview APIs
export const startInterview = async (role, resumeId = null) => {
  const params = { role }
  if (resumeId) {
    params.resume_id = resumeId
  }
  
  const response = await api.get('/interview/start', { params })
  return response.data
}

export const submitAnswer = async (sessionId, answer) => {
  const response = await api.post('/interview/answer', {
    session_id: sessionId,
    answer: answer,
  })
  
  return response.data
}

export const getFeedback = async (sessionId) => {
  const response = await api.get(`/interview/feedback/${sessionId}`)
  return response.data
}

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || 'An error occurred'
      console.error('API Error:', message)
    } else if (error.request) {
      // Request was made but no response
      console.error('Network Error: No response from server')
    } else {
      // Something else happened
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api 