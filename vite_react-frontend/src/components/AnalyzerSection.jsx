import { useState } from 'react'
import { motion } from 'framer-motion'
import { useStrideStore } from '../store/strideStore'

const AnalyzerSection = () => {
  const [flowInput, setFlowInput] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const { setThreats } = useStrideStore()

  const handleAnalyze = async () => {
    if (!flowInput.trim()) return
    
    setIsAnalyzing(true)
    
    try {
      // Call the backend API (keeping the same endpoint)
      const response = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ flow: flowInput })
      })
      
      if (response.ok) {
        const data = await response.json()
        setThreats(data.threats || [])
      } else {
        console.error('Analysis failed')
        setThreats([])
      }
    } catch (error) {
      console.error('Error analyzing threats:', error)
      setThreats([])
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <motion.section 
      className="analyzer-section"
      id="analyzer"
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      viewport={{ once: true, amount: 0.3 }}
    >
      <div className="container">
        <motion.div 
          className="section-header"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <h2 className="section-title">System Analysis</h2>
          <p className="section-subtitle">Describe your system architecture for comprehensive threat analysis</p>
        </motion.div>
        
        <motion.div 
          className="analyzer-card card"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          whileHover={{ y: -5, boxShadow: "0 8px 40px rgba(57, 255, 20, 0.1)" }}
        >
          <div className="input-wrapper">
            <label htmlFor="flowInput" className="input-label">System Flow Description</label>
            <motion.textarea
              id="flowInput"
              className="flow-input"
              placeholder="Describe your system flow here..."
              rows="6"
              value={flowInput}
              onChange={(e) => setFlowInput(e.target.value)}
              whileFocus={{ scale: 1.01, boxShadow: "0 0 20px rgba(57, 255, 20, 0.2)" }}
              transition={{ type: "spring", stiffness: 300 }}
            />
          </div>
          <div className="analyzer-actions">
            <motion.button
              className="btn btn--primary"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !flowInput.trim()}
              whileHover={{ 
                scale: 1.05,
                boxShadow: "0 0 25px rgba(57, 255, 20, 0.4)"
              }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <motion.svg 
                className="btn-icon" 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none"
                animate={isAnalyzing ? { rotate: 360 } : { rotate: 0 }}
                transition={{ duration: 1, repeat: isAnalyzing ? Infinity : 0 }}
              >
                <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2"/>
                <path d="21 21l-4.35-4.35" stroke="currentColor" strokeWidth="2"/>
              </motion.svg>
              {isAnalyzing ? 'Analyzing...' : 'Analyze Threats'}
            </motion.button>
          </div>
        </motion.div>
      </div>
    </motion.section>
  )
}

export default AnalyzerSection