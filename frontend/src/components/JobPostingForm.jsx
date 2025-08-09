import { useState } from 'react'
import { motion } from 'framer-motion'
import { Link2, Plus, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { uploadJob } from '../services/api'

const JobPostingForm = ({ onJobAdded }) => {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!url.trim()) {
      toast.error('Please enter a valid LinkedIn job URL')
      return
    }

    // Basic URL validation
    if (!url.includes('linkedin.com') || !url.includes('jobs/view')) {
      toast.error('Please enter a valid LinkedIn job posting URL')
      return
    }

    setIsLoading(true)
    try {
      const response = await uploadJob(url.trim())
      toast.success('Job posting added successfully!')
      setUrl('')
      setIsExpanded(false)
      onJobAdded?.(response)
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to add job posting'
      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {!isExpanded ? (
          <button
            onClick={() => setIsExpanded(true)}
            className="w-full p-4 flex items-center gap-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div className="w-10 h-10 bg-linkedin-blue rounded-lg flex items-center justify-center">
              <Plus className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-white">Add Job Posting</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Paste a LinkedIn job URL to analyze
              </p>
            </div>
          </button>
        ) : (
          <form onSubmit={handleSubmit} className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-linkedin-blue rounded-lg flex items-center justify-center">
                <Link2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">Add Job Posting</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Enter a LinkedIn job posting URL
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label htmlFor="jobUrl" className="sr-only">
                  LinkedIn Job URL
                </label>
                <input
                  id="jobUrl"
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://linkedin.com/jobs/view/123456789"
                  className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
                  disabled={isLoading}
                  autoFocus
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={isLoading || !url.trim()}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <div className="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      Adding...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      Add Job
                    </>
                  )}
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setIsExpanded(false)
                    setUrl('')
                  }}
                  disabled={isLoading}
                  className="btn-secondary px-4"
                >
                  Cancel
                </button>
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex gap-2">
                <AlertCircle className="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-blue-800 dark:text-blue-300">
                  <p className="font-medium mb-1">How to get a LinkedIn job URL:</p>
                  <ol className="list-decimal list-inside space-y-1 text-xs">
                    <li>Go to the job posting on LinkedIn</li>
                    <li>Copy the URL from your browser's address bar</li>
                    <li>Paste it here to analyze the job requirements</li>
                  </ol>
                </div>
              </div>
            </div>
          </form>
        )}
      </div>
    </motion.div>
  )
}

export default JobPostingForm
