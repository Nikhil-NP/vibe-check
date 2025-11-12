# 🌟 Vibe Check

A modern, AI-powered sentiment analysis application that provides comprehensive text analysis using multiple models including VADER, TextBlob, and Google's Gemini AI.

## ✨ Features

- **Multi-Model Sentiment Analysis**: Combines VADER, TextBlob, and optional HuggingFace models
- **Gemini AI Integration**: Side-by-side comparison with AI-powered contextual analysis
- **Emotion Detection**: Analyzes 5 core emotions (Joy, Anger, Sadness, Fear, Surprise)
- **Text Insights**: Pattern detection, formality analysis, subjectivity scoring
- **AI Enhancement**: Optional writing tips and improvements via Gemini AI
- **Beautiful UI**: Modern gradient design with smooth animations

## 🏗️ Architecture

```
vibe-check/
├── backend/              # Python FastAPI server
│   ├── main.py          # Core API with sentiment analysis
│   ├── requirements.txt # Python dependencies
│   ├── .env            # Environment variables (API keys)
│   └── README.md
└── frontend/            # React TypeScript app
    ├── src/
    │   ├── App.tsx      # Main UI component
    │   ├── index.css    # Tailwind styles
    │   └── main.tsx     # Entry point
    ├── package.json
    └── tailwind.config.js
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- pnpm (or npm)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
# Optional: HF_API_TOKEN=your_huggingface_token
```

4. Start the server:
```bash
uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
pnpm install  # or: npm install
```

3. Start development server:
```bash
pnpm dev  # or: npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🔑 API Keys

### Gemini AI (Required for AI features)
1. Get API key from: https://makersuite.google.com/app/apikey
2. Add to `backend/.env`: `GEMINI_API_KEY=your_key`

### HuggingFace (Optional)
1. Get token from: https://huggingface.co/settings/tokens
2. Add to `backend/.env`: `HF_API_TOKEN=your_token`

## 📡 API Endpoints

### `POST /analyze`
Analyzes text sentiment with multiple models.

**Request:**
```json
{
  "text": "I am absolutely thrilled about this amazing opportunity!"
}
```

**Response:**
```json
{
  "sentiment": "very positive",
  "confidence": 0.89,
  "vibe": "Super Positive Vibes!",
  "emoji": "🌟",
  "emotions": {
    "joy": 0.85,
    "anger": 0.0,
    "sadness": 0.0,
    "fear": 0.05,
    "surprise": 0.10
  },
  "gemini_analysis": {
    "sentiment": "positive",
    "confidence": 0.92,
    "vibe_description": "Highly enthusiastic and optimistic",
    "emotional_tone": "excited",
    "energy_level": "high",
    "formality": "casual",
    "key_phrases": ["absolutely thrilled", "amazing opportunity"],
    "reasoning": "Strong positive language with excitement indicators"
  }
}
```

### `POST /enhance`
Get AI-powered writing improvements and suggestions.

### `POST /suggest`
Generate text rewrites (softer, professional, concise versions).

### `GET /health`
Health check endpoint.

## 🎨 Features Overview

### Traditional Sentiment Analysis
- **VADER**: Rule-based sentiment analysis optimized for social media
- **TextBlob**: Pattern-based sentiment with subjectivity scoring
- **HuggingFace**: Optional transformer-based models

### Gemini AI Analysis
- Natural language understanding
- Context-aware sentiment detection
- Creative vibe descriptions
- Key phrase extraction
- Reasoning explanations
- Energy level and formality detection

### Emotion Detection
- Joy/Happiness
- Anger
- Sadness
- Fear/Anxiety
- Surprise

### Text Insights
- High energy detection (exclamation marks)
- Question-heavy text
- ALL CAPS intensity
- Emoji usage
- Sarcasm indicators
- Negation patterns
- Strong emotional language

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **VADER Sentiment**: Social media optimized sentiment analysis
- **TextBlob**: Natural language processing
- **text2emotion**: Emotion detection
- **Google Gemini AI**: Advanced language model
- **Python 3.8+**

### Frontend
- **React 18**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS
- **pnpm**: Fast package manager

## 📦 Deployment

### Backend Deployment
- Deploy to services like Railway, Render, or Heroku
- Set environment variables in platform settings
- Use `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment
- Deploy to Vercel, Netlify, or Cloudflare Pages
- Update API endpoint in `App.tsx`
- Build: `pnpm build`
- Output: `dist/` directory

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 👨‍💻 Author

**Nikhil P**
- GitHub: [@Nikhil-NP](https://github.com/Nikhil-NP)

## 🙏 Acknowledgments

- VADER Sentiment Analysis
- TextBlob NLP Library
- Google Gemini AI
- FastAPI Framework
- React & Tailwind CSS

---

Made with ❤️ for understanding human sentiment