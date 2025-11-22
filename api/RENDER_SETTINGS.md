# 🎯 Render Deployment Settings

Copy these exact settings when creating your Web Service on Render.

---

## 📋 Basic Settings

| Setting | Value |
|---------|-------|
| **Service Name** | `rubiks-cube-backend` |
| **Environment** | `Python 3` |
| **Region** | `Oregon (US West)` or closest to you |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |

---

## 🔨 Build & Deploy Settings

### Build Command
```
pip install -r requirements.txt
```

### Start Command
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app
```

---

## 💰 Instance Type

| Setting | Value |
|---------|-------|
| **Instance Type** | `Free` |
| **Auto-Deploy** | `Yes` (recommended) |

---

## 🌍 Environment Variables (Optional)

*No environment variables required for basic setup.*

If you need to add custom backend path later:

| Key | Value |
|-----|-------|
| `BACKEND_PATH` | `/opt/render/project/src` |

---

## 🔗 URLs After Deployment

Your backend will be available at:

```
https://rubiks-cube-backend.onrender.com
```

Or with your custom name:

```
https://YOUR-SERVICE-NAME.onrender.com
```

---

## 📝 Copy-Paste Checklist

When creating the Web Service, copy these values:

**Name:**
```
rubiks-cube-backend
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app
```

---

## 🧪 Test Endpoints After Deployment

Replace `YOUR-URL` with your actual Render URL:

```bash
# Health check
curl https://YOUR-URL.onrender.com/api/health

# Test endpoint
curl https://YOUR-URL.onrender.com/api/test

# Color mappings
curl https://YOUR-URL.onrender.com/api/color-mappings

# Camera status
curl https://YOUR-URL.onrender.com/api/camera-status
```

---

## 🎨 Frontend Configuration

After deployment, update your frontend's `scripts/config.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://rubiks-cube-backend.onrender.com';  // ← Your Render URL here

export const CONFIG = {
    API_BASE_URL: API_BASE_URL,
    
    API_ENDPOINTS: {
        COLOR_MAPPINGS: '/api/color-mappings',
        VALIDATE_CUBE: '/api/validate-cube',
        DETECT_COLORS: '/api/detect-colors',
        DETECT_COLORS_FAST: '/api/detect-colors-fast',
        SOLVE_CUBE: '/api/solve-cube'
    }
};
```

---

## ⚙️ Advanced Settings (Optional)

### Health Check Path
```
/api/health
```

### Auto-Deploy
- ✅ **Enabled** - Automatically deploy when you push to GitHub

### Pull Request Previews
- ⬜ **Disabled** - Not needed for free tier

---

## 📊 Expected Performance

| Metric | Value |
|--------|-------|
| **Build Time** | 5-10 minutes (first time) |
| **Cold Start** | 30-60 seconds (free tier) |
| **Warm Response** | < 1 second |
| **Sleep After** | 15 minutes inactivity (free tier) |

---

## 🔄 Keep Backend Awake (Optional)

Free tier sleeps after 15 minutes. To keep it awake:

1. Go to https://uptimerobot.com
2. Create free account
3. Add monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://YOUR-URL.onrender.com/api/health`
   - **Interval**: 5 minutes

---

## 🎯 Quick Copy Section

**For Render Dashboard:**

```
Name: rubiks-cube-backend
Environment: Python 3
Build: pip install -r requirements.txt
Start: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app
```

**For Frontend Config:**

```javascript
'https://rubiks-cube-backend.onrender.com'
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Build completed successfully (check logs)
- [ ] Service shows "Live" status
- [ ] Health endpoint responds: `/api/health`
- [ ] Test endpoint works: `/api/test`
- [ ] Frontend can connect to backend
- [ ] CORS working (no errors in browser console)

---

**That's it!** These are all the settings you need. 🚀
