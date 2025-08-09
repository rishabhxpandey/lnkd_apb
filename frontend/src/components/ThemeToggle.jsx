import { motion } from 'framer-motion'
import { Lightbulb } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

const ThemeToggle = () => {
  const { isDark, toggleTheme } = useTheme()

  return (
    <motion.button
      onClick={toggleTheme}
      className={`
        relative p-2 rounded-lg transition-colors duration-200
        ${isDark 
          ? 'bg-yellow-500 text-gray-900 hover:bg-yellow-400' 
          : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
        }
      `}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <motion.div
        initial={false}
        animate={{ 
          rotate: isDark ? 0 : 180,
          scale: isDark ? 1.1 : 1
        }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <Lightbulb 
          className={`w-5 h-5 ${isDark ? 'fill-current' : ''}`} 
          strokeWidth={isDark ? 1 : 2}
        />
      </motion.div>
      
      {/* Subtle glow effect when in dark mode */}
      {isDark && (
        <motion.div
          className="absolute inset-0 rounded-lg bg-yellow-400 opacity-20"
          initial={{ scale: 1 }}
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
    </motion.button>
  )
}

export default ThemeToggle
