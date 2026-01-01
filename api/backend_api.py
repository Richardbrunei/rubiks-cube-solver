"""
Flask API for Rubik's Cube Color Detection
Provides endpoints for image upload and color detection using CV2
Integrates with your existing backend modules
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import json
import sys
import os

app = Flask(__name__)

# Enable CORS for all routes with explicit configuration
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8000",  # Local development
            "http://127.0.0.1:8000",  # Local development
            "https://*.onrender.com",  # All Render domains
            "*"  # Allow all origins (can be restricted in production)
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure backend path for different environments
# Priority: Environment variable > Local dev path > Production fallback

# Local development path (Windows) - kept for testing
LOCAL_DEV_PATH = r"C:\Users\Liang\OneDrive\Documents\cube_code_backend"

# For Render deployment: Add parent directory to Python path
# This allows importing modules from the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    print(f"[INFO] Added parent directory to path: {parent_dir}")

# Check environment variable first (for Render/production)
BACKEND_PATH = os.environ.get('BACKEND_PATH', LOCAL_DEV_PATH)

# Try to add backend path to Python path
if os.path.exists(BACKEND_PATH):
    sys.path.insert(0, BACKEND_PATH)
    print(f"[SUCCESS] Added backend path: {BACKEND_PATH}")
else:
    # Production mode - try parent directory
    BACKEND_PATH = parent_dir
    print(f"[INFO] Using parent directory as backend path: {BACKEND_PATH}")

# Import backend modules or use fallbacks
try:
    from config import COLOR_TO_CUBE
    print("[SUCCESS] Successfully imported config.py")
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"[INFO] Could not import config.py, using fallback color mappings: {e}")
    # Fallback color mappings for production
    COLOR_TO_CUBE = {
        "White": "U",
        "Red": "R",
        "Green": "F",
        "Yellow": "D",
        "Orange": "L",
        "Blue": "B"
    }
    BACKEND_AVAILABLE = True  # We have fallback, so mark as available
    print("[SUCCESS] Using fallback COLOR_TO_CUBE mappings")

# Import camera interface functions
try:
    from camera_interface import show_live_preview, capture_face, edit_face_colors
    print("[SUCCESS] Successfully imported camera_interface functions")
except ImportError as e:
    print(f"[ERROR] Could not import camera_interface functions: {e}")
    print(f"[ERROR] Camera capture features will not be available")
    show_live_preview = None
    capture_face = None
    edit_face_colors = None

# Import validation functions
try:
    from cube_validation import validate_cube_state, fix_cube_complete
    print("[SUCCESS] Successfully imported cube_validation functions")
except ImportError as e:
    print(f"[ERROR] Could not import cube_validation functions: {e}")
    print(f"[ERROR] Cube validation features will not be available")
    validate_cube_state = None
    fix_cube_complete = None

# Import color detection functions
try:
    from color_detection import detect_color_advanced, get_dominant_color
    print("[SUCCESS] Successfully imported color_detection functions")
except ImportError as e:
    print(f"[ERROR] Could not import color_detection functions: {e}")
    print(f"[ERROR] Color detection features will not be available")
    detect_color_advanced = None
    get_dominant_color = None

# Import image processing functions
try:
    from image_processing import correct_white_balance, adaptive_brighten_image, prepare_frame
    print("[SUCCESS] Successfully imported image_processing functions")
except ImportError as e:
    print(f"[ERROR] Could not import image_processing functions: {e}")
    print(f"[ERROR] Image preprocessing features will not be available")
    correct_white_balance = None
    adaptive_brighten_image = None
    prepare_frame = None



@app.route('/api/detect-colors', methods=['POST'])
def detect_colors():
    """
    API endpoint to detect colors from uploaded image
    
    Expected request format:
    {
        "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
        "face": "front|back|left|right|top|bottom"
    }
    
    Returns:
    {
        "success": true,
        "colors": ["White", "Red", "Green", ...],
        "cube_notation": ["U", "R", "F", ...],
        "face": "front",
        "confidence": [0.95, 0.92, ...],
        "message": "Colors detected successfully"
    }
    """
    if not BACKEND_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Backend modules not available. Please check backend configuration.'
        }), 503

    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        image_data = data.get('image')
        face = data.get('face', 'unknown')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400
        
        # Decode base64 image
        try:
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # Decode to OpenCV image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({
                    'success': False,
                    'error': 'Failed to decode image'
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to decode image: {str(e)}'
            }), 400
        
        # Preprocess frame (matching camera_interface.py specifications)
        try:
            # 1. Mirror horizontally for natural interaction
            frame = cv2.flip(image, 1)
            
            # 2. Use prepare_frame for complete preprocessing pipeline if available
            # This includes: crop to square, resize, white balance, brightness enhancement
            if prepare_frame is not None:
                frame = prepare_frame(frame, target_size=(600, 600), brightness=40)
            else:
                # Fallback to manual preprocessing
                # 2a. Crop to square aspect ratio (centered)
                height, width = frame.shape[:2]
                size = min(height, width)
                x = (width - size) // 2
                y = (height - size) // 2
                frame = frame[y:y+size, x:x+size]
                
                # 2b. Resize to 600x600 (CAMERA_RESOLUTION)
                frame = cv2.resize(frame, (600, 600))
                
                # 2c. Apply white balance correction
                if correct_white_balance is not None:
                    frame = correct_white_balance(frame)
                
                # 2d. Apply adaptive brightness enhancement
                if adaptive_brighten_image is not None:
                    frame = adaptive_brighten_image(frame, 40)  # BRIGHTNESS_ADJUSTMENT = 40
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Image preprocessing failed: {str(e)}'
            }), 500
        
        # Extract colors from 3x3 grid (matching camera_interface.py)
        try:
            colors = []
            confidence_scores = []
            
            # Grid specifications (matching backend)
            GRID_START = 200
            GRID_STEP = 100
            DETECTION_SIZE = 20
            
            # Extract 9 detection patches from grid positions
            for row in range(3):
                for col in range(3):
                    # Calculate center position
                    center_x = GRID_START + 50 + (col * GRID_STEP)  # 250, 350, 450
                    center_y = GRID_START + 50 + (row * GRID_STEP)  # 250, 350, 450
                    
                    # Extract 40x40 patch (DETECTION_SIZE * 2)
                    x1 = center_x - DETECTION_SIZE
                    y1 = center_y - DETECTION_SIZE
                    x2 = center_x + DETECTION_SIZE
                    y2 = center_y + DETECTION_SIZE
                    patch = frame[y1:y2, x1:x2]
                    
                    # Detect color using advanced detection
                    # Note: detect_color_advanced() automatically uses detect_color_low_brightness()
                    # when brightness (V) < 80, providing better detection in low light conditions
                    color = detect_color_advanced(patch, use_fast=False)
                    colors.append(color)
                    
                    # Calculate confidence (simple metric based on color consistency)
                    confidence = calculate_color_confidence(patch, color)
                    confidence_scores.append(confidence)
            
            # Unmirror color order (compensate for horizontal flip)
            colors = unmirror_colors(colors)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Color detection failed: {str(e)}'
            }), 500
        
        # Convert to cube notation
        cube_notation = [COLOR_TO_CUBE.get(color, "X") for color in colors]
        
        # Check for detection failures
        if "X" in cube_notation or "Unknown" in colors:
            return jsonify({
                'success': False,
                'error': 'Some colors could not be detected',
                'colors': colors,
                'cube_notation': cube_notation,
                'face': face,
                'confidence': confidence_scores
            }), 422
        
        return jsonify({
            'success': True,
            'colors': colors,
            'cube_notation': cube_notation,
            'face': face,
            'confidence': confidence_scores,
            'message': 'Colors detected successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/detect-colors-fast', methods=['POST'])
def detect_colors_fast():
    """
    Fast color detection endpoint for live preview
    Uses detect_color_advanced with use_fast=True for better performance
    
    Expected request format:
    {
        "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
        "face": "front|back|left|right|top|bottom"
    }
    
    Returns:
    {
        "success": true,
        "colors": ["White", "Red", "Green", ...],
        "cube_notation": ["U", "R", "F", ...],
        "face": "front"
    }
    """
    if not BACKEND_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Backend modules not available'
        }), 503

    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        image_data = data.get('image')
        face = data.get('face', 'unknown')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400
        
        # Decode base64 image
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return jsonify({
                    'success': False,
                    'error': 'Failed to decode image'
                }), 400
                
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Failed to decode image: {str(e)}'
            }), 400
        
        # Preprocess frame (same as detect-colors but optimized for speed)
        try:
            frame = cv2.flip(image, 1)
            
            if prepare_frame is not None:
                frame = prepare_frame(frame, target_size=(600, 600), brightness=40)
            else:
                height, width = frame.shape[:2]
                size = min(height, width)
                x = (width - size) // 2
                y = (height - size) // 2
                frame = frame[y:y+size, x:x+size]
                frame = cv2.resize(frame, (600, 600))
                
                if correct_white_balance is not None:
                    frame = correct_white_balance(frame)
                if adaptive_brighten_image is not None:
                    frame = adaptive_brighten_image(frame, 40)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Image preprocessing failed: {str(e)}'
            }), 500
        
        # Extract colors using FAST detection for live preview
        try:
            colors = []
            
            GRID_START = 200
            GRID_STEP = 100
            DETECTION_SIZE = 20
            
            for row in range(3):
                for col in range(3):
                    center_x = GRID_START + 50 + (col * GRID_STEP)
                    center_y = GRID_START + 50 + (row * GRID_STEP)
                    
                    x1 = center_x - DETECTION_SIZE
                    y1 = center_y - DETECTION_SIZE
                    x2 = center_x + DETECTION_SIZE
                    y2 = center_y + DETECTION_SIZE
                    patch = frame[y1:y2, x1:x2]
                    
                    # Use FAST detection (use_fast=True) for live preview performance
                    # This uses simple averaging instead of KMeans clustering
                    color = detect_color_advanced(patch, use_fast=True)
                    colors.append(color)
            
            # Unmirror color order
            colors = unmirror_colors(colors)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Color detection failed: {str(e)}'
            }), 500
        
        # Convert to cube notation
        cube_notation = [COLOR_TO_CUBE.get(color, "X") for color in colors]
        
        return jsonify({
            'success': True,
            'colors': colors,
            'cube_notation': cube_notation,
            'face': face
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Rubik\'s Cube Color Detection API is running'
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    if not BACKEND_AVAILABLE or COLOR_TO_CUBE is None:
        return jsonify({
            'success': False,
            'message': 'Backend modules not available',
            'backend_available': BACKEND_AVAILABLE
        }), 503
    
    return jsonify({
        'success': True,
        'message': 'API is working correctly',
        'backend_available': BACKEND_AVAILABLE,
        'supported_colors': list(COLOR_TO_CUBE.keys()),
        'cube_notation': list(COLOR_TO_CUBE.values())
    })

@app.route('/api/color-mappings', methods=['GET'])
def get_color_mappings():
    """Get color mappings from backend config"""
    if not BACKEND_AVAILABLE or COLOR_TO_CUBE is None:
        return jsonify({
            'success': False,
            'error': 'Backend modules not available. Cannot retrieve color mappings.'
        }), 503
    
    # Create inverse mapping
    cube_to_color = {v: k for k, v in COLOR_TO_CUBE.items()}
    
    return jsonify({
        'success': True,
        'color_to_cube': COLOR_TO_CUBE,
        'cube_to_color': cube_to_color
    })

@app.route('/api/launch-camera', methods=['POST'])
def launch_camera():
    """Launch the existing camera program"""
    if not BACKEND_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Backend modules not available. Cannot launch camera program.'
        }), 503
    
    try:
        import subprocess
        import threading
        
        # Determine working directory - use BACKEND_PATH if available, otherwise current dir
        working_dir = BACKEND_PATH if BACKEND_PATH and os.path.exists(BACKEND_PATH) else '.'
        
        def run_camera():
            # Launch your existing camera program
            subprocess.run([sys.executable, 'back_end_main.py'], cwd=working_dir)
        
        # Run in background thread so API doesn't block
        thread = threading.Thread(target=run_camera)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Camera program launched successfully',
            'working_dir': working_dir
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to launch camera program: {str(e)}'
        }), 500

@app.route('/api/launch-integrated-camera', methods=['POST'])
def launch_integrated_camera():
    """
    DEPRECATED: Start the integrated camera capture process
    
    This endpoint is deprecated in favor of frontend-controlled camera capture.
    The new workflow uses the browser's camera API and sends images to /api/detect-colors.
    
    This endpoint is kept for backward compatibility but will be removed in a future version.
    """
    return jsonify({
        'success': False,
        'error': 'This endpoint is deprecated. Please use frontend camera capture with /api/detect-colors instead.',
        'deprecated': True,
        'alternative': '/api/detect-colors'
    }), 410  # 410 Gone - indicates deprecated endpoint

# DEPRECATED: Legacy integrated camera capture function
# This function is no longer used with the new frontend-controlled camera workflow.
# Kept for reference only - will be removed in a future version.
#
# def integrated_camera_capture():
#     """
#     DEPRECATED: Integrated camera capture using backend functions
#     
#     This function launched an external camera program that captured all 6 faces
#     and wrote results to web_output/ directory. The new workflow uses frontend
#     camera capture with the /api/detect-colors endpoint instead.
#     """
#     pass

# DEPRECATED: Legacy web integration helper functions
# These functions were used by the old integrated_camera_capture workflow
# that wrote results to web_output/ directory for polling by CubeImporter.
# The new workflow uses direct API responses instead.
# Kept for backward compatibility only - will be removed in a future version.

WEB_OUTPUT_DIR = "web_output"
CUBE_STATE_FILE = os.path.join(WEB_OUTPUT_DIR, "cube_state.json")
STATUS_FILE = os.path.join(WEB_OUTPUT_DIR, "status.json")

# Helper functions for color detection API

def unmirror_colors(colors):
    """
    Unmirror the color order to compensate for horizontal flip
    The frame is mirrored for natural interaction, so we need to unmirror the detected colors
    
    Args:
        colors: list of 9 colors in mirrored order
    
    Returns:
        list: 9 colors in correct (unmirrored) order
    """
    if len(colors) != 9:
        return colors
    
    # Unmirror by reversing each row
    unmirrored = []
    for row in range(3):
        start = row * 3
        end = start + 3
        row_colors = colors[start:end]
        unmirrored.extend(reversed(row_colors))
    
    return unmirrored

def calculate_color_confidence(patch, detected_color):
    """
    Calculate confidence score for detected color based on color consistency
    
    Args:
        patch: numpy array of the image patch
        detected_color: string name of detected color
    
    Returns:
        float: confidence score between 0 and 1
    """
    try:
        # Convert to HSV for analysis
        hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
        
        # Calculate standard deviation of hue (lower = more consistent)
        h_std = np.std(hsv[:, :, 0])
        
        # Calculate standard deviation of saturation
        s_std = np.std(hsv[:, :, 1])
        
        # Calculate standard deviation of value
        v_std = np.std(hsv[:, :, 2])
        
        # Normalize standard deviations (lower std = higher confidence)
        # HSV ranges: H=0-180, S=0-255, V=0-255
        h_confidence = max(0, 1 - (h_std / 30))  # 30 is threshold for hue variation
        s_confidence = max(0, 1 - (s_std / 50))  # 50 is threshold for saturation variation
        v_confidence = max(0, 1 - (v_std / 50))  # 50 is threshold for value variation
        
        # Weight hue more heavily for color detection
        confidence = (h_confidence * 0.5 + s_confidence * 0.25 + v_confidence * 0.25)
        
        # Boost confidence for white (which has low saturation)
        if detected_color == "White":
            avg_saturation = np.mean(hsv[:, :, 1])
            if avg_saturation < 50:  # Low saturation indicates white
                confidence = max(confidence, 0.85)
        
        return round(confidence, 2)
        
    except Exception as e:
        print(f"Error calculating confidence: {e}")
        return 0.5  # Default medium confidence

# Fallback implementations if backend modules are not available

def fallback_correct_white_balance(image):
    """
    Fallback white balance correction if backend module not available
    Simple gray world algorithm
    """
    result = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result

def fallback_adaptive_brighten_image(image, base_brightness=40):
    """
    Fallback brightness adjustment if backend module not available
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Calculate average brightness
    avg_brightness = np.mean(v)
    
    # Adjust brightness based on current level
    if avg_brightness < 100:
        adjustment = base_brightness + (100 - avg_brightness) * 0.5
    else:
        adjustment = base_brightness * 0.5
    
    # Apply brightness adjustment
    v = cv2.add(v, int(adjustment))
    
    # Merge and convert back
    hsv = cv2.merge([h, s, v])
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return result

def fallback_detect_color_advanced(patch, use_fast=False):
    """
    Fallback color detection if backend module not available
    Simple HSV-based color classification
    """
    # Convert to HSV
    hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
    avg_hsv = np.mean(hsv.reshape(-1, 3), axis=0)
    h, s, v = avg_hsv
    
    # Classify based on HSV values
    # White: High value, low saturation
    if v > 180 and s < 60:
        return "White"
    
    # Yellow: Hue 20-35
    elif 20 <= h <= 35 and s > 80:
        return "Yellow"
    
    # Orange: Hue 10-20
    elif 10 <= h <= 20 and s > 100:
        return "Orange"
    
    # Red: Hue 0-10 or 170-180
    elif (h < 10 or h > 170) and s > 100:
        return "Red"
    
    # Green: Hue 40-80
    elif 40 <= h <= 80 and s > 80:
        return "Green"
    
    # Blue: Hue 90-130
    elif 90 <= h <= 130 and s > 80:
        return "Blue"
    
    else:
        return "Unknown"

# Use backend functions if available, otherwise use fallbacks
if correct_white_balance is None:
    correct_white_balance = fallback_correct_white_balance
    print("[WARNING] Using fallback white balance correction")

if adaptive_brighten_image is None:
    adaptive_brighten_image = fallback_adaptive_brighten_image
    print("[WARNING] Using fallback brightness adjustment")

if detect_color_advanced is None:
    detect_color_advanced = fallback_detect_color_advanced
    print("[WARNING] Using fallback color detection")

# def ensure_output_directory():
#     """DEPRECATED: Create output directory for web integration files"""
#     if not os.path.exists(WEB_OUTPUT_DIR):
#         os.makedirs(WEB_OUTPUT_DIR)

# def update_status(status, message, progress=0):
#     """DEPRECATED: Update status file for web interface"""
#     pass

# def save_cube_state(cube_state, cube_string, is_valid=False):
#     """DEPRECATED: Save cube state to file for web interface"""
#     pass

@app.route('/api/solve-cube', methods=['POST'])
def solve_cube():
    """
    Solve a Rubik's cube using the Kociemba algorithm
    
    Expected request format:
    {
        "cubestring": "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBBBB"
    }
    
    Returns:
    {
        "success": true,
        "solution": "R U R' U' R' F R2 U' R' U' R U R' F'",
        "move_count": 14,
        "message": "Solution found successfully"
    }
    
    Error responses:
    - 400: Invalid cubestring format
    - 422: Impossible cube state
    - 500: Solver error
    - 503: Kociemba library not available
    """
    try:
        # Check if kociemba is available
        try:
            import kociemba
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Kociemba solver not available',
                'details': 'Please install kociemba: pip install kociemba'
            }), 503
        
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        cubestring = data.get('cubestring')
        
        # Validate cubestring presence
        if not cubestring:
            return jsonify({
                'success': False,
                'error': 'Missing cubestring',
                'details': 'Request must include a cubestring field'
            }), 400
        
        # Validate cubestring length
        if len(cubestring) != 54:
            return jsonify({
                'success': False,
                'error': 'Invalid cubestring length',
                'details': f'Cubestring must be exactly 54 characters, got {len(cubestring)}'
            }), 400
        
        # Validate cubestring characters
        valid_chars = set('URFDLB')
        cubestring_chars = set(cubestring)
        if not cubestring_chars.issubset(valid_chars):
            invalid_chars = cubestring_chars - valid_chars
            return jsonify({
                'success': False,
                'error': 'Invalid cubestring characters',
                'details': f'Cubestring must only contain U, R, F, D, L, B. Invalid characters: {", ".join(invalid_chars)}'
            }), 400
        
        # Validate color distribution (each color must appear exactly 9 times)
        color_counts = {}
        for char in cubestring:
            color_counts[char] = color_counts.get(char, 0) + 1
        
        invalid_counts = []
        for color in valid_chars:
            count = color_counts.get(color, 0)
            if count != 9:
                invalid_counts.append(f'{color}: {count}')
        
        if invalid_counts:
            return jsonify({
                'success': False,
                'error': 'Invalid color distribution',
                'details': f'Each color must appear exactly 9 times. Current counts: {", ".join(invalid_counts)}'
            }), 400
        
        # Attempt to solve the cube
        try:
            solution = kociemba.solve(cubestring)
            
            # Count moves in solution
            moves = solution.split() if solution else []
            move_count = len(moves)
            
            # Handle already solved cube
            if not solution or solution.strip() == '':
                return jsonify({
                    'success': True,
                    'solution': '',
                    'move_count': 0,
                    'message': 'Cube is already solved'
                })
            
            return jsonify({
                'success': True,
                'solution': solution,
                'move_count': move_count,
                'message': 'Solution found successfully'
            })
            
        except ValueError as e:
            # Kociemba raises ValueError for impossible cube states
            error_msg = str(e)
            return jsonify({
                'success': False,
                'error': 'Invalid cube state',
                'details': f'This cube configuration cannot be solved: {error_msg}'
            }), 422
            
        except Exception as e:
            # Catch any other kociemba errors
            return jsonify({
                'success': False,
                'error': 'Solver error',
                'details': f'An error occurred while solving: {str(e)}'
            }), 500
        
    except Exception as e:
        # Catch unexpected errors
        return jsonify({
            'success': False,
            'error': 'Unexpected error',
            'details': str(e)
        }), 500

# Configure paths for serving static files
# When running from api/ directory, parent directory contains frontend files
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..')

# Serve static files (HTML, CSS, JS)
@app.route('/')
def serve_index():
    """Serve the main index.html file"""
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/test-interactivity.html')
def serve_test():
    """Serve the test page"""
    return send_from_directory(STATIC_DIR, 'test-interactivity.html')

@app.route('/about.html')
def serve_about():
    """Serve the about page"""
    return send_from_directory(STATIC_DIR, 'about.html')

@app.route('/scripts/<path:filename>')
def serve_scripts(filename):
    """Serve JavaScript files"""
    return send_from_directory(os.path.join(STATIC_DIR, 'scripts'), filename)

@app.route('/styles/<path:filename>')
def serve_styles(filename):
    """Serve CSS files"""
    return send_from_directory(os.path.join(STATIC_DIR, 'styles'), filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve asset files"""
    return send_from_directory(os.path.join(STATIC_DIR, 'assets'), filename)

@app.route('/web_output/<path:filename>')
def serve_web_output(filename):
    """Serve camera program output files"""
    return send_from_directory(os.path.join(STATIC_DIR, 'web_output'), filename)

@app.route('/api/validate-cube', methods=['POST'])
def validate_cube():
    """
    Validate cube state using backend validation functions
    
    Expected request format:
    {
        "cube_state": ["White", "Red", ...],  // 54 color names
        "cube_string": "UUUUUUUUU...",        // 54-character cubestring (optional)
        "show_analysis": true                  // Optional: return detailed error message
    }
    
    Returns:
    {
        "success": true,
        "is_valid": true,
        "message": "Cube is valid",
        "analysis": "Cube is valid",  // Only if show_analysis=true
        "warnings": []
    }
    
    Or if invalid:
    {
        "success": true,
        "is_valid": false,
        "message": "Cube state is invalid",
        "analysis": "Wrong color counts: White: 11, Red: 7 (expected 9 each)",
        "warnings": []
    }
    """
    if not BACKEND_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Backend modules not available. Cannot validate cube state.'
        }), 503
    
    if validate_cube_state is None:
        return jsonify({
            'success': False,
            'error': 'Cube validation function not available.'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        cube_state = data.get('cube_state')
        cube_string = data.get('cube_string')
        show_analysis = data.get('show_analysis', False)
        
        if not cube_state or not isinstance(cube_state, list):
            return jsonify({
                'success': False,
                'error': 'Invalid cube_state: must be an array of 54 color names'
            }), 400
        
        if len(cube_state) != 54:
            return jsonify({
                'success': False,
                'error': f'Invalid cube_state length: expected 54, got {len(cube_state)}'
            }), 400
        
        # Validate using backend function with optional analysis
        if show_analysis:
            is_valid, analysis_message = validate_cube_state(cube_state, debug=False, show_analysis=True)
        else:
            is_valid = validate_cube_state(cube_state, debug=False, show_analysis=False)
            analysis_message = None
        
        warnings = []
        
        # Check if cube string matches cube state
        if cube_string and len(cube_string) == 54:
            # Verify cube_string matches cube_state
            expected_string = ''.join([COLOR_TO_CUBE.get(color, 'X') for color in cube_state])
            if cube_string != expected_string:
                warnings.append({
                    'type': 'cubestring_mismatch',
                    'message': 'Cube string does not match cube state',
                    'expected': expected_string,
                    'actual': cube_string
                })
        
        response = {
            'success': True,
            'is_valid': is_valid,
            'message': 'Cube is valid' if is_valid else 'Cube state is invalid',
            'warnings': warnings,
            'cube_state_length': len(cube_state)
        }
        
        # Add analysis message if requested
        if show_analysis and analysis_message:
            response['analysis'] = analysis_message
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}'
        }), 500

@app.route('/api/camera-status', methods=['GET'])
def camera_status():
    """Check camera availability and backend status"""
    try:
        import cv2
        
        # Check if camera is available
        cam = cv2.VideoCapture(0)
        camera_available = cam.isOpened()
        if camera_available:
            cam.release()
        
        return jsonify({
            'success': True,
            'camera_available': camera_available,
            'backend_available': BACKEND_AVAILABLE,
            'message': f"Camera: {'Available' if camera_available else 'Not available'}, Backend: {'Available' if BACKEND_AVAILABLE else 'Not available'}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'camera_available': False,
            'backend_available': BACKEND_AVAILABLE,
            'error': str(e)
        })

if __name__ == '__main__':
    print("Starting Rubik's Cube Color Detection API...")
    print("Available endpoints:")
    print("  POST /api/detect-colors - Detect colors from image")
    print("  POST /api/solve-cube - Solve cube using Kociemba algorithm")
    print("  GET  /api/health - Health check")
    print("  GET  /api/test - Test endpoint")
    print("\nWeb interface available at:")
    print("  http://localhost:5000/ - Main interface")
    print("  http://localhost:5000/test-interactivity.html - Test page")
    print("\nAPI running on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)