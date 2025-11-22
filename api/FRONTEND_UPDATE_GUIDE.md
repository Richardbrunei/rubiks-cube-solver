# 🎨 Frontend Update Guide

Your backend is now deployed! Here's what you need to do in your **frontend repository**.

---

## 📍 What's Your Backend URL?

First, get your backend URL from Render:

```
https://rubiks-cube-backend.onrender.com
```

Or whatever custom name you chose.

---

## 🔧 Step 1: Update Frontend Config

In your **frontend repository**, find and update `scripts/config.js`:

### Before:
```javascript
export const CONFIG = {
    API_BASE_URL: 'http://localhost:5000',
    // ...
};
```

### After:
```javascript
// Detect environment
const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';

// Set API base URL based on environment
const API_BASE_URL = isDevelopment 
    ? 'http://localhost:5000'  // Local backend
    : 'https://rubiks-cube-backend.onrender.com';  // ← Your Render URL

export const CONFIG = {
    API_BASE_URL: API_BASE_URL,
    
    API_ENDPOINTS: {
        COLOR_MAPPINGS: '/api/color-mappings',
        VALIDATE_CUBE: '/api/validate-cube',
        DETECT_COLORS: '/api/detect-colors',
        DETECT_COLORS_FAST: '/api/detect-colors-fast',
        SOLVE_CUBE: '/api/solve-cube'
    }
    // ... rest of your config
};
```

---

## 🔧 Step 2: Fix Hardcoded URLs

Search your frontend for any hardcoded `localhost:5000` URLs:

### Check these files:
- `scripts/solve-button.js`
- `scripts/camera-capture.js`
- `scripts/cube-state.js`
- Any other JavaScript files

### Find and Replace:

**Before:**
```javascript
fetch('http://localhost:5000/api/solve-cube', {
```

**After:**
```javascript
import { CONFIG } from './config.js';

fetch(`${CONFIG.API_BASE_URL}/api/solve-cube`, {
```

---

## 🧪 Step 3: Test Locally

Before deploying, test that your frontend can connect to the deployed backend:

```bash
# In your frontend directory
python -m http.server 8000
```

Then open http://localhost:8000 and:

1. Open browser console (F12)
2. Check for CORS errors
3. Test cube functionality
4. Verify API calls go to your Render URL

---

## 🚀 Step 4: Deploy Frontend

### Option A: Deploy to Render (Static Site)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Static Site"**
3. Connect your frontend repository
4. Configure:
   - **Name**: `rubiks-cube-frontend`
   - **Build Command**: *(leave empty)*
   - **Publish Directory**: `.`
5. Click **"Create Static Site"**

### Option B: Deploy to GitHub Pages

```bash
# In your frontend repository
git add .
git commit -m "Connect to deployed backend"
git push origin main
```

Then enable GitHub Pages in repository settings.

### Option C: Deploy to Netlify

1. Go to https://app.netlify.com
2. Drag and drop your frontend folder
3. Done!

---

## ✅ Step 5: Test Everything

After deploying frontend, test:

```bash
# Test backend directly
curl https://rubiks-cube-backend.onrender.com/api/health

# Test frontend
# Open your frontend URL in browser
# Check browser console for errors
# Test cube detection and solving
```

---

## 🐛 Troubleshooting

### Issue: CORS Errors

**Symptom:** "Access to fetch has been blocked by CORS policy"

**Solution:** Your backend already has CORS enabled. If you still see errors:

1. Check the backend URL is correct in `config.js`
2. Verify backend is running: `curl https://YOUR-URL.onrender.com/api/health`
3. Check browser console for the exact error

### Issue: 404 Errors

**Symptom:** API endpoints return 404

**Solution:**
1. Verify backend URL in config.js
2. Check endpoint paths start with `/api/`
3. Test backend directly with curl

### Issue: Backend Sleeps

**Symptom:** First request takes 30-60 seconds

**Solution:** This is normal for Render's free tier. The backend wakes up on first request.

---

## 📋 Quick Checklist

- [ ] Get backend URL from Render
- [ ] Update `scripts/config.js` with backend URL
- [ ] Search for hardcoded `localhost:5000` URLs
- [ ] Replace hardcoded URLs with `CONFIG.API_BASE_URL`
- [ ] Test locally (python -m http.server 8000)
- [ ] Commit changes to Git
- [ ] Deploy frontend
- [ ] Test deployed frontend
- [ ] Verify API calls work

---

## 🎯 Example: Complete config.js

```javascript
/**
 * Application Configuration
 */

// Detect environment
const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';

// Set API base URL based on environment
const API_BASE_URL = isDevelopment 
    ? 'http://localhost:5000'
    : 'https://rubiks-cube-backend.onrender.com';  // ← YOUR URL HERE

export const CONFIG = {
    /**
     * Backend API Base URL
     */
    API_BASE_URL: API_BASE_URL,
    
    /**
     * API Endpoints
     */
    API_ENDPOINTS: {
        COLOR_MAPPINGS: '/api/color-mappings',
        VALIDATE_CUBE: '/api/validate-cube',
        DETECT_COLORS: '/api/detect-colors',
        DETECT_COLORS_FAST: '/api/detect-colors-fast',
        SOLVE_CUBE: '/api/solve-cube'
    },
    
    /**
     * Camera Settings
     */
    CAMERA: {
        WIDTH: 640,
        HEIGHT: 480,
        FACING_MODE: 'environment'
    },
    
    /**
     * Cube Colors
     */
    COLORS: {
        White: '#FFFFFF',
        Red: '#FF0000',
        Green: '#00FF00',
        Yellow: '#FFFF00',
        Orange: '#FF8800',
        Blue: '#0000FF'
    }
};

console.log(`🚀 Running in ${isDevelopment ? 'DEVELOPMENT' : 'PRODUCTION'} mode`);
console.log(`📡 API Base URL: ${API_BASE_URL}`);
```

---

## 🎉 You're Almost Done!

1. Update your frontend config
2. Deploy frontend
3. Test everything
4. Enjoy your deployed Rubik's Cube app! 🎊

---

**Need help?** Check the browser console for errors and verify your backend URL is correct.
