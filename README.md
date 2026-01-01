# Rubik's Cube Color Detection System

A complete computer vision-based Rubik's cube color detection, validation, and solving system with both CLI and web interfaces.

## Features

### Desktop Application
- **Live Camera Preview**: Real-time mirrored display with 3x3 alignment grid
- **Advanced Color Detection**: HSV-based color detection with automatic low-light fallback
- **White Balance Correction**: Automatic correction for camera color casts
- **Interactive Color Editing**: Manual correction capabilities for detected colors
- **Cube Validation**: Validates cube state according to Rubik's cube rules
- **Auto-Correction**: Intelligent face reordering and rotation fixing
- **Cube Solving**: Integration with Kociemba algorithm for optimal solutions

### Web API & Interface
- **RESTful API**: Flask-based backend with CORS support
- **Image Upload**: Browser-based camera capture with instant color detection
- **Real-time Processing**: Fast color detection endpoint for live preview
- **Cube Solver**: Web-accessible solving with move-by-move instructions
- **Production Ready**: Deployable to Render with Gunicorn

## Requirements

- Python 3.9+
- OpenCV (headless for servers)
- NumPy
- Flask & Flask-CORS
- Kociemba (cube solving algorithm)
- Pillow (image processing)

## Installation

### Desktop Application

1. Clone this repository:
```bash
git clone <repository-url>
cd rubiks-cube-detector
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the desktop application:
```bash
python rubiks_cube_color_detector.py
```

### Web API

1. Navigate to the API directory:
```bash
cd api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python backend_api.py
```

The API will be available at `http://localhost:5000`

## Usage

### Desktop Application

Run the main script:
```bash
python rubiks_cube_color_detector.py
```

**Controls:**
- **SPACE**: Capture current face
- **ESC**: Exit program
- Follow on-screen instructions for each cube face

**Capture Order:**
1. White (Up) → 2. Red (Right) → 3. Green (Front)
4. Yellow (Down) → 5. Orange (Left) → 6. Blue (Back)

### Web API Endpoints

#### Health Check
```bash
GET /api/health
```

#### Detect Colors from Image
```bash
POST /api/detect-colors
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,...",
  "face": "front"
}
```

#### Solve Cube
```bash
POST /api/solve-cube
Content-Type: application/json

{
  "cubestring": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
}
```

#### Validate Cube State
```bash
POST /api/validate-cube
Content-Type: application/json

{
  "cube_state": ["White", "Red", "Green", ...],
  "cube_string": "UUUUUUUUU..."
}
```

See `api/README.md` for complete API documentation.

## Project Structure

```
├── rubiks_cube_color_detector.py  # Main desktop application
├── config.py                      # Configuration and constants
├── color_detection.py             # Color detection algorithms
├── image_processing.py            # Image enhancement utilities
├── camera_interface.py            # Camera and user interface
├── cube_validation.py             # Cube validation and fixing
├── cube_display.py                # Display and printing functions
├── requirements.txt               # Python dependencies
├── Procfile                       # Deployment configuration
├── runtime.txt                    # Python version for deployment
├── api/
│   ├── backend_api.py            # Flask API server
│   ├── requirements.txt          # API dependencies
│   ├── README.md                 # API documentation
│   ├── DEPLOYMENT.md             # Deployment guide
│   └── RENDER_SETTINGS.md        # Render configuration
└── README.md                      # This file
```

## How It Works

### Color Detection Pipeline

1. **Image Preprocessing**
   - Horizontal mirror for natural interaction
   - Square crop and resize to 600x600
   - White balance correction
   - Adaptive brightness enhancement

2. **Color Detection**
   - HSV-based color range matching
   - Automatic low-light fallback (V < 80)
   - KMeans clustering for accurate detection
   - Fast mode for live preview

3. **Validation & Fixing**
   - Center piece validation
   - Face reordering by center colors
   - Automatic face rotation correction
   - Edge and corner piece validation

4. **Solving**
   - Kociemba two-phase algorithm
   - Optimal solution (typically 20 moves or less)
   - Standard cube notation (R, U, F, D, L, B)

### Cube Notation

- **Faces**: U (Up/White), R (Right/Red), F (Front/Green), D (Down/Yellow), L (Left/Orange), B (Back/Blue)
- **Moves**: Letter = clockwise 90°, Letter' = counter-clockwise 90°, Letter2 = 180°
- **Example**: `R U R' U'` = Right clockwise, Up clockwise, Right counter-clockwise, Up counter-clockwise

## Deployment

The backend API is ready for deployment to Render or similar platforms.

### Quick Deploy to Render

1. Push to GitHub:
```bash
git add .
git commit -m "Deploy backend"
git push origin main
```

2. Create new Web Service on Render
3. Connect your GitHub repository
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd api && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 backend_api:app`
   - **Environment**: Python 3

See `api/DEPLOYMENT.md` for detailed deployment instructions.

## Configuration

### Camera Settings (config.py)
- **Resolution**: 600x600 pixels
- **Grid**: 3x3 detection grid (100px spacing)
- **Detection Area**: 40x40 pixels per sticker
- **Brightness Adjustment**: +40 (adaptive)

### Color Ranges (HSV)
Optimized HSV ranges for each cube color with fallback BGR values for low-light conditions.

## Troubleshooting

### Desktop Application

**Camera not accessible:**
- Check camera permissions
- Ensure no other application is using the camera
- Try different camera index: `cv2.VideoCapture(1)`

**Poor color detection:**
- Improve lighting conditions
- Use white balance correction
- Manually edit misdetected colors
- Avoid shadows and reflections

### Web API

**CORS errors:**
- CORS is pre-configured for localhost and Render
- Update CORS settings in `backend_api.py` if needed

**Module import errors:**
- Backend uses fallback functions when modules unavailable
- Check logs for which modules loaded successfully

**Render deployment sleeps:**
- Free tier sleeps after 15 minutes inactivity
- First request takes 30-60 seconds to wake
- Use UptimeRobot for keep-alive pings

## Testing

### Test Enhanced Validation
```bash
python test_enhanced_validation.py
```

### Test Local API
```bash
cd api
python test_local.py
```

## Performance

- **Desktop**: 30 FPS live preview with real-time color detection
- **API**: < 500ms per face detection
- **Solving**: < 1 second for optimal solution

## Author

Created by Richard with AI Assistant (Kiro)

## License

This project is provided as-is for educational and personal use.