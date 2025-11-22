# 🚀 Quick Reference - Render Deployment

## One-Command Test

```bash
cd api && python test_local.py
```

## One-Command Deploy (After GitHub Setup)

```bash
cd api && git add . && git commit -m "Deploy to Render" && git push
```

## Render Configuration (Copy-Paste Ready)

| Setting | Value |
|---------|-------|
| Name | `rubiks-cube-backend` |
| Environment | `Python 3` |
| Branch | `main` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app` |

## Test Commands

```bash
# Local test
curl http://localhost:5000/api/health

# Production test (replace URL)
curl https://rubiks-cube-backend.onrender.com/api/health
```

## Frontend Config Update

```javascript
// scripts/config.js
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:5000'
    : 'https://rubiks-cube-backend.onrender.com';
```

## Files Checklist

- ✅ Procfile
- ✅ runtime.txt
- ✅ requirements.txt
- ✅ .gitignore
- ✅ backend_api.py (CORS enabled)

## Deployment Steps

1. **Test**: `python test_local.py`
2. **Push**: `git push origin main`
3. **Deploy**: Create Web Service on Render
4. **Test**: `curl https://YOUR-URL.onrender.com/api/health`
5. **Update**: Frontend config.js

## Expected Timeline

- Build: 5-10 minutes
- First request: 30-60 seconds (free tier)
- Normal requests: < 1 second

---

**Full Guide**: See DEPLOYMENT.md
**Setup Details**: See SETUP_COMPLETE.md
