from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import text2emotion as te
from typing import Dict, List, Any
import re
import uvicorn

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
    # NEW: Multi-model analysis
    models: Dict[str, Dict[str, float]]  # vader, textblob results
    # NEW: Emotions
    emotions: Dict[str, float]  # joy, anger, sadness, etc.
    dominant_emotion: str
    # NEW: Text insights
    insights: List[str]  # detected patterns
    text_stats: Dict[str, Any]  # word count, readability, etc.

def get_sentiment_data(compound_score: float) -> Dict[str, str]:
    """Return sentiment classification, emoji, vibe label, and color"""
    if compound_score >= 0.5:
        return {
            "sentiment": "very positive",
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

def analyze_text_patterns(text: str) -> List[str]:
    """Detect interesting patterns in text"""
    insights = []
    
    # Exclamation marks (high energy)
    exclamations = text.count('!')
    if exclamations >= 3:
        insights.append(f"⚡ High energy detected ({exclamations} exclamation marks)")
    
    # Question marks (curiosity/uncertainty)
    questions = text.count('?')
    if questions >= 3:
        insights.append(f"🤔 Question-heavy text ({questions} questions)")
    
    # ALL CAPS (intensity/shouting)
    caps_words = re.findall(r'\b[A-Z]{2,}\b', text)
    if len(caps_words) >= 2:
        insights.append(f"📢 Intense language ({len(caps_words)} words in CAPS)")
    
    # Emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport
        "]+", flags=re.UNICODE)
    emojis = emoji_pattern.findall(text)
    if len(emojis) >= 3:
        insights.append(f"😀 Emoji-rich text ({len(emojis)} emojis)")
    
    # Ellipsis (trailing thought)
    if '...' in text or '…' in text:
        insights.append("💭 Contains ellipsis - thoughtful or uncertain")
    
    # Sarcasm indicators
    sarcasm_markers = ['yeah right', 'sure', 'totally', 'obviously', 'of course']
    if any(marker in text.lower() for marker in sarcasm_markers):
        insights.append("🎭 Possible sarcasm detected")
    
    # Negations (sentiment flippers)
    negations = len(re.findall(r'\b(not|no|never|none|nobody|nothing|neither|nowhere|hardly|scarcely|barely)\b', text.lower()))
    if negations >= 2:
        insights.append(f"🔄 Multiple negations ({negations}) - complex sentiment")
    
    # Profanity/strong language (simplified check)
    strong_words = ['hate', 'love', 'amazing', 'terrible', 'awful', 'worst', 'best']
    strong_count = sum(1 for word in strong_words if word in text.lower())
    if strong_count >= 2:
        insights.append("💥 Strong emotional language")
    
    return insights if insights else ["📝 Clean, straightforward text"]

def get_text_stats(text: str) -> Dict:
    """Calculate text statistics"""
    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    sentences = max(sentences, 1)  # Avoid division by zero
    
    # Average word length
    avg_word_length = sum(len(word) for word in words) / max(len(words), 1)
    
    # Formality (longer words = more formal)
    formality_score = min(avg_word_length / 7.0, 1.0)  # Normalize to 0-1
    
    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": sentences,
        "avg_word_length": round(avg_word_length, 1),
        "formality": round(formality_score, 2)
    }

def get_emotion_emoji(emotion: str) -> str:
    """Map emotion to emoji"""
    emotion_map = {
        "Happy": "😊",
        "Angry": "😠",
        "Sad": "😢",
        "Fear": "😨",
        "Surprise": "😮"
    }
    return emotion_map.get(emotion, "😐")

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
    Enhanced sentiment analysis with multi-model approach and text insights
    """
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text is too long (max 5000 characters)")
    
    # === 1. VADER Analysis ===
    vader_scores = vader.polarity_scores(text)
    vader_compound = vader_scores['compound']
    
    # === 2. TextBlob Analysis ===
    blob = TextBlob(text)
    textblob_polarity = blob.sentiment.polarity  # -1 to 1
    textblob_subjectivity = blob.sentiment.subjectivity  # 0 to 1
    
    # Convert TextBlob polarity to pos/neu/neg format
    if textblob_polarity > 0.1:
        tb_sentiment = "positive"
        tb_pos = abs(textblob_polarity)
        tb_neg = 0.0
        tb_neu = 1 - tb_pos
    elif textblob_polarity < -0.1:
        tb_sentiment = "negative"
        tb_neg = abs(textblob_polarity)
        tb_pos = 0.0
        tb_neu = 1 - tb_neg
    else:
        tb_sentiment = "neutral"
        tb_neu = 1.0
        tb_pos = 0.0
        tb_neg = 0.0
    
    # === 3. Emotion Detection ===
    try:
        emotions_dict = te.get_emotion(text)
        # Get dominant emotion
        dominant_emotion = max(emotions_dict.items(), key=lambda x: x[1])[0]
    except:
        # Fallback if emotion detection fails
        emotions_dict = {"Happy": 0, "Angry": 0, "Sad": 0, "Fear": 0, "Surprise": 0}
        dominant_emotion = "Neutral"
    
    # === 4. Consensus Analysis ===
    # Average compound scores for overall sentiment
    avg_compound = (vader_compound + textblob_polarity) / 2
    sentiment_data = get_sentiment_data(avg_compound)
    
    # Calculate confidence based on model agreement
    vader_sent = "positive" if vader_compound > 0.1 else "negative" if vader_compound < -0.1 else "neutral"
    agreement = 1.0 if vader_sent == tb_sentiment else 0.5
    confidence = abs(avg_compound) * agreement
    
    # === 5. Text Insights ===
    insights = analyze_text_patterns(text)
    text_stats = get_text_stats(text)
    
    # Add subjectivity insight
    if textblob_subjectivity > 0.7:
        insights.append("💬 Highly subjective/personal opinion")
    elif textblob_subjectivity < 0.3:
        insights.append("📊 Objective and factual tone")
    
    # Add formality insight
    if text_stats["formality"] > 0.7:
        insights.append("👔 Formal/professional language")
    elif text_stats["formality"] < 0.4:
        insights.append("😎 Casual/informal tone")
    
    # Model agreement insight
    if agreement == 1.0:
        insights.append("✅ All models agree - high confidence!")
    else:
        insights.append("⚠️ Models disagree - nuanced sentiment")
    
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
        color=sentiment_data["color"],
        # NEW fields
        models={
            "vader": {
                "compound": round(vader_compound, 3),
                "positive": round(vader_scores['pos'], 3),
                "neutral": round(vader_scores['neu'], 3),
                "negative": round(vader_scores['neg'], 3)
            },
            "textblob": {
                "polarity": round(textblob_polarity, 3),
                "subjectivity": round(textblob_subjectivity, 3),
                "positive": round(tb_pos, 3),
                "neutral": round(tb_neu, 3),
                "negative": round(tb_neg, 3)
            }
        },
        emotions={
            "joy": round(emotions_dict.get("Happy", 0), 3),
            "anger": round(emotions_dict.get("Angry", 0), 3),
            "sadness": round(emotions_dict.get("Sad", 0), 3),
            "fear": round(emotions_dict.get("Fear", 0), 3),
            "surprise": round(emotions_dict.get("Surprise", 0), 3)
        },
        dominant_emotion=dominant_emotion,
        insights=insights,
        text_stats=text_stats
    )

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
