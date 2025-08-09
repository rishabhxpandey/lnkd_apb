import { Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import HomePage from './pages/HomePage'
import InterviewPage from './pages/InterviewPage'
import Layout from './components/Layout'

function App() {
  return (
    <ThemeProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/interview" element={<InterviewPage />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  )
}

export default App 