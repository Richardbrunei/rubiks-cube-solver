# Prepare Backend for Render - Complete Guide

Complete guide for deploying your Rubik's Cube backend to Render.

**Your backend is in a separate repository from this frontend.**

---

## Table of Contents

1. [Prepare Your Backend Repository](#step-1-prepare-your-backend-repository)
2. [Deploy Backend to Render](#step-2-deploy-backend-to-render)
3. [Connect Frontend to Backend](#connect-frontend-to-backend)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)

---

## Step 1: Prepare Your Backend Repository

Navigate to your backend repository:
```bash
cd /path/to/your/backend/repo
```

### 1.1 Create `Procfile`

Create a file named `Procfile` (no extension) in the root:

```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
```

**Note**: Replace `app:app` with your actual file and app name:
- If your main file is `backend_api.py` with `app = Flask(__name__)`, use: `backend_api:app`
- If your main file is `main.py` with `app = Flask(__name__)`, use: `main:app`
- Format is: `filename:variable_name`

### 1.2 Create `runtime.txt`

Create a file named `runtime.txt`:

```
python-3.9.18
```

### 1.3 Create/Update `requirements.txt`

Ensure your `requirements.txt` includes these essential packages:

```
# Web framework
flask>=2.0.0
flask-cors>=3.0.0
gunicorn>=20.1.0

# Computer vision (headless version for servers)
opencv-python-headless>=4.5.0
numpy>=1.21.0

# Cube solving
kociemba>=1.2.0

# Image processing
pillow>=8.0.0

# Optional
requests>=2.25.0
```

**Important**: Use `opencv-python-headless` (not `opencv-python`) for server deployment.

### 1.4 Enable CORS in Your Backend

Your backend MUST enable CORS to allow the frontend to make API calls.

**Update your main backend file** (e.g., `backend_api.py`, `app.py`, or `main.py`):

```python
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8000",  # Local development
            "https://*.onrender.com",  # All Render domains
            "*"  # Or allow all origins
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Your routes here
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

# ... rest of your code
```

### 1.5 Verify File Structure

Your backend repository should have:

```
your-backend-repo/
├── Procfile                    ← Start command
├── runtime.txt                 ← Python version
├── requirements.txt            ← Dependencies
├── backend_api.py (or app.py)  ← Main Flask app
├── config.py                   ← Configuration (if you have it)
├── camera_interface.py         ← Camera functions (if you have it)
└── ... other backend files
```

### 1.6 Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Test with Flask development server
python backend_api.py

# Test with gunicorn (production mode)
gunicorn --bind 0.0.0.0:5000 backend_api:app
```

Visit http://localhost:5000/api/health to verify it works.

## Step 2: Deploy Backend to Render

### 2.1 Push to GitHub

```bash
git add .
git commit -m "Prepare backend for Render deployment"
git push origin main
```

### 2.2 Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect GitHub"** (authorize if needed)
4. Select your **backend repository**
5. Click **"Connect"**

### 2.3 Configure Service

| Setting | Value |
|---------|-------|
| **Name** | `rubiks-cube-backend` |
| **Environment** | `Python 3` |
| **Branch** | `main` |
| **Root Directory** | (leave blank) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app` |
| **Instance Type** | `Free` |

**Important**: Adjust the start command if your file isn't `backend_api.py`.

6. Click **"Create Web Service"**

### 2.4 Wait for Deployment

- Build takes 5-10 minutes (OpenCV installation is slow)
- Watch the logs for: `Your service is live 🎉`
- Note your backend URL: `https://rubiks-cube-backend.onrender.com`

### 2.5 Test Backend

```bash
# Health check
curl https://rubiks-cube-backend.onrender.com/api/health

# Test endpoint (if you have it)
curl https://rubiks-cube-backend.onrender.com/api/test

# Color mappings (if you have it)
curl https://rubiks-cube-backend.onrender.com/api/color-mappings
```



# Connect Frontend to Backend

## Update Frontend Configuration

Your frontend already has a centralized config in `scripts/config.js`.

### Option 1: Environment-Based Configuration (Recommended)

Update `scripts/config.js`:

```javascript
/**
 * Application Configuration
 */

// Detect environment
const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';

// Set API base URL based on environment
const API_BASE_URL = isDevelopment 
    ? 'http://localhost:5000'  // Local backend
    : 'https://rubiks-cube-backend.onrender.com';  // Production backend

export const CONFIG = {
    /**
     * Backend API Base URL
     * Automatically switches between local and production
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
    
    // ... rest of your config
};

// ... rest of your code
```

### Option 2: Manual Configuration

Simply update the `API_BASE_URL` in `scripts/config.js`:

```javascript
export const CONFIG = {
    // Change this to your backend URL
    API_BASE_URL: 'https://rubiks-cube-backend.onrender.com',
    
    // ... rest of config
};
```

### Fix Hardcoded URL in solve-button.js

Update `scripts/solve-button.js` line 114:

**Before:**
```javascript
const response = await fetch('http://localhost:5000/api/solve-cube', {
```

**After:**
```javascript
import { CONFIG } from './config.js';

// ... in your code
const response = await fetch(`${CONFIG.API_BASE_URL}/api/solve-cube`, {
```

## Deploy Frontend

### Option A: Static Site (Recommended)

1. **Push to GitHub**:
```bash
git add .
git commit -m "Configure frontend for production backend"
git push origin main
```

2. **Deploy on Render**:
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Static Site"**
   - Connect your repository
   - Configure:
     - **Name**: `rubiks-cube-frontend`
     - **Build Command**: (leave empty)
     - **Publish Directory**: `.`
   - Click **"Create Static Site"**

3. **Your frontend URL**: `https://rubiks-cube-frontend.onrender.com`



---

# Testing

## Test Backend

```bash
# Health check
curl https://rubiks-cube-backend.onrender.com/api/health

# Expected response:
# {"status":"healthy","message":"Rubik's Cube Color Detection API is running"}
```

## Test Frontend

1. Open: `https://rubiks-cube-frontend.onrender.com` (or your frontend URL)
2. Open browser console (F12)
3. Check for errors
4. Test cube functionality

## Test CORS

Run in browser console on your frontend:

```javascript
fetch('https://rubiks-cube-backend.onrender.com/api/health')
    .then(r => r.json())
    .then(data => console.log('✅ CORS working:', data))
    .catch(err => console.error('❌ CORS error:', err));
```

## Test API Integration

```javascript
// Test color mappings
fetch('https://rubiks-cube-backend.onrender.com/api/color-mappings')
    .then(r => r.json())
    .then(data => console.log('Color mappings:', data));
```

---

# Troubleshooting

## Issue: CORS Errors

**Symptom**: "Access to fetch has been blocked by CORS policy"

**Fix**: Update backend CORS configuration:

```python
from flask_cors import CORS

# Allow all origins (for testing)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Or allow specific domains (for production)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://rubiks-cube-frontend.onrender.com",
            "http://localhost:8000"
        ]
    }
})
```

## Issue: Backend Build Fails

**Symptom**: "Error installing opencv-python"

**Fix**: Use `opencv-python-headless` in requirements.txt:
```
opencv-python-headless>=4.5.0
```

## Issue: Backend Returns 404

**Symptom**: API endpoints return 404

**Fix**: 
1. Check your routes start with `/api/`
2. Verify backend is running: `curl https://your-backend.onrender.com/api/health`
3. Check logs in Render Dashboard

## Issue: Frontend Can't Connect to Backend

**Symptom**: Network errors in browser console

**Fix**:
1. Verify backend URL in `scripts/config.js`
2. Check backend is deployed and running
3. Test backend directly: `curl https://your-backend.onrender.com/api/health`
4. Check CORS is enabled

## Issue: Backend Sleeps (Free Tier)

**Symptom**: First request takes 30-60 seconds

**Fix**: 
1. Use UptimeRobot to ping every 5 minutes: https://uptimerobot.com
2. Or upgrade to paid tier ($7/month)

## Issue: "gunicorn: command not found"

**Symptom**: Build fails with gunicorn error

**Fix**: Add to requirements.txt:
```
gunicorn>=20.1.0
```

---

# File Checklist

## Backend Repository (Separate)

- [ ] `Procfile` - Contains gunicorn start command
- [ ] `runtime.txt` - Contains `python-3.9.18`
- [ ] `requirements.txt` - Includes flask, flask-cors, gunicorn, opencv-python-headless
- [ ] CORS enabled in Flask app
- [ ] All backend files committed
- [ ] Pushed to GitHub
- [ ] Deployed to Render
- [ ] Backend URL noted: `https://rubiks-cube-backend.onrender.com`

## Frontend Repository (This One)

- [ ] `scripts/config.js` - Updated with backend URL
- [ ] `scripts/solve-button.js` - Fixed hardcoded URL
- [ ] Tested locally with backend
- [ ] All changes committed
- [ ] Pushed to GitHub
- [ ] Deployed to Render (if separate)
- [ ] Frontend URL noted: `https://rubiks-cube-frontend.onrender.com`

---

# Quick Reference

## Backend Repository Files

**Procfile**:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app
```

**runtime.txt**:
```
python-3.9.18
```

**requirements.txt** (minimum):
```
flask>=2.0.0
flask-cors>=3.0.0
gunicorn>=20.1.0
opencv-python-headless>=4.5.0
numpy>=1.21.0
kociemba>=1.2.0
```

**CORS Configuration**:
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## Frontend Configuration

**scripts/config.js**:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://rubiks-cube-backend.onrender.com';

export const CONFIG = {
    API_BASE_URL: API_BASE_URL,
    // ... rest of config
};
```

## Test Commands

```bash
# Test backend locally
cd /path/to/backend
python app.py

# Test with gunicorn
gunicorn --bind 0.0.0.0:5000 backend_api:app

# Test deployed backend
curl https://rubiks-cube-backend.onrender.com/api/health

# Test frontend locally
python -m http.server 8000
```

## Deployment URLs

After deployment:

- **Backend**: `https://rubiks-cube-backend.onrender.com`
- **Frontend**: `https://rubiks-cube-frontend.onrender.com`
- **API Endpoints**: `https://rubiks-cube-backend.onrender.com/api/*`

---

# Summary

## Deployment Steps:

1. ✅ Create `Procfile`, `runtime.txt`, `requirements.txt` in backend repo
2. ✅ Enable CORS in Flask app
3. ✅ Push backend to GitHub
4. ✅ Deploy backend to Render as Web Service
5. ✅ Update frontend `scripts/config.js` with backend URL
6. ✅ Deploy frontend as Static Site
7. ✅ Test everything
8. 🎉 Done!

---

**Your backend is ready for Render deployment!** 🚀

Follow the steps above and both frontend and backend will be live in about 15 minutes.
