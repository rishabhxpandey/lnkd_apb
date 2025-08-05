import { Fragment } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import { motion } from 'framer-motion'
import { Star, CheckCircle, AlertCircle, BookOpen, X } from 'lucide-react'

const FeedbackModal = ({ feedback, onClose }) => {
  const { overall_score, strengths, improvements, flashcards } = feedback

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600'
    if (score >= 6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const renderStars = (score) => {
    const fullStars = Math.floor(score / 2)
    const hasHalfStar = score % 2 >= 1
    
    return (
      <div className="flex items-center space-x-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`h-6 w-6 ${
              i < fullStars
                ? 'fill-yellow-400 text-yellow-400'
                : i === fullStars && hasHalfStar
                ? 'fill-yellow-200 text-yellow-400'
                : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    )
  }

  return (
    <Transition appear show={true} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-3xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex justify-between items-start mb-6">
                  <Dialog.Title
                    as="h3"
                    className="text-2xl font-bold text-gray-900"
                  >
                    Interview Feedback
                  </Dialog.Title>
                  <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>

                {/* Overall Score */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center mb-8"
                >
                  <h4 className="text-lg font-semibold mb-2">Overall Performance</h4>
                  <div className={`text-5xl font-bold ${getScoreColor(overall_score)} mb-2`}>
                    {overall_score}/10
                  </div>
                  {renderStars(overall_score)}
                </motion.div>

                <div className="grid md:grid-cols-2 gap-6 mb-8">
                  {/* Strengths */}
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 }}
                  >
                    <h4 className="flex items-center text-lg font-semibold mb-3 text-green-700">
                      <CheckCircle className="h-5 w-5 mr-2" />
                      Strengths
                    </h4>
                    <ul className="space-y-2">
                      {strengths.map((strength, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-500 mr-2">•</span>
                          <span className="text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </motion.div>

                  {/* Areas for Improvement */}
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <h4 className="flex items-center text-lg font-semibold mb-3 text-orange-700">
                      <AlertCircle className="h-5 w-5 mr-2" />
                      Areas for Improvement
                    </h4>
                    <ul className="space-y-2">
                      {improvements.map((improvement, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-orange-500 mr-2">•</span>
                          <span className="text-gray-700">{improvement}</span>
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                </div>

                {/* Flashcards */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <h4 className="flex items-center text-lg font-semibold mb-4">
                    <BookOpen className="h-5 w-5 mr-2" />
                    Study Flashcards
                  </h4>
                  <div className="grid gap-4">
                    {flashcards.map((card, index) => (
                      <div
                        key={index}
                        className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                      >
                        <div className="font-medium text-gray-900 mb-2">
                          Q: {card.front}
                        </div>
                        <div className="text-gray-700">
                          A: {card.back}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>

                <div className="mt-8 flex justify-end">
                  <button
                    type="button"
                    className="btn-primary"
                    onClick={onClose}
                  >
                    Continue Practicing
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}

export default FeedbackModal 