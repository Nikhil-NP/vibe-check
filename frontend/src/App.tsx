import { useState } from 'react'

interface SentimentResult {
  sentiment: string
  confidence: number
  scores: { positive: number; neutral: number; negative: number }
  vibe: string
  emoji: string
  color: string
  models: {
    vader: { compound: number }
    textblob: { polarity: number; subjectivity: number }
  }
  emotions: { joy: number; anger: number; sadness: number; fear: number; surprise: number }
  dominant_emotion: string
  insights: string[]
  text_stats: { word_count: number; character_count: number; formality: number }
  gemini_analysis?: {
    sentiment: string
    confidence: number
    vibe_description: string
    emotional_tone: string
    key_phrases: string[]
    reasoning: string
    mood_score: number
    energy_level: string
    formality: string
  }
}

interface EnhanceResult {
  writing_tips: string[]
  tone_suggestions: string[]
  improved_version: string
  social_ready: string
  hashtags: string[]
  key_takeaway: string
}

function App() {
  const [text, setText] = useState('')
  const [result, setResult] = useState<SentimentResult | null>(null)
  const [enhance, setEnhance] = useState<EnhanceResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [enhancing, setEnhancing] = useState(false)
  const [error, setError] = useState('')

  const analyzeSentiment = async () => {
    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setEnhance(null)

    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      })

      if (!res.ok) throw new Error('Analysis failed')
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError('Failed to analyze. Is the backend running?')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const enhanceWithAI = async () => {
    if (!result) return

    setEnhancing(true)
    try {
      const res = await fetch('http://localhost:8000/enhance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, sentiment_data: result }),
      })

      if (!res.ok) throw new Error('Enhancement failed')
      const data = await res.json()
      setEnhance(data)
    } catch (err) {
      console.error(err)
    } finally {
      setEnhancing(false)
    }
  }

  const copy = (s: string) => navigator.clipboard?.writeText(s)

  const pct = (v: number) => `${(v * 100).toFixed(1)}%`

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-100 via-purple-50 to-fuchsia-100 py-10 px-4">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-7xl font-black bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 bg-clip-text text-transparent mb-3">
            Vibe Check
          </h1>
          <p className="text-gray-600 text-xl font-medium">
            Multi-model sentiment analysis powered by VADER, TextBlob & emotion AI
          </p>
        </div>

        {/* Input */}
        <div className="backdrop-blur-lg bg-white/60 rounded-3xl shadow-2xl p-8 mb-8 border border-white">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter or paste your text here..."
            className="w-full h-40 p-5 border-2 border-purple-200 rounded-2xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 outline-none transition resize-none bg-white/80"
          />
          
          <div className="mt-5 flex justify-between items-center">
            <span className="text-sm text-gray-600 font-medium">{text.length} characters</span>
            <button
              onClick={analyzeSentiment}
              disabled={loading || !text.trim()}
              className="px-8 py-4 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white font-bold rounded-2xl hover:shadow-xl hover:scale-105 disabled:opacity-50 disabled:scale-100 transition-all"
            >
              {loading ? '🔮 Analyzing...' : '✨ Analyze Sentiment'}
            </button>
          </div>

          {error && <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-lg">{error}</div>}
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6 animate-fade-in">
            
            {/* Main Sentiment Card */}
            <div className="backdrop-blur-lg bg-white/60 rounded-3xl shadow-2xl p-8 border border-white">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-800 mb-2">{result.vibe}</h2>
                  <p className="text-gray-600">Confidence: <span className="font-bold">{pct(result.confidence)}</span></p>
                </div>
                <div className="text-7xl">{result.emoji}</div>
              </div>

              {/* Sentiment Breakdown */}
              <div className="space-y-3 mb-6">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-green-600 font-semibold">😊 Positive</span>
                    <span className="font-bold">{pct(result.scores.positive)}</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500" style={{ width: pct(result.scores.positive) }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600 font-semibold">😐 Neutral</span>
                    <span className="font-bold">{pct(result.scores.neutral)}</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-gray-400" style={{ width: pct(result.scores.neutral) }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-red-600 font-semibold">😢 Negative</span>
                    <span className="font-bold">{pct(result.scores.negative)}</span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div className="h-full bg-red-500" style={{ width: pct(result.scores.negative) }} />
                  </div>
                </div>
              </div>

              {/* Emotions */}
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6">
                <h3 className="font-bold text-gray-800 mb-4">Emotion Breakdown</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
                  {[
                    ['Joy', result.emotions.joy, '😊'],
                    ['Anger', result.emotions.anger, '😠'],
                    ['Sadness', result.emotions.sadness, '😢'],
                    ['Fear', result.emotions.fear, '😨'],
                    ['Surprise', result.emotions.surprise, '😮']
                  ].map(([name, val, emoji]) => (
                    <div key={name as string} className="bg-white rounded-xl p-3">
                      <div className="text-3xl mb-1">{emoji}</div>
                      <div className="text-xs font-semibold text-gray-600">{name}</div>
                      <div className="text-lg font-bold">{pct(val as number)}</div>
                    </div>
                  ))}
                </div>
                <p className="text-sm text-gray-600 mt-4">Dominant: <span className="font-bold">{result.dominant_emotion}</span></p>
              </div>
            </div>

            {/* Gemini AI Side-by-Side Comparison */}
            {result.gemini_analysis && (
              <div className="backdrop-blur-lg bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-3xl shadow-2xl p-8 border-2 border-indigo-200">
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-4xl">🤖</span>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800">Gemini AI Vibe Check</h3>
                    <p className="text-sm text-gray-600">AI-powered sentiment analysis side-by-side</p>
                  </div>
                </div>

                {/* Side by Side Comparison */}
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  {/* Traditional Analysis */}
                  <div className="bg-white/80 rounded-2xl p-6 border-2 border-purple-200">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-2xl">📊</span>
                      <h4 className="font-bold text-gray-800">Traditional Analysis</h4>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm text-gray-600">Sentiment:</span>
                        <p className="text-lg font-bold text-gray-800 capitalize">{result.sentiment}</p>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Confidence:</span>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-purple-500 to-pink-500" 
                              style={{ width: pct(result.confidence) }} 
                            />
                          </div>
                          <span className="text-sm font-bold">{pct(result.confidence)}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Vibe:</span>
                        <p className="text-base font-semibold text-gray-800">{result.vibe}</p>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Method:</span>
                        <p className="text-sm text-gray-700">VADER + TextBlob + HuggingFace</p>
                      </div>
                    </div>
                  </div>

                  {/* Gemini AI Analysis */}
                  <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white border-2 border-indigo-300 shadow-lg">
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-2xl">✨</span>
                      <h4 className="font-bold">Gemini AI Analysis</h4>
                    </div>
                    <div className="space-y-3">
                      <div>
                        <span className="text-sm text-indigo-100">Sentiment:</span>
                        <p className="text-lg font-bold capitalize">{result.gemini_analysis.sentiment}</p>
                      </div>
                      <div>
                        <span className="text-sm text-indigo-100">Confidence:</span>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-3 bg-white/30 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-white" 
                              style={{ width: pct(result.gemini_analysis.confidence) }} 
                            />
                          </div>
                          <span className="text-sm font-bold">{pct(result.gemini_analysis.confidence)}</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-sm text-indigo-100">Vibe:</span>
                        <p className="text-base font-semibold">{result.gemini_analysis.vibe_description}</p>
                      </div>
                      <div>
                        <span className="text-sm text-indigo-100">Method:</span>
                        <p className="text-sm text-indigo-100">Google Gemini Pro AI</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI Insights Details */}
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Emotional Analysis */}
                  <div className="bg-white/80 rounded-2xl p-5 border border-gray-200">
                    <h5 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <span>🎭</span>
                      <span>Emotional Tone</span>
                    </h5>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Tone:</span>
                        <span className="font-bold text-gray-800 capitalize">{result.gemini_analysis.emotional_tone}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Energy Level:</span>
                        <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-bold uppercase">
                          {result.gemini_analysis.energy_level}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Formality:</span>
                        <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-bold uppercase">
                          {result.gemini_analysis.formality}
                        </span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600 mb-1 block">Mood Score:</span>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-indigo-400 to-purple-500" 
                              style={{ width: pct(result.gemini_analysis.mood_score) }} 
                            />
                          </div>
                          <span className="text-xs font-bold text-gray-700">{pct(result.gemini_analysis.mood_score)}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Key Phrases */}
                  <div className="bg-white/80 rounded-2xl p-5 border border-gray-200">
                    <h5 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <span>🔑</span>
                      <span>Key Phrases</span>
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {result.gemini_analysis.key_phrases.map((phrase, i) => (
                        <span 
                          key={i} 
                          className="px-3 py-1.5 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 text-indigo-700 rounded-lg text-sm font-medium"
                        >
                          "{phrase}"
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* AI Reasoning */}
                <div className="mt-6 bg-white/80 rounded-2xl p-5 border border-gray-200">
                  <h5 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <span>🧠</span>
                    <span>AI Reasoning</span>
                  </h5>
                  <p className="text-gray-700 leading-relaxed">{result.gemini_analysis.reasoning}</p>
                </div>

                {/* Comparison Note */}
                <div className="mt-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-200">
                  <p className="text-sm text-gray-700">
                    <span className="font-bold">💡 Note:</span> Traditional models use statistical patterns, 
                    while Gemini AI understands context and nuance. Compare both for comprehensive insights!
                  </p>
                </div>
              </div>
            )}

            {/* No Gemini Notice */}
            {!result.gemini_analysis && (
              <div className="backdrop-blur-lg bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl p-6 border-2 border-blue-200">
                <div className="flex items-start gap-4">
                  <span className="text-3xl">💡</span>
                  <div>
                    <h4 className="font-bold text-gray-800 mb-2">Want AI-Powered Insights?</h4>
                    <p className="text-sm text-gray-600 mb-3">
                      Add your Gemini API key to get side-by-side AI sentiment analysis with reasoning, 
                      emotional tone detection, and key phrase extraction.
                    </p>
                    <a 
                      href="https://makersuite.google.com/app/apikey" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-block px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-semibold transition"
                    >
                      Get API Key →
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Insights & Stats */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="backdrop-blur-lg bg-white/60 rounded-3xl shadow-xl p-6 border border-white">
                <h3 className="font-bold text-gray-800 mb-4">💡 Insights</h3>
                <ul className="space-y-2">
                  {result.insights.map((ins, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                      <span className="text-purple-500">•</span>
                      <span>{ins}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="backdrop-blur-lg bg-white/60 rounded-3xl shadow-xl p-6 border border-white">
                <h3 className="font-bold text-gray-800 mb-4">📊 Text Stats</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Words:</span>
                    <span className="font-bold">{result.text_stats.word_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Characters:</span>
                    <span className="font-bold">{result.text_stats.character_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Formality:</span>
                    <span className="font-bold">{pct(result.text_stats.formality)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Subjectivity:</span>
                    <span className="font-bold">{pct(result.models.textblob.subjectivity)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Enhancement Button */}
            {!enhance && (
              <button
                onClick={enhanceWithAI}
                disabled={enhancing}
                className="w-full py-5 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-bold rounded-2xl hover:shadow-2xl hover:scale-105 disabled:opacity-50 transition-all"
              >
                {enhancing ? '🤖 Enhancing with Gemini AI...' : '🚀 Enhance with AI (optional)'}
              </button>
            )}

            {/* AI Enhancement Results */}
            {enhance && (
              <div className="backdrop-blur-lg bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl shadow-2xl p-8 border-2 border-amber-200">
                <div className="flex items-center gap-3 mb-6">
                  <span className="text-4xl">🤖</span>
                  <h3 className="text-2xl font-bold text-gray-800">AI-Powered Insights</h3>
                </div>

                <div className="space-y-6">
                  {/* Writing Tips */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-3">✍️ Writing Tips</h4>
                    <ul className="space-y-2">
                      {enhance.writing_tips.map((tip, i) => (
                        <li key={i} className="bg-white rounded-lg p-3 text-sm text-gray-700">{tip}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Tone Suggestions */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-3">🎯 Tone Suggestions</h4>
                    <div className="flex flex-wrap gap-2">
                      {enhance.tone_suggestions.map((sug, i) => (
                        <span key={i} className="bg-white px-4 py-2 rounded-full text-sm font-semibold text-gray-700">{sug}</span>
                      ))}
                    </div>
                  </div>

                  {/* Improved Version */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-3">✨ Improved Version</h4>
                    <div className="bg-white rounded-xl p-5">
                      <p className="text-gray-800 leading-relaxed mb-3">{enhance.improved_version}</p>
                      <button onClick={() => copy(enhance.improved_version)} className="px-4 py-2 bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-lg text-sm font-semibold transition">
                        📋 Copy
                      </button>
                    </div>
                  </div>

                  {/* Social Ready */}
                  <div>
                    <h4 className="font-bold text-gray-800 mb-3">🐦 Social Media Ready</h4>
                    <div className="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl p-5 text-white">
                      <p className="text-lg mb-3">{enhance.social_ready}</p>
                      <div className="flex items-center justify-between flex-wrap gap-3">
                        <div className="flex gap-2 flex-wrap">
                          {enhance.hashtags.map((tag, i) => (
                            <span key={i} className="bg-white/20 px-3 py-1 rounded-full text-sm">#{tag}</span>
                          ))}
                        </div>
                        <button onClick={() => copy(enhance.social_ready + '\n\n' + enhance.hashtags.map(t => '#' + t).join(' '))} className="px-4 py-2 bg-white text-blue-600 rounded-lg font-bold hover:scale-105 transition">
                          Copy Tweet
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Key Takeaway */}
                  <div className="bg-gradient-to-r from-violet-500 to-purple-500 rounded-xl p-5 text-white">
                    <h4 className="font-bold mb-2">💎 Key Takeaway</h4>
                    <p className="text-lg">{enhance.key_takeaway}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Reset Button */}
            <button
              onClick={() => { setText(''); setResult(null); setEnhance(null); }}
              className="w-full py-4 backdrop-blur-lg bg-white/60 hover:bg-white/80 text-gray-700 font-bold rounded-2xl transition border border-white"
            >
              ✨ Analyze Another Text
            </button>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-16 text-gray-500 text-sm">
          <p className="font-semibold">© Nikhil P {new Date().getFullYear()} </p>
          <a href="https://github.com/Nikhil-NP/vibe-check" target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:underline font-semibold mt-2 inline-block">
            GitHub 
          </a>
        </div>
      </div>
    </div>
  )
}

export default App