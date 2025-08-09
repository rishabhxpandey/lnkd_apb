import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Upload, File, X, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { uploadResume } from '../services/api'

const ResumeUpload = ({ onUpload }) => {
  const [file, setFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [extractedInfo, setExtractedInfo] = useState(null)
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      if (!validTypes.includes(selectedFile.type)) {
        toast.error('Please upload a PDF or DOCX file')
        return
      }
      
      if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('File size must be less than 10MB')
        return
      }
      
      setFile(selectedFile)
      setUploadSuccess(false)
      setExtractedInfo(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setIsUploading(true)
    try {
      const response = await uploadResume(file)
      setUploadSuccess(true)
      setExtractedInfo(response.extracted_info)
      onUpload(response.resume_id)
      toast.success('Resume processed successfully!')
    } catch (error) {
      toast.error('Failed to upload resume')
      console.error(error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleRemove = () => {
    setFile(null)
    setUploadSuccess(false)
    setExtractedInfo(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="card"
      >
        {!file ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-linkedin-blue transition-colors"
          >
            <Upload className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
            <p className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
              Click to upload your resume
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              PDF or DOCX (max 10MB)
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <File className="h-8 w-8 text-linkedin-blue" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{file.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              {uploadSuccess ? (
                <CheckCircle className="h-6 w-6 text-green-500" />
              ) : (
                <button
                  onClick={handleRemove}
                  className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>

            {!uploadSuccess && (
              <button
                onClick={handleUpload}
                disabled={isUploading}
                className="btn-primary w-full"
              >
                {isUploading ? (
                  <div className="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                ) : (
                  'Upload Resume'
                )}
              </button>
            )}

            {extractedInfo && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg"
              >
                <h4 className="font-semibold text-green-900 dark:text-green-400 mb-2">
                  Resume Processed Successfully!
                </h4>
                <div className="text-sm text-green-800 dark:text-green-300 space-y-1">
                  {extractedInfo.email && (
                    <p>📧 Email: {extractedInfo.email}</p>
                  )}
                  {extractedInfo.skills && extractedInfo.skills.length > 0 && (
                    <p>🛠️ Skills: {extractedInfo.skills.slice(0, 5).join(', ')}</p>
                  )}
                  {extractedInfo.experience && extractedInfo.experience.length > 0 && (
                    <p>💼 Experience entries: {extractedInfo.experience.length}</p>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        )}
      </motion.div>
    </div>
  )
}

export default ResumeUpload 