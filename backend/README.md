# Vibe Check Backend

FastAPI backend for sentiment analysis.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server runs on: http://localhost:8000

## API Endpoints

- `GET /` - API info
- `POST /analyze` - Analyze text sentiment
- `GET /health` - Health check

## Deploy to Render

1. Push to GitHub
2. Create new Web Service on Render
3. Connect your repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
