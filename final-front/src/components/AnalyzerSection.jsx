import { useState } from 'react'
import { motion } from 'framer-motion'
import { useStrideStore } from '../store/strideStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const stripJsonCodeFence = (text) => {
  const trimmed = text.trim()
  const fenceMatch = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i)
  return fenceMatch ? fenceMatch[1].trim() : trimmed
}

const normalizeJsonLikeInput = (text) => {
  const normalizedQuotes = text
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/[\u2018\u2019]/g, "'")
    .trim()

  const firstBrace = normalizedQuotes.indexOf('{')
  const lastBrace = normalizedQuotes.lastIndexOf('}')

  if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
    return normalizedQuotes.slice(firstBrace, lastBrace + 1)
  }

  return normalizedQuotes
}

const AnalyzerSection = () => {
  const [flowInput, setFlowInput] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isGeneratingDFD, setIsGeneratingDFD] = useState(false)
  const [dfdImageUrl, setDfdImageUrl] = useState(null)
  const [analysisError, setAnalysisError] = useState('')
  const [dfdError, setDfdError] = useState('')
  const { setThreats } = useStrideStore()

  const readErrorMessage = async (response, fallbackMessage) => {
    try {
      const data = await response.json()
      return data?.detail || fallbackMessage
    } catch {
      return fallbackMessage
    }
  }

  const parseDfdPayload = () => {
    let parsed
    const cleanedInput = normalizeJsonLikeInput(stripJsonCodeFence(flowInput))

    try {
      parsed = JSON.parse(cleanedInput)
    } catch {
      throw new Error("DFD generation expects valid JSON. Paste raw JSON or a fenced ```json``` block with 'nodes' and 'flows'.")
    }

    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed) && parsed.flow && typeof parsed.flow === 'object') {
      parsed = parsed.flow
    }

    if (!parsed || typeof parsed !== 'object' || !Array.isArray(parsed.nodes) || !Array.isArray(parsed.flows)) {
      throw new Error("DFD JSON must contain top-level 'nodes' and 'flows' arrays.")
    }

    return parsed
  }

  const handleAnalyze = async () => {
    if (!flowInput.trim()) return

    setIsAnalyzing(true)
    setDfdImageUrl(null)
    setAnalysisError('')

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ flow: flowInput }),
      })

      if (response.ok) {
        const data = await response.json()
        setThreats(data.threats || [])
      } else {
        const message = await readErrorMessage(response, 'Threat analysis failed.')
        setAnalysisError(message)
        setThreats([])
      }
    } catch (error) {
      console.error('Error analyzing threats:', error)
      setAnalysisError('Could not reach the backend. Check that the FastAPI server is running.')
      setThreats([])
    } finally {
      setIsAnalyzing(false)
    }
  }

  const generateDFD = async () => {
    if (!flowInput.trim()) return

    setIsGeneratingDFD(true)
    setDfdImageUrl(null)
    setDfdError('')

    try {
      const dfdPayload = parseDfdPayload()

      const response = await fetch(`${API_BASE_URL}/generate_dfd`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dfdPayload),
      })

      if (!response.ok) {
        const message = await readErrorMessage(response, 'Failed to generate DFD.')
        setDfdError(message)
        setDfdImageUrl(null)
        return
      }

      const blob = await response.blob()
      const imageUrl = URL.createObjectURL(blob)
      setDfdImageUrl(imageUrl)
    } catch (error) {
      console.error('Error generating DFD:', error)
      setDfdError(error.message || 'Could not generate the DFD.')
      setDfdImageUrl(null)
    } finally {
      setIsGeneratingDFD(false)
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
          whileHover={{ y: -5, boxShadow: '0 8px 40px rgba(57, 255, 20, 0.1)' }}
        >
          <div className="input-wrapper">
            <label htmlFor="flowInput" className="input-label">System Flow Description</label>
            <p style={{ margin: '0 0 0.75rem', opacity: 0.75 }}>
              Threat analysis accepts prose or pasted JSON. DFD generation expects JSON with `nodes` and `flows`.
            </p>
            <motion.textarea
              id="flowInput"
              className="flow-input"
              placeholder="Describe your system flow, or paste DFD JSON here..."
              rows="6"
              value={flowInput}
              onChange={(e) => setFlowInput(e.target.value)}
              whileFocus={{ scale: 1.01, boxShadow: '0 0 20px rgba(57, 255, 20, 0.2)' }}
              transition={{ type: 'spring', stiffness: 300 }}
            />
          </div>

          <div className="analyzer-actions" style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <motion.button
              className="btn btn--primary"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !flowInput.trim()}
              whileHover={{
                scale: 1.05,
                boxShadow: '0 0 25px rgba(57, 255, 20, 0.4)',
              }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Threats'}
            </motion.button>

            <motion.button
              className="btn btn--secondary"
              onClick={generateDFD}
              disabled={isGeneratingDFD || !flowInput.trim()}
              whileHover={{
                scale: 1.05,
                boxShadow: '0 0 25px rgba(20, 120, 255, 0.6)',
              }}
              whileTap={{ scale: 0.98 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              {isGeneratingDFD ? 'Generating DFD...' : 'Generate DFD'}
            </motion.button>
          </div>

          {analysisError && (
            <p style={{ marginTop: '1rem', color: '#ff6b6b' }}>
              {analysisError}
            </p>
          )}

          {dfdError && (
            <p style={{ marginTop: '0.5rem', color: '#ffb86b' }}>
              {dfdError}
            </p>
          )}

          {dfdImageUrl && (
            <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
              <h4>Generated Data Flow Diagram</h4>
              <img
                src={dfdImageUrl}
                alt="Data Flow Diagram"
                style={{ maxWidth: '100%', borderRadius: '8px', boxShadow: '0 0 10px rgba(0,0,0,0.2)' }}
              />
              <br />
              <a
                href={dfdImageUrl}
                download="data_flow_diagram.png"
                style={{
                  display: 'inline-block',
                  marginTop: '1rem',
                  padding: '0.5rem 1rem',
                  backgroundColor: '#398c15',
                  color: 'white',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  cursor: 'pointer',
                }}
              >
                Download Diagram
              </a>
            </div>
          )}
        </motion.div>
      </div>
    </motion.section>
  )
}

export default AnalyzerSection
