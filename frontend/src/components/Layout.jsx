import { Link } from 'react-router-dom'
import { Briefcase } from 'lucide-react'
import ThemeToggle from './ThemeToggle'

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <Briefcase className="h-8 w-8 text-linkedin-blue" />
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                LinkedIn Interview Prep AI
              </span>
            </Link>
            
            <nav className="flex items-center space-x-4">
              <Link 
                to="/" 
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium transition-colors"
              >
                Home
              </Link>
              <a 
                href="https://linkedin.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-linkedin-blue hover:text-linkedin-darkblue font-medium transition-colors"
              >
                LinkedIn
              </a>
              <ThemeToggle />
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 dark:bg-gray-900 text-white py-8 mt-12 transition-colors duration-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-sm">
              © 2024 LinkedIn Interview Prep AI - APB Demo Project
            </p>
            <p className="text-xs mt-2 text-gray-400">
              Built with FastAPI & React
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout 