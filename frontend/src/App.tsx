import { useState } from 'react'
import './App.css'

interface SentimentResult {
  sentiment: string
  confidence: number
  scores: {
    positive: number
    neutral: number
    negative: number
  }
  vibe: string
  emoji: string
  color: string
}

function App() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<SentimentResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const analyzeText = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        throw new Error('Failed to analyze text')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Failed to analyze. Make sure the backend is running!')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.metaKey) {
      analyzeText()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            ✨ Vibe Check
          </h1>
          <p className="text-gray-600 text-lg">
            Analyze the sentiment of any text instantly
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <label htmlFor="text-input" className="block text-sm font-medium text-gray-700 mb-2">
            Enter your text
          </label>
          <textarea
            id="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type or paste any text here... (⌘+Enter to analyze)"
            className="w-full h-40 p-4 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 outline-none transition-all resize-none"
          />
          
          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">
              {text.length} characters
            </span>
            <button
              onClick={analyzeText}
              disabled={loading || !text.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 active:scale-95"
            >
              {loading ? '🔮 Analyzing...' : '✨ Check Vibe'}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {result && (
          <div className="bg-white rounded-2xl shadow-xl p-8 animate-fade-in">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">{result.emoji}</div>
              <h2 className="text-3xl font-bold mb-2" style={{ color: result.color }}>
                {result.vibe}
              </h2>
              <p className="text-gray-600 capitalize">
                Overall Sentiment: <span className="font-semibold">{result.sentiment}</span>
              </p>
            </div>

            {/* Confidence Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Confidence</span>
                <span className="font-semibold">{(result.confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full transition-all duration-500"
                  style={{
                    width: `${result.confidence * 100}%`,
                    backgroundColor: result.color,
                  }}
                />
              </div>
            </div>

            {/* Sentiment Breakdown */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-700 mb-3">Sentiment Breakdown</h3>
              
              {/* Positive */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-green-600">😊 Positive</span>
                  <span className="font-semibold">{(result.scores.positive * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 transition-all duration-500"
                    style={{ width: `${result.scores.positive * 100}%` }}
                  />
                </div>
              </div>

              {/* Neutral */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">😐 Neutral</span>
                  <span className="font-semibold">{(result.scores.neutral * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-400 transition-all duration-500"
                    style={{ width: `${result.scores.neutral * 100}%` }}
                  />
                </div>
              </div>

              {/* Negative */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-red-600">😢 Negative</span>
                  <span className="font-semibold">{(result.scores.negative * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500 transition-all duration-500"
                    style={{ width: `${result.scores.negative * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Try Another Button */}
            <button
              onClick={() => {
                setText('')
                setResult(null)
              }}
              className="w-full mt-6 px-6 py-3 bg-gray-100 text-gray-700 font-semibold rounded-xl hover:bg-gray-200 transition-all"
            >
              Check Another Vibe
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>© Nikhil P {new Date().getFullYear()}</p>
          <a href="https://github.com/Nikhil-NP/vibe-check" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
            GitHub
          </a>
        </div>
      </div>
    </div>
  )
}

export default App
