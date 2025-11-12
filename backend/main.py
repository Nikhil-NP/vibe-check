from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from typing import Dict, List, Any, Optional
import re
import uvicorn
import os
import requests
from math import copysign
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    # NEW: Multi-model analysis (vader, textblob, optional hf)
    models: Dict[str, Dict[str, float]]  # vader, textblob, optional hf
    # NEW: Emotions
    emotions: Dict[str, float]  # joy, anger, sadness, etc.
    dominant_emotion: str
    # NEW: Text insights
    insights: List[str]  # detected patterns
    text_stats: Dict[str, Any]  # word count, readability, etc.
    # NEW: Gemini AI analysis
    gemini_analysis: Optional[Dict[str, Any]] = None  # AI-powered sentiment analysis

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


def detect_emotions_robust(text: str) -> tuple[Dict[str, float], str]:
    """
    Rule-based emotion detection without external dependencies.
    Returns (emotions_dict, dominant_emotion)
    """
    text_lower = text.lower()
    
    # Happy indicators
    happy_words = ['happy', 'joy', 'great', 'excellent', 'wonderful', 'amazing', 
                   'love', 'good', 'best', 'awesome', 'fantastic', 'thrilled', 'excited',
                   'delighted', 'pleased', 'glad', 'perfect', 'brilliant', '😊', '😀', '🎉', '❤️']
    happy_score = sum(1 for word in happy_words if word in text_lower)
    
    # Angry indicators
    angry_words = ['angry', 'hate', 'terrible', 'awful', 'worst', 'disgusting',
                   'furious', 'mad', 'rage', 'annoyed', 'frustrated', 'irritated', '😠', '😡', '🤬']
    angry_score = sum(1 for word in angry_words if word in text_lower)
    
    # Sad indicators
    sad_words = ['sad', 'depressed', 'unhappy', 'miserable', 'disappointed',
                 'sorry', 'unfortunate', 'bad', 'upset', 'down', 'heartbroken', '😢', '😭', '💔']
    sad_score = sum(1 for word in sad_words if word in text_lower)
    
    # Fear indicators
    fear_words = ['fear', 'scared', 'afraid', 'worried', 'anxious', 'nervous',
                  'terrified', 'panic', 'concern', 'frightened', '😨', '😰']
    fear_score = sum(1 for word in fear_words if word in text_lower)
    
    # Surprise indicators
    surprise_words = ['surprise', 'shocked', 'amazed', 'unexpected', 'wow',
                      'omg', 'unbelievable', 'incredible', 'astonishing', '😮', '😲']
    surprise_score = sum(1 for word in surprise_words if word in text_lower)
    
    # Normalize scores
    total_score = max(happy_score + angry_score + sad_score + fear_score + surprise_score, 1)
    
    emotions_dict = {
        "Happy": round(happy_score / total_score, 3),
        "Angry": round(angry_score / total_score, 3),
        "Sad": round(sad_score / total_score, 3),
        "Fear": round(fear_score / total_score, 3),
        "Surprise": round(surprise_score / total_score, 3)
    }
    
    # If no emotion detected, use neutral distribution
    if sum(emotions_dict.values()) == 0:
        emotions_dict = {"Happy": 0.2, "Angry": 0.2, "Sad": 0.2, "Fear": 0.2, "Surprise": 0.2}
        dominant_emotion = "Neutral"
    else:
        dominant_emotion = max(emotions_dict.items(), key=lambda x: x[1])[0]
    
    return emotions_dict, dominant_emotion

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


def expand_contractions(text: str) -> str:
    """A small contraction expansion to help basic preprocessing without extra deps."""
    contractions = {
        "can't": "cannot",
        "won't": "will not",
        "n't": " not",
        "'re": " are",
        "'s": " is",
        "'d": " would",
        "'ll": " will",
        "'ve": " have",
        "'m": " am",
    }
    s = text
    for k, v in contractions.items():
        s = re.sub(k, v, s, flags=re.IGNORECASE)
    return s


def preprocess_text(text: str) -> str:
    """Run lightweight preprocessing steps to normalize text before analysis."""
    t = text.strip()
    # Normalize whitespace
    t = re.sub(r"\s+", " ", t)
    # Expand simple contractions
    t = expand_contractions(t)
    return t


def call_hf_sentiment(text: str) -> Optional[Dict[str, float]]:
    """Call Hugging Face Inference API if HF_API_TOKEN is provided.
    Returns a dict with keys "compound" or label scores depending on model output.
    """
    hf_token = os.environ.get("HF_API_TOKEN")
    hf_model = os.environ.get("HF_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
    if not hf_token:
        return None

    url = f"https://api-inference.huggingface.co/models/{hf_model}"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": text}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        # Typical output: [{"label":"POSITIVE","score":0.99}, ...]
        if isinstance(data, dict) and data.get("error"):
            return None
        if isinstance(data, list):
            # Convert to a simple polarity -1..1 using label mapping
            score_map = {"POSITIVE": 1.0, "NEGATIVE": -1.0, "NEUTRAL": 0.0}
            # Weighted average by score
            total = 0.0
            weight = 0.0
            for item in data:
                label = item.get("label", "")
                s = float(item.get("score", 0.0))
                total += score_map.get(label.upper(), 0.0) * s
                weight += s
            polarity = (total / weight) if weight else 0.0
            return {"polarity": round(polarity, 3)}
    except Exception:
        return None
    return None


def generate_rewrites(text: str) -> Dict[str, str]:
    """Create simple rule-based rewrites: softer, professional, concise."""
    s = text.strip()

    # Softer: reduce exclamations, soften strong words
    softer = re.sub(r"!+", "!", s)
    softer = re.sub(r"\b(hate|terrible|awful|worst)\b", lambda m: {
        'hate':'dislike', 'terrible':'unpleasant', 'awful':'unfortunate', 'worst':'not great'
    }[m.group(0).lower()], softer, flags=re.IGNORECASE)

    # Professional: expand contractions, remove slang, avoid emojis/punct-heavy endings
    prof = expand_contractions(s)
    prof = re.sub(r"\b(imo|idk|u)\b", lambda m: {'imo':'in my opinion','idk':'I do not know','u':'you'}[m.group(0).lower()], prof, flags=re.IGNORECASE)
    # remove unusual punctuation but keep common separators and quotes
    prof = re.sub(r"[^\w\s\.-,\'\"]+", '', prof)

    # Concise: keep first 2 sentences, remove fluff
    sentences = re.split(r'(?<=[.!?])\s+', s)
    concise = ' '.join(sentences[:2]) if sentences else s
    if len(concise) > 200:
        concise = concise[:197].rsplit(' ', 1)[0] + '...'

    return {
        'softer': softer,
        'professional': prof,
        'concise': concise
    }


class SuggestInput(BaseModel):
    text: str


@app.post('/suggest')
def suggest_rewrites(payload: SuggestInput):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail='Text cannot be empty')
    rewrites = generate_rewrites(text)
    return {
        'original': text,
        'suggestions': rewrites
    }


class EnhanceInput(BaseModel):
    text: str
    sentiment_data: Optional[Dict[str, Any]] = None


class EnhanceResponse(BaseModel):
    writing_tips: List[str]
    tone_suggestions: List[str]
    improved_version: str
    social_ready: str
    hashtags: List[str]
    key_takeaway: str


def call_gemini_api(prompt: str) -> Optional[str]:
    """Call Google Gemini API using GEMINI_API_KEY env var."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("geminiapi")
    if not api_key:
        print("No Gemini API key found")
        return None
    
    # Use v1beta API with gemini-2.0-flash model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800,
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            print(f"Gemini API error: {resp.status_code} - {resp.text[:200]}")
            return None
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return None
    except Exception as e:
        print(f"Gemini API exception: {str(e)}")
        return None


def get_gemini_vibe_check(text: str) -> Optional[Dict[str, Any]]:
    """
    Get AI-powered vibe check from Gemini.
    Returns sentiment analysis with reasoning and creative insights.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("geminiapi")
    if not api_key:
        print("No Gemini API key configured")
        return None
    
    prompt = f"""Analyze the sentiment and vibe of this text. Return ONLY valid JSON with this exact structure:

{{
  "sentiment": "positive/negative/neutral",
  "confidence": 0.85,
  "vibe_description": "brief creative description of the overall vibe",
  "emotional_tone": "the dominant emotional tone",
  "key_phrases": ["notable phrase 1", "notable phrase 2"],
  "reasoning": "brief explanation of why you arrived at this sentiment",
  "mood_score": 0.75,
  "energy_level": "high/medium/low",
  "formality": "formal/casual/neutral"
}}

Text to analyze:
"{text}"

Return only the JSON object, no markdown formatting or additional text."""

    response = call_gemini_api(prompt)
    if not response:
        print("No response from Gemini API")
        return None
    
    try:
        # Clean up response
        cleaned = response.strip()
        
        # Remove markdown code blocks if present
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            cleaned = '\n'.join(lines)
        
        # Extract JSON
        jstart = cleaned.find('{')
        jend = cleaned.rfind('}') + 1
        if jstart >= 0 and jend > jstart:
            json_str = cleaned[jstart:jend]
            parsed = json.loads(json_str)
            print(f"Gemini analysis successful: {parsed.get('sentiment', 'unknown')}")
            return parsed
        else:
            print(f"No JSON found in Gemini response: {cleaned[:200]}")
        return None
    except json.JSONDecodeError as e:
        print(f"Gemini JSON parsing error: {str(e)}")
        print(f"Response was: {response[:300]}")
        return None
    except Exception as e:
        print(f"Gemini unexpected error: {str(e)}")
        return None


@app.post('/enhance', response_model=EnhanceResponse)
def enhance_with_ai(payload: EnhanceInput):
    """Optional AI enhancement using Gemini for writing tips and improvements."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail='Text cannot be empty')

    # If no Gemini API key, provide rule-based suggestions
    if not os.environ.get("GEMINI_API_KEY"):
        vader_scores = vader.polarity_scores(text)
        compound = vader_scores['compound']
        
        tips = []
        if compound < -0.2:
            tips.append("Consider softening negative language")
            tips.append("Add constructive alternatives")
        elif compound > 0.5:
            tips.append("Great positive tone!")
        else:
            tips.append("Consider adding more emotional language")
        
        improved = generate_rewrites(text).get('professional', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        social = ' '.join(sentences[:2])[:240] if sentences else text[:240]
        
        return EnhanceResponse(
            writing_tips=tips,
            tone_suggestions=["Add specific examples", "Use active voice"],
            improved_version=improved,
            social_ready=social,
            hashtags=["#communication", "#writing"],
            key_takeaway="Gemini AI not configured. Set GEMINI_API_KEY for AI-powered suggestions."
        )

    # Build Gemini prompt
    sentiment_info = ""
    if payload.sentiment_data:
        sentiment_info = f"\n\nCurrent sentiment analysis: {payload.sentiment_data.get('sentiment', 'neutral')} (confidence: {payload.sentiment_data.get('confidence', 0)})"
    
    prompt = f"""Analyze this text and provide actionable writing improvements. Return ONLY valid JSON with these keys:

{{
  "writing_tips": ["3-4 specific actionable tips"],
  "tone_suggestions": ["2-3 tone adjustments"],
  "improved_version": "rewritten version with better flow",
  "social_ready": "engaging social media version (max 240 chars)",
  "hashtags": ["3 relevant hashtags without # symbol"],
  "key_takeaway": "one sentence main insight"
}}

Text:{sentiment_info}

"{text}"

Return only the JSON, no markdown formatting."""

    response = call_gemini_api(prompt)
    if not response:
        raise HTTPException(status_code=502, detail="Gemini API request failed")

    try:
        cleaned = response.strip()
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            cleaned = '\n'.join(lines[1:-1])
        
        jstart = cleaned.find('{')
        jend = cleaned.rfind('}') + 1
        if jstart >= 0 and jend > jstart:
            parsed = json.loads(cleaned[jstart:jend])
            return EnhanceResponse(
                writing_tips=parsed.get('writing_tips', []),
                tone_suggestions=parsed.get('tone_suggestions', []),
                improved_version=parsed.get('improved_version', ''),
                social_ready=parsed.get('social_ready', ''),
                hashtags=parsed.get('hashtags', []),
                key_takeaway=parsed.get('key_takeaway', '')
            )
        raise ValueError("No valid JSON in response")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'Failed to parse Gemini response: {str(e)}')


@app.post("/analyze", response_model=VibeResponse)
def analyze_vibe(input_data: TextInput):
    """
    Enhanced sentiment analysis with multi-model approach and text insights
    """
    text = preprocess_text(input_data.text)
    
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
    
    # === 3. Emotion Detection (Improved) ===
    emotions_dict, dominant_emotion = detect_emotions_robust(text)
    
    # === 4. Optional Hugging Face Analysis (if configured) ===
    hf_result = call_hf_sentiment(text)
    
    # === 5. Gemini AI Vibe Check (if configured) ===
    gemini_analysis = get_gemini_vibe_check(text)

    # === 6. Consensus / Ensemble Analysis ===
    # Weighted combination: vader (0.3), textblob (0.3), hf (0.4 if present)
    weights = {"vader": 0.3, "textblob": 0.3}
    if hf_result:
        weights["hf"] = 0.4
    else:
        # normalize to sum to 1
        weights["vader"] = 0.5
        weights["textblob"] = 0.5

    # map each model to a polarity in -1..1
    vader_p = vader_compound
    tb_p = textblob_polarity
    hf_p = hf_result.get("polarity") if hf_result else None

    total = vader_p * weights.get("vader", 0) + tb_p * weights.get("textblob", 0)
    if hf_p is not None:
        total += hf_p * weights.get("hf", 0)
    avg_compound = total
    sentiment_data = get_sentiment_data(avg_compound)
    
    # Calculate confidence: combination of absolute polarity and agreement
    vader_sent = "positive" if vader_compound > 0.1 else "negative" if vader_compound < -0.1 else "neutral"
    tb_sent = tb_sentiment
    models_votes = [vader_sent, tb_sent]
    if hf_p is not None:
        hf_sent = "positive" if hf_p > 0.1 else "negative" if hf_p < -0.1 else "neutral"
        models_votes.append(hf_sent)
    # agreement score: fraction of models that agree on majority
    majority = max(set(models_votes), key=models_votes.count)
    agree_count = models_votes.count(majority)
    agreement = agree_count / len(models_votes)

    # confidence combines agreement and signal strength
    confidence = min(1.0, abs(avg_compound) * (0.6 + 0.4 * agreement))
    
    # === 6. Text Insights ===
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
    elif agreement >= 0.66:
        insights.append("👍 Most models agree")
    else:
        insights.append("⚠️ Models disagree - nuanced sentiment")
    
    # Add Gemini insight if available
    if gemini_analysis:
        insights.append(f"🤖 AI detected {gemini_analysis.get('energy_level', 'medium')} energy level")
    
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
                ,
                **({"hf": {"polarity": round(hf_p, 3)}} if hf_p is not None else {})
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
        text_stats=text_stats,
        gemini_analysis=gemini_analysis
    )

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
