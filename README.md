# Rubik's Cube Color Detection System

A computer vision-based Rubik's cube color detection and analysis system using OpenCV and Python.

## Features

- **Live Camera Preview**: Real-time mirrored display with 3x3 alignment grid
- **Advanced Color Detection**: HSV-based color detection with fallback methods
- **White Balance Correction**: Automatic correction for camera color casts
- **Interactive Color Editing**: Manual correction capabilities for detected colors
- **Cube Validation**: Validates cube state according to Rubik's cube rules
- **Performance Optimized**: Smooth real-time operation with efficient processing

## Requirements

- Python 3.7+
- OpenCV (`cv2`)
- NumPy
- scikit-learn
- kociemba (for cube solving)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd rubiks-cube-detector
```

2. Install required packages:
```bash
pip install opencv-python numpy scikit-learn kociemba
```

## Usage

Run the main script:
```bash
python rubiks_cube_color_detector.py
```

### Controls
- **SPACE**: Capture current face
- **ESC**: Exit program
- Follow on-screen instructions for each cube face

## How It Works

1. **Color Detection**: Uses HSV color ranges for robust color identification
2. **Face Capture**: Captures all 6 faces of the cube in sequence
3. **Validation**: Checks if the detected cube state is geometrically valid
4. **Auto-correction**: Attempts to fix common detection errors
5. **Manual Editing**: Allows user correction of any misdetected colors

## Cube Face Order

The system captures faces in this order:
1. White (Up)
2. Red (Right) 
3. Green (Front)
4. Yellow (Down)
5. Orange (Left)
6. Blue (Back)

## Author

Created by Richard with AI Assistant (Kiro)