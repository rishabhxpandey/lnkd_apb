import { Link } from 'react-router-dom'
import { Briefcase } from 'lucide-react'

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <Briefcase className="h-8 w-8 text-linkedin-blue" />
              <span className="text-xl font-bold text-gray-900">
                LinkedIn Interview Prep AI
              </span>
            </Link>
            
            <nav className="flex items-center space-x-4">
              <Link 
                to="/" 
                className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
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
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
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