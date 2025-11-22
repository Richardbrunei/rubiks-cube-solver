# Backend Deployment Guide for Render

This guide will help you deploy the Rubik's Cube backend API to Render.

## ✅ Pre-Deployment Checklist

All necessary files have been created:
- ✅ `Procfile` - Gunicorn start command
- ✅ `runtime.txt` - Python 3.9.18
- ✅ `requirements.txt` - All dependencies
- ✅ `.gitignore` - Ignore unnecessary files
- ✅ CORS enabled in `backend_api.py`

## 📋 Step 1: Push to GitHub

If this is a new repository:

```bash
cd api
git init
git add .
git commit -m "Initial commit - Backend ready for Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rubiks-cube-backend.git
git push -u origin main
```

If you're updating an existing repository:

```bash
cd api
git add .
git commit -m "Prepare backend for Render deployment"
git push origin main
```

## 🚀 Step 2: Deploy to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** (authorize if needed)
4. Select your backend repository
5. Click **"Connect"**

### Configuration Settings:

| Setting | Value |
|---------|-------|
| **Name** | `rubiks-cube-backend` |
| **Environment** | `Python 3` |
| **Branch** | `main` |
| **Root Directory** | (leave blank or use `api` if in subdirectory) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app` |
| **Instance Type** | `Free` |

6. Click **"Create Web Service"**

## ⏱️ Step 3: Wait for Deployment

- Build takes 5-10 minutes (OpenCV installation is slow)
- Watch the logs for: `Your service is live 🎉`
- Note your backend URL: `https://rubiks-cube-backend.onrender.com`

## 🧪 Step 4: Test Your Backend

### Test Health Check

```bash
curl https://rubiks-cube-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Rubik's Cube Color Detection API is running"
}
```

### Test API Endpoints

```bash
# Test endpoint
curl https://rubiks-cube-backend.onrender.com/api/test

# Color mappings
curl https://rubiks-cube-backend.onrender.com/api/color-mappings

# Camera status
curl https://rubiks-cube-backend.onrender.com/api/camera-status
```

## 🔗 Step 5: Update Frontend

Update your frontend's `scripts/config.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://rubiks-cube-backend.onrender.com';  // Your backend URL

export const CONFIG = {
    API_BASE_URL: API_BASE_URL,
    // ... rest of config
};
```

## 🐛 Troubleshooting

### Issue: Build Fails with OpenCV Error

**Solution**: The `requirements.txt` already uses `opencv-python-headless` which is designed for servers.

### Issue: CORS Errors

**Solution**: CORS is already configured in `backend_api.py` to allow all origins. If you need to restrict it, update the CORS configuration.

### Issue: Backend Sleeps (Free Tier)

**Solution**: Render's free tier sleeps after 15 minutes of inactivity. First request will take 30-60 seconds to wake up. Use UptimeRobot (https://uptimerobot.com) to ping every 5 minutes, or upgrade to paid tier.

### Issue: Module Import Errors

**Solution**: The backend is designed to work with fallback functions when external modules aren't available. Check the logs to see which modules loaded successfully.

## 📝 Important Notes

1. **Backend Path**: The backend uses environment variable `BACKEND_PATH` or falls back to built-in functions
2. **Production Mode**: When deployed, the backend automatically uses fallback color detection if external modules aren't available
3. **Free Tier Limitations**: 
   - 750 hours/month
   - Sleeps after 15 minutes of inactivity
   - Limited CPU and memory

## 🎉 Success!

Once deployed, your backend will be available at:
- **Backend URL**: `https://rubiks-cube-backend.onrender.com`
- **API Endpoints**: `https://rubiks-cube-backend.onrender.com/api/*`

Your backend is now ready to serve your Rubik's Cube frontend! 🚀
