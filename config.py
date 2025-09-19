"""
Configuration and constants for Rubik's Cube Color Detection System
"""

import numpy as np
import warnings

# Suppress sklearn warnings once at startup to keep output clean
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

# ============================================================================
# COLOR DETECTION CONFIGURATION
# ============================================================================

# HSV color ranges for robust cube color detection
# HSV format: [Hue (0-180), Saturation (0-255), Value/Brightness (0-255)]
COLOR_RANGES = {
    "White": {
        "lower": np.array([0, 0, 200]),      # Any hue, low saturation, high brightness
        "upper": np.array([180, 30, 255]),   # White has very low saturation
        "backup_bgr": np.array([255, 255, 255])  # Pure white in BGR for fallback
    },
    "Red": {
        # Red spans across 0° in HSV color wheel, so we need two ranges
        "lower1": np.array([0, 120, 60]),    # Red range 1: 0-8 degrees, lower brightness threshold
        "upper1": np.array([8, 255, 255]),
        "lower2": np.array([172, 120, 60]),  # Red range 2: 172-180 degrees, lower brightness threshold
        "upper2": np.array([180, 255, 255]),
        "backup_bgr": np.array([0, 0, 180])  # Darker red for low-light comparison
    },
    "Green": {
        "lower": np.array([45, 60, 60]),     # Green hue range: 45-75 degrees, higher saturation and brightness
        "upper": np.array([75, 255, 255]),   # Narrower range to avoid confusion
        "backup_bgr": np.array([0, 180, 0])  # Darker green for low-light comparison
    },
    "Yellow": {
        "lower": np.array([20, 100, 100]),   # Yellow hue range: 20-30 degrees
        "upper": np.array([30, 255, 255]),
        "backup_bgr": np.array([0, 255, 255])  # Pure yellow in BGR
    },
    "Orange": {
        "lower": np.array([8, 120, 100]),    # Orange hue range: 8-18 degrees
        "upper": np.array([18, 255, 255]),   # Between red and yellow, higher saturation
        "backup_bgr": np.array([0, 140, 255])  # More distinct orange in BGR
    },
    "Blue": {
        "lower": np.array([100, 150, 0]),    # Blue hue range: 100-130 degrees
        "upper": np.array([130, 255, 255]),
        "backup_bgr": np.array([255, 0, 0])  # Pure blue in BGR
    }
}

# Standard Rubik's cube notation mapping
# U=Up(White), R=Right(Red), F=Front(Green), D=Down(Yellow), L=Left(Orange), B=Back(Blue)
COLOR_TO_CUBE = {
    "White": "U",   # Up face
    "Red": "R",     # Right face
    "Green": "F",   # Front face
    "Yellow": "D",  # Down face
    "Orange": "L",  # Left face
    "Blue": "B"     # Back face
}

# Camera and display settings
CAMERA_RESOLUTION = (600, 600)
GRID_STEP = 100
DETECTION_SIZE = 20
BRIGHTNESS_ADJUSTMENT = 40
PERFORMANCE_FRAME_SKIP = 5  # Only detect colors every 5th frame for smooth preview