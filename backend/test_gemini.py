import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY')
print(f'API Key found: {bool(api_key)}')

if not api_key:
    print("No API key found in .env")
    exit(1)

# Use v1beta API with gemini-2.0-flash model
url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

prompt = """Analyze the sentiment of this text. Return ONLY valid JSON with this structure:
{"sentiment": "positive", "confidence": 0.85, "vibe_description": "brief description", "emotional_tone": "tone", "key_phrases": ["phrase1"], "reasoning": "why", "mood_score": 0.75, "energy_level": "high", "formality": "casual"}

Text: "I am so happy about this amazing opportunity!"

Return only JSON."""

headers = {
    'Content-Type': 'application/json',
    'X-goog-api-key': api_key
}

body = {
    'contents': [{
        'parts': [{'text': prompt}]
    }],
    'generationConfig': {
        'temperature': 0.7,
        'maxOutputTokens': 800,
    }
}

try:
    print("\nSending request to Gemini API...")
    resp = requests.post(url, headers=headers, json=body, timeout=30)
    print(f'Status: {resp.status_code}')
    
    if resp.status_code == 200:
        data = resp.json()
        print(f'Response keys: {list(data.keys())}')
        
        if 'candidates' in data:
            print(f'Candidates: {len(data["candidates"])}')
            if data['candidates']:
                content = data['candidates'][0].get('content', {})
                parts = content.get('parts', [])
                if parts:
                    text = parts[0].get('text', '')
                    print(f'\nText length: {len(text)}')
                    print(f'\nGemini Response:\n{text}')
                    
                    # Try to parse JSON
                    cleaned = text.strip()
                    if cleaned.startswith('```'):
                        lines = cleaned.split('\n')
                        if lines[0].startswith('```'):
                            lines = lines[1:]
                        if lines and lines[-1].startswith('```'):
                            lines = lines[:-1]
                        cleaned = '\n'.join(lines)
                    
                    jstart = cleaned.find('{')
                    jend = cleaned.rfind('}') + 1
                    if jstart >= 0 and jend > jstart:
                        try:
                            json_str = cleaned[jstart:jend]
                            parsed = json.loads(json_str)
                            print(f'\n✅ Parsed JSON successfully!')
                            print(json.dumps(parsed, indent=2))
                        except Exception as e:
                            print(f'\n❌ Failed to parse JSON: {e}')
                            print(f'Attempted to parse: {json_str[:200]}')
                    else:
                        print(f'\n❌ No JSON found in response')
    else:
        print(f'❌ Error response: {resp.text[:500]}')
        
except Exception as e:
    print(f'❌ Exception: {e}')
    import traceback
    traceback.print_exc()
