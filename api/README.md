# Rubik's Cube API Backend

This folder contains the Python backend API for camera integration and cube state management.

## 📁 Files Overview

### Core API Files
- **`start_backend.py`** - Main backend server startup script
- **`backend_api.py`** - Flask API endpoints and routes
- **`back_end_main.py`** - Core backend functionality

### Camera Integration
- **`web_integrated_camera.py`** - Camera capture integration for web interface
- **`camera_interface_template.py`** - Template for camera interface implementation

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Start the Backend Server**
   ```bash
   python start_backend.py
   ```

3. **API Endpoints**
   - `GET /api/camera-status` - Check camera availability
   - `POST /api/detect-colors` - **NEW** Detect colors from captured image
   - `POST /api/validate-cube` - Validate cube state
   - `POST /api/solve-cube` - **NEW** Generate solving instructions using Kociemba algorithm
   - `GET /api/color-mappings` - Get color notation mappings
   - ~~`POST /api/launch-integrated-camera`~~ - **DEPRECATED** (use frontend camera capture)
   - ~~`GET /web_output/status.json`~~ - **DEPRECATED** (no longer used)
   - ~~`GET /web_output/cube_state.json`~~ - **DEPRECATED** (no longer used)

## 🔧 Configuration

The backend server runs on `localhost:5000` by default. CORS is enabled for web interface integration.

## 📋 Dependencies

- **Flask** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **OpenCV** - Computer vision and camera access
- **NumPy** - Numerical computations for color detection
- **Kociemba** - Rubik's cube solving algorithm

## 🎯 Camera Capture Workflow (NEW)

1. User clicks camera button in web interface
2. Browser opens camera preview with visual guide
3. User positions cube face and clicks capture
4. Frontend sends image to `/api/detect-colors` endpoint
5. Backend processes image and returns detected colors
6. Frontend immediately updates cube visualization

### Legacy Workflow (DEPRECATED)
The old workflow that launched an external camera program and wrote to `web_output/` files is deprecated and no longer supported.

## 🔍 API Response Format

### POST /api/detect-colors (NEW)

**Request:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "face": "front"
}
```

**Success Response:**
```json
{
  "success": true,
  "colors": ["White", "Red", "Green", "Yellow", "Orange", "Blue", "White", "Red", "Green"],
  "cube_notation": ["U", "R", "F", "D", "L", "B", "U", "R", "F"],
  "face": "front",
  "confidence": [0.95, 0.92, 0.88, 0.91, 0.89, 0.93, 0.96, 0.90, 0.87],
  "message": "Colors detected successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to decode image"
}
```

### Image Preprocessing Pipeline

The `/api/detect-colors` endpoint applies the following preprocessing steps to match the backend camera interface:

1. **Horizontal Mirror** - Flips image for natural interaction
2. **Square Crop** - Crops to square aspect ratio (centered)
3. **Resize** - Resizes to 600x600 pixels
4. **White Balance** - Corrects color casts
5. **Brightness Enhancement** - Adaptive brightness adjustment

### Color Detection Grid

The endpoint extracts colors from a 3x3 grid with these specifications:
- **Grid Size**: 300x300 pixels (centered in 600x600 frame)
- **Grid Position**: (200, 200) to (500, 500)
- **Detection Areas**: 9 squares of 40x40 pixels each
- **Grid Spacing**: 100 pixels between centers

### Camera Status Response
```json
{
  "camera_available": true,
  "backend_available": true,
  "status": "ready"
}
```

### Cube Validation Response
```json
{
  "success": true,
  "is_valid": true,
  "message": "Cube state is valid",
  "warnings": []
}
```

### POST /api/solve-cube (NEW)

**Request:**
```json
{
  "cubestring": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBBBB"
}
```

**Success Response:**
```json
{
  "success": true,
  "solution": "R U R' U' R' F R2 U' R' U' R U R' F'",
  "move_count": 14,
  "message": "Solution found successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid cube state",
  "details": "There is not exactly one facelet of each colour"
}
```

**Cube Notation:**
- **Moves**: R (Right), L (Left), U (Up), D (Down), F (Front), B (Back)
- **Modifiers**: ' (counter-clockwise), 2 (180° turn)
- **Example**: `R U R' U'` means Right clockwise, Up clockwise, Right counter-clockwise, Up counter-clockwise

For detailed documentation, see `../docs/SOLVE-BUTTON-GUIDE.md`

## 🛠️ Development

For development and testing, see the files in the `../tests/` directory.

## 🔒 Security Notes

- Backend only accepts connections from localhost
- No sensitive data is stored or transmitted
- Camera access requires user permission