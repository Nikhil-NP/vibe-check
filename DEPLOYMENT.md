# 🚀 Deployment Guide

## Quick Deploy Options

### Option 1: Railway (Recommended for Backend)

#### Backend Deployment
1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set root directory to `/backend`
5. Add environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `PORT`: 8000 (Railway sets this automatically)
6. Railway will auto-detect Python and deploy!

#### Frontend Deployment (Vercel)
1. Create account at [vercel.com](https://vercel.com)
2. Click "New Project" → Import your repository
3. Set root directory to `/frontend`
4. Build command: `pnpm build`
5. Output directory: `dist`
6. Update `App.tsx` with your backend URL:
   ```tsx
   const res = await fetch('https://your-backend.railway.app/analyze', {
   ```
7. Deploy!

### Option 2: All-in-One with Render

#### Backend
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your repo
4. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables: Add `GEMINI_API_KEY`

#### Frontend
1. New → Static Site
2. Settings:
   - Root Directory: `frontend`
   - Build Command: `pnpm install && pnpm build`
   - Publish Directory: `dist`
3. Add environment variable:
   - `VITE_API_URL`: Your backend URL

### Option 3: Docker Deployment

#### Create Dockerfile for Backend
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Create Dockerfile for Frontend
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

## 🔒 Security Checklist

- [ ] Never commit `.env` file with actual API keys
- [ ] Use `.env.example` for documentation
- [ ] Set proper CORS origins in production (not `["*"]`)
- [ ] Use HTTPS for production deployment
- [ ] Rate limit API endpoints
- [ ] Add API key validation
- [ ] Monitor API usage and costs

## 🔧 Production Optimizations

### Backend
1. **Update CORS** in `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

2. **Add rate limiting**:
   ```bash
   pip install slowapi
   ```

3. **Use gunicorn** for production:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend
1. **Update API URL** for production in `App.tsx`
2. **Enable production build optimizations** (already configured)
3. **Add analytics** if needed
4. **Configure CDN** for assets

## 📊 Monitoring

### Recommended Tools
- **Backend**: [Sentry](https://sentry.io) for error tracking
- **Frontend**: Google Analytics or Plausible
- **API Usage**: Monitor Gemini API quota
- **Uptime**: UptimeRobot or Better Uptime

## 💰 Cost Estimation

### Gemini AI
- Free tier: 60 requests per minute
- Paid: Check [Google AI pricing](https://ai.google.dev/pricing)

### Hosting
- **Railway/Render Free Tier**: 
  - Backend: Free with limitations
  - Good for demos/portfolio
  
- **Vercel/Netlify Free Tier**:
  - Frontend: Free for personal projects
  - 100GB bandwidth/month

### Production Costs (Estimated)
- Backend: $5-20/month (Railway/Render)
- Frontend: Free (Vercel/Netlify)
- Gemini API: $0-50/month (depends on usage)
- **Total**: ~$5-70/month

## 🐛 Troubleshooting

### "Module not found" errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

### CORS errors in production
- Update `allow_origins` in backend
- Check if backend URL is correct in frontend

### Gemini API not working
- Verify API key is set correctly
- Check API quota/billing
- Ensure model name is correct (gemini-2.0-flash)

### Frontend can't connect to backend
- Check if backend is running
- Verify URL in frontend code
- Check CORS settings

## 📱 Mobile Optimization

The app is already responsive! Test on:
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] iPad/Tablet
- [ ] Desktop (Chrome, Firefox, Safari)

## 🎯 Post-Deployment

1. Test all features in production
2. Set up error monitoring
3. Add analytics
4. Monitor API costs
5. Gather user feedback
6. Consider adding:
   - User accounts
   - Analysis history
   - Export results feature
   - Batch analysis
   - API authentication

---

**Your app is ready for the world! 🌍✨**
