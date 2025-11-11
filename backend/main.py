from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict

app = FastAPI(title="Vibe Check API", version="1.0.0")

# CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

# Initialize VADER sentiment analyzer
vader = SentimentIntensityAnalyzer()

class TextInput(BaseModel):
    text: str

class VibeResponse(BaseModel):
    sentiment: str  # positive, neutral, negative
    confidence: float  # 0-1
    scores: Dict[str, float]  # positive, neutral, negative breakdown
    vibe: str  # friendly description
    emoji: str
    color: str  # hex color for UI

def get_sentiment_data(compound_score: float) -> Dict[str, str]:
    """Return sentiment classification, emoji, vibe label, and color"""
    if compound_score >= 0.5:
        return {
            "sentiment": "positive",
            "emoji": "🌟",
            "vibe": "Super Positive Vibes!",
            "color": "#10b981"  # green
        }
    elif compound_score >= 0.2:
        return {
            "sentiment": "positive",
            "emoji": "😊",
            "vibe": "Pretty Positive",
            "color": "#22c55e"  # light green
        }
    elif compound_score >= -0.2:
        return {
            "sentiment": "neutral",
            "emoji": "😐",
            "vibe": "Neutral Vibes",
            "color": "#6b7280"  # gray
        }
    elif compound_score >= -0.5:
        return {
            "sentiment": "negative",
            "emoji": "😕",
            "vibe": "Slightly Negative",
            "color": "#f59e0b"  # orange
        }
    else:
        return {
            "sentiment": "negative",
            "emoji": "😤",
            "vibe": "Very Negative",
            "color": "#ef4444"  # red
        }

@app.get("/")
def root():
    return {
        "message": "Vibe Check API is running! 🌟",
        "endpoints": {
            "/analyze": "POST - Analyze text sentiment",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "vibe-check-api"}

@app.post("/analyze", response_model=VibeResponse)
def analyze_vibe(input_data: TextInput):
    """
    Analyze the vibe/sentiment of input text
    """
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text is too long (max 5000 characters)")
    
    # VADER sentiment analysis
    vader_scores = vader.polarity_scores(text)
    
    # Get compound score and sentiment data
    compound_score = vader_scores['compound']
    sentiment_data = get_sentiment_data(compound_score)
    
    # Calculate confidence (how far from neutral)
    confidence = abs(compound_score)
    
    return VibeResponse(
        sentiment=sentiment_data["sentiment"],
        confidence=round(confidence, 3),
        scores={
            "positive": round(vader_scores['pos'], 3),
            "neutral": round(vader_scores['neu'], 3),
            "negative": round(vader_scores['neg'], 3),
        },
        vibe=sentiment_data["vibe"],
        emoji=sentiment_data["emoji"],
        color=sentiment_data["color"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
