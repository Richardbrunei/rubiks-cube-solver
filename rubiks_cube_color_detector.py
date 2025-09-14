"""
Rubik's Cube Color Detection System

This program captures and analyzes Rubik's cube faces using computer vision.
It provides real-time color detection with manual correction capabilities.

Features:
- Live camera preview with mirrored display for natural interaction
- Advanced HSV-based color detection with fallback methods
- White balance correction for camera color casts
- Interactive color editing system
- Performance optimizations for smooth real-time operation

Author: Richard and AI Assistant (Kiro)
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
import warnings
import kociemba

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
        "lower1": np.array([0, 120, 70]),    # Red range 1: 0-10 degrees
        "upper1": np.array([10, 255, 255]),
        "lower2": np.array([170, 120, 70]),  # Red range 2: 170-180 degrees
        "upper2": np.array([180, 255, 255]),
        "backup_bgr": np.array([0, 0, 200])  # Pure red in BGR
    },
    "Green": {
        "lower": np.array([40, 40, 40]),     # Green hue range: 40-80 degrees
        "upper": np.array([80, 255, 255]),
        "backup_bgr": np.array([0, 255, 0])  # Pure green in BGR
    },
    "Yellow": {
        "lower": np.array([20, 100, 100]),   # Yellow hue range: 20-30 degrees
        "upper": np.array([30, 255, 255]),
        "backup_bgr": np.array([0, 255, 255])  # Pure yellow in BGR
    },
    "Orange": {
        "lower": np.array([10, 100, 100]),   # Orange hue range: 10-20 degrees
        "upper": np.array([20, 255, 255]),   # Between red and yellow
        "backup_bgr": np.array([0, 165, 255])  # Orange in BGR
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

# ============================================================================
# COLOR DETECTION FUNCTIONS
# ============================================================================

def detect_color_advanced(patch, use_fast=False):
    """
    Advanced color detection using HSV ranges and multiple fallback methods.
    
    This function uses a two-stage approach:
    1. Primary: HSV range matching (most reliable for cube colors)
    2. Fallback: BGR distance calculation if HSV fails
    
    Args:
        patch: Image patch (numpy array) to analyze
        use_fast: If True, uses simple averaging instead of KMeans (faster for live preview)
    
    Returns:
        String: Detected color name or "Unknown"
    """
    if patch.size == 0:
        return "Unknown"
    
    # Step 1: Get dominant color from patch
    # Use fast method for live preview, accurate method for final capture
    if use_fast:
        dominant_bgr = get_dominant_color_fast(patch)
    else:
        dominant_bgr = get_dominant_color(patch)
    
    # Step 2: Convert BGR to HSV for better color analysis
    # HSV separates color information (hue) from brightness (value)
    bgr_pixel = np.uint8([[dominant_bgr]])
    hsv_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2HSV)[0][0]
    h, s, v = hsv_pixel
    
    # Step 3: Primary Method - HSV Range Detection
    # Score each color based on how well it matches HSV ranges
    color_scores = {}
    
    for color_name, ranges in COLOR_RANGES.items():
        score = 0
        
        if color_name == "Red":
            # Special case: Red wraps around 0° in HSV color wheel
            # Check both ranges: 0-10° and 170-180°
            if ((ranges["lower1"][0] <= h <= ranges["upper1"][0]) or 
                (ranges["lower2"][0] <= h <= ranges["upper2"][0])) and \
               (ranges["lower1"][1] <= s <= ranges["upper1"][1]) and \
               (ranges["lower1"][2] <= v <= ranges["upper1"][2]):
                score = 100
        elif color_name == "White":
            # Special case: White has low saturation and high brightness
            # Score inversely proportional to saturation (lower saturation = whiter)
            if s <= ranges["upper"][1] and v >= ranges["lower"][2]:
                score = 100 - s  # Higher score for lower saturation
        else:
            # Standard HSV range check for other colors
            if (ranges["lower"][0] <= h <= ranges["upper"][0]) and \
               (ranges["lower"][1] <= s <= ranges["upper"][1]) and \
               (ranges["lower"][2] <= v <= ranges["upper"][2]):
                score = 100
        
        color_scores[color_name] = score
    
    # Step 4: Fallback Method - BGR Distance
    # If no HSV matches found, use traditional color distance in BGR space
    if max(color_scores.values()) == 0:
        min_dist = float("inf")
        best_match = "Unknown"
        
        for color_name, ranges in COLOR_RANGES.items():
            # Calculate Euclidean distance in BGR color space
            bgr_dist = np.linalg.norm(dominant_bgr - ranges["backup_bgr"])
            if bgr_dist < min_dist:
                min_dist = bgr_dist
                best_match = color_name
        
        return best_match
    
    # Step 5: Return best match from HSV analysis
    best_color = max(color_scores, key=color_scores.get)
    return best_color if color_scores[best_color] > 0 else "Unknown"

# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================

def correct_white_balance(image):
    """
    Correct white balance to remove color casts (like bluish tint from cameras).
    
    This function analyzes the average color in each channel and adjusts them
    to be more neutral. Particularly effective for cameras with blue color cast.
    
    Args:
        image: Input image in BGR format
    
    Returns:
        numpy.ndarray: White balance corrected image
    """
    # Calculate average intensity for each BGR channel using vectorized operations
    means = np.mean(image, axis=(0, 1))  # [B_avg, G_avg, R_avg]
    avg_gray = np.mean(means)  # Overall average across all channels
    
    # Calculate scaling factors to balance channels
    # If a channel is too strong (like blue), its scale factor will be < 1.0
    scales = np.where(means > 0, avg_gray / means, 1.0)
    
    # Apply limits to prevent overcorrection and maintain natural look
    # Blue can be reduced more aggressively (1.3x) than green/red (1.2x)
    scales = np.clip(scales, 0.8, [1.3, 1.2, 1.2])  # [B, G, R] limits
    
    # Apply corrections using numpy broadcasting (much faster than loops)
    corrected = np.clip(image * scales, 0, 255).astype(np.uint8)
    return corrected

def brighten_image(image, brightness=25):
    """
    Brighten the image by adding a constant value to all pixels.
    
    Uses OpenCV's convertScaleAbs for efficient brightness adjustment.
    
    Args:
        image: Input image
        brightness: Amount to brighten (0-100 typical range)
    
    Returns:
        numpy.ndarray: Brightened image
    """
    # alpha=1.0 means no scaling, beta=brightness adds constant value
    brightened = cv2.convertScaleAbs(image, alpha=1.0, beta=brightness)
    return brightened

# ============================================================================
# DOMINANT COLOR EXTRACTION FUNCTIONS
# ============================================================================

def get_dominant_color_fast(patch):
    """
    Fast dominant color extraction using simple averaging.
    
    Used for live preview where speed is more important than perfect accuracy.
    Simply calculates the mean color of all pixels in the patch.
    
    Args:
        patch: Image patch to analyze
    
    Returns:
        numpy.ndarray: Average BGR color [B, G, R]
    """
    if patch.size == 0:
        return np.array([0, 0, 0])
    
    # Reshape to 2D array: [num_pixels, 3_channels] and calculate mean
    return np.mean(patch.reshape(-1, 3), axis=0)

def get_dominant_color(patch, k=2):
    """
    Accurate dominant color extraction using KMeans clustering.
    
    Used for final capture where accuracy is more important than speed.
    Groups similar colors together and returns the most common cluster center.
    
    Args:
        patch: Image patch to analyze
        k: Number of color clusters to find (default: 2)
    
    Returns:
        numpy.ndarray: Dominant BGR color [B, G, R]
    """
    if patch.size == 0:
        return np.array([0, 0, 0])
    
    # Reshape patch to list of pixels: [num_pixels, 3_channels]
    data = patch.reshape((-1, 3))
    
    # Performance optimization: Check for uniform patches first
    # Cube stickers are often very uniform in color
    if np.std(data) < 10:  # Very low color variation
        return np.mean(data, axis=0)  # Just return average
    
    # Check number of unique colors to avoid KMeans warnings
    unique_colors = np.unique(data, axis=0)
    
    if len(unique_colors) <= 1:
        # Only one unique color, return it directly
        return unique_colors[0] if len(unique_colors) == 1 else np.mean(data, axis=0)
    
    # Adjust cluster count to not exceed unique colors
    # This prevents "clusters < n_clusters" warnings
    actual_k = min(k, len(unique_colors))
    
    try:
        # Optimized KMeans settings for small patches:
        # - n_init=3: Fewer random initializations (faster)
        # - max_iter=50: Fewer iterations (faster)
        # - random_state=42: Reproducible results
        kmeans = KMeans(n_clusters=actual_k, n_init=3, max_iter=50, random_state=42)
        kmeans.fit(data)
        
        # Find the cluster with the most pixels (most dominant color)
        cluster_centers = kmeans.cluster_centers_
        counts = np.bincount(kmeans.labels_)
        dominant = cluster_centers[np.argmax(counts)]
        return dominant
        
    except Exception:
        # Fallback to simple averaging if KMeans fails for any reason
        return np.mean(data, axis=0)

# ============================================================================
# CAMERA INTERFACE FUNCTIONS
# ============================================================================

def show_live_preview(cam, face_name):
    """
    Display live camera preview with 3x3 alignment grid and real-time color detection.
    
    Features:
    - Mirrored display for natural interaction (like a selfie camera)
    - Performance optimized: only detects colors every 5th frame
    - Visual grid overlay to help align cube face
    - Real-time color labels showing detected colors
    
    Args:
        cam: OpenCV VideoCapture object
        face_name: Name of the face being captured (for display)
    
    Returns:
        bool: True if user pressed SPACE (capture), False if ESC (exit)
    """
    print(f"Position the {face_name} face in the grid. Press SPACE to capture or ESC to exit.")
    
    # Performance optimization: Cache color detection results
    # Only detect colors every 5th frame to maintain smooth video
    frame_count = 0
    cached_colors = ["?"] * 9  # Store last detected colors for each square
    
    while True:
        ret, frame = cam.read()
        if not ret:
            break
            
        # Step 1: Mirror frame horizontally for natural interaction
        # This makes camera movement feel intuitive (like looking in a mirror)
        frame = cv2.flip(frame, 1)
        
        # Step 2: Crop to square aspect ratio to avoid distortion
        # Most cameras are 16:9 or 4:3, but we need square for cube analysis
        height, width = frame.shape[:2]
        if width > height:
            # Landscape: crop excess width from left and right
            start_x = (width - height) // 2
            frame = frame[:, start_x:start_x + height]
        elif height > width:
            # Portrait: crop excess height from top and bottom
            start_y = (height - width) // 2
            frame = frame[start_y:start_y + width, :]
        
        # Step 3: Resize to standard 600x600 for consistent processing
        frame = cv2.resize(frame, (600, 600))
        
        # Step 4: Apply image enhancements
        frame = correct_white_balance(frame)  # Fix color cast
        frame = brighten_image(frame, brightness=40)  # Improve visibility
        
        # Step 5: Define 3x3 grid parameters
        step = 100  # Distance between grid squares (pixels)
        size = 20   # Half-size of detection squares (20px = 40x40 total)
        
        # Center the 3x3 grid on the 600x600 frame
        # Grid spans 2*step (200px), so center it: (600-200)/2 = 200px from edge
        start_x = (600 - 2 * step) // 2
        start_y = (600 - 2 * step) // 2
        
        # Step 6: Draw grid lines for visual alignment
        # Draw 4 vertical and 4 horizontal lines to create 3x3 grid
        for i in range(4):
            x_pos = start_x + i * step
            y_pos = start_y + i * step
            # Vertical lines
            cv2.line(frame, (x_pos, start_y), (x_pos, start_y + 3 * step), (255, 255, 255), 1)
            # Horizontal lines
            cv2.line(frame, (start_x, y_pos), (start_x + 3 * step, y_pos), (255, 255, 255), 1)
        
        # Step 7: Perform color detection (performance optimized)
        # Only detect colors every 5th frame to maintain smooth 30fps video
        # This reduces CPU usage while still providing responsive color updates
        if frame_count % 5 == 0:
            # Pre-calculate all 9 square positions to avoid repeated math
            positions = [(start_x + col * step + step // 2, start_y + row * step + step // 2) 
                        for row in range(3) for col in range(3)]
            
            # Detect color in each of the 9 squares
            for i, (x, y) in enumerate(positions):
                # Extract small patch around each square center
                patch = frame[y-size:y+size, x-size:x+size]  # 40x40 pixel patch
                if patch.size > 0:
                    # Use fast detection method for live preview (speed over accuracy)
                    label = detect_color_advanced(patch, use_fast=True)
                    # Cache result and abbreviate for display (first 3 letters)
                    cached_colors[i] = label[:3] if label != "Unknown" else "?"
        
        # Step 8: Draw detection squares and color labels
        # Use cached colors from last detection frame for smooth display
        for i, (row, col) in enumerate([(r, c) for r in range(3) for c in range(3)]):
            x = start_x + col * step + step // 2
            y = start_y + row * step + step // 2
            
            # Draw green detection square outline
            cv2.rectangle(frame, (x-size, y-size), (x+size, y+size), (0, 255, 0), 2)
            
            # Draw color label with outline for better visibility
            display_label = cached_colors[i]
            # White text with black outline for readability on any background
            cv2.putText(frame, display_label, (x-12, y+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, display_label, (x-12, y+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Step 9: Add user interface text
        # Title showing which face is being captured
        cv2.putText(frame, f"Capturing: {face_name} face", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        # Instructions for user interaction
        cv2.putText(frame, "SPACE: Capture | ESC: Exit", (10, 570),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Step 10: Display frame and handle user input
        cv2.imshow("Cube Face Capture", frame)
        
        frame_count += 1  # Increment for performance optimization timing
        
        # Check for user input (non-blocking)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Spacebar pressed - capture this face
            return True
        elif key == 27:  # ESC key pressed - exit program
            return False
        # Any other key or no key - continue live preview loop

def capture_face(cam):
    """
    Capture and analyze one cube face, returning detected colors.
    
    This function:
    1. Takes a single frame from camera
    2. Processes it with same enhancements as live preview
    3. Detects colors using accurate method (KMeans)
    4. Displays unmirrored result for 2 seconds
    5. Returns colors in unmirrored order for consistency
    
    Args:
        cam: OpenCV VideoCapture object
    
    Returns:
        list: 9 color names in reading order (left-to-right, top-to-bottom)
    """
    ret, frame = cam.read()
    if not ret:
        return ["X"] * 9

    # Process mirrored frame for color detection (consistent with preview)
    mirrored_frame = cv2.flip(frame, 1)
    
    # Maintain aspect ratio - crop to square from center instead of stretching
    height, width = mirrored_frame.shape[:2]
    if width > height:
        # Crop width to match height (landscape to square)
        start_x = (width - height) // 2
        mirrored_frame = mirrored_frame[:, start_x:start_x + height]
    elif height > width:
        # Crop height to match width (portrait to square)
        start_y = (height - width) // 2
        mirrored_frame = mirrored_frame[start_y:start_y + width, :]
    
    # Now resize to 600x600 without distortion
    mirrored_frame = cv2.resize(mirrored_frame, (600, 600))
    mirrored_frame = correct_white_balance(mirrored_frame)
    mirrored_frame = brighten_image(mirrored_frame, brightness=40)
    
    # Detect colors from mirrored frame
    colors = []
    step = 100
    size = 20
    start_x = (600 - 2 * step) // 2
    start_y = (600 - 2 * step) // 2
    
    for row in range(3):
        for col in range(3):
            x = start_x + col * step + step // 2
            y = start_y + row * step + step // 2
            patch = mirrored_frame[y-size:y+size, x-size:x+size]
            color_name = detect_color_advanced(patch)
            colors.append(color_name)

    # Create display frame (unmirrored for natural viewing)
    display_frame = frame.copy()
    
    # Apply same processing to display frame
    height, width = display_frame.shape[:2]
    if width > height:
        start_x = (width - height) // 2
        display_frame = display_frame[:, start_x:start_x + height]
    elif height > width:
        start_y = (height - width) // 2
        display_frame = display_frame[start_y:start_y + width, :]
    
    display_frame = cv2.resize(display_frame, (600, 600))
    display_frame = correct_white_balance(display_frame)
    display_frame = brighten_image(display_frame, brightness=40)
    
    # Draw visualization on unmirrored display frame
    # Note: colors array is in mirrored order, so we need to flip the column order
    for row in range(3):
        for col in range(3):
            x = start_x + col * step + step // 2
            y = start_y + row * step + step // 2
            
            # Get color from mirrored detection (flip column index)
            mirrored_col = 2 - col  # 0->2, 1->1, 2->0
            color_idx = row * 3 + mirrored_col
            color_name = colors[color_idx]
            
            # Get patch from display frame for visualization color
            patch = display_frame[y-size:y+size, x-size:x+size]
            dom_color = get_dominant_color(patch)

            # Draw visualization
            cv2.rectangle(display_frame, (x-size, y-size), (x+size, y+size),
                          (int(dom_color[0]), int(dom_color[1]), int(dom_color[2])), -1)
            
            # Show abbreviated color name at the correct unmirrored position
            display_label = color_name[:3] if color_name != "Unknown" else "?"
            cv2.putText(display_frame, display_label, (x-12, y+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Add title to show this is the unmirrored capture
    cv2.putText(display_frame, "Captured (Unmirrored)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Cube Face Capture", display_frame)
    cv2.waitKey(2000)  # Show result for 2 seconds
    
    # Return colors in unmirrored order for consistency with display
    unmirrored_colors = []
    for row in range(3):
        for col in range(3):
            mirrored_col = 2 - col  # Flip column order
            color_idx = row * 3 + mirrored_col
            unmirrored_colors.append(colors[color_idx])
    
    return unmirrored_colors

def edit_face_colors(face_name, colors):
    """Allow user to edit detected colors for a face"""
    print(f"\n=== Edit {face_name} Face Colors ===")
    print("Current detected colors:")
    
    # Display current colors in 3x3 grid
    for row in range(3):
        row_colors = []
        for col in range(3):
            idx = row * 3 + col
            color = colors[idx][:3] if colors[idx] != "Unknown" else "???"
            row_colors.append(f"{idx+1}:{color}")
        print("  " + "  ".join(row_colors))
    
    print("\nAvailable colors: White, Red, Green, Yellow, Orange, Blue")
    print("Commands:")
    print("  - Type position number (1-9) to edit that square")
    print("  - Type 'done' or 'd' to finish editing")
    print("  - Type 'reset' to restore original detection")
    
    original_colors = colors.copy()
    edited_colors = colors.copy()
    
    while True:
        try:
            user_input = input("\nEnter command: ").strip().lower()
            
            if user_input == 'done' or user_input == 'd':
                break
            elif user_input == 'reset':
                edited_colors = original_colors.copy()
                print("Colors reset to original detection")
                continue
            
            # Try to parse as position number
            try:
                pos = int(user_input)
                if 1 <= pos <= 9:
                    idx = pos - 1
                    current_color = edited_colors[idx]
                    
                    print(f"\nPosition {pos} is currently: {current_color}")
                    print("Available colors:")
                    color_options = list(COLOR_TO_CUBE.keys())
                    for i, color in enumerate(color_options, 1):
                        print(f"  {i}. {color}")
                    
                    color_input = input("Enter color name or number: ").strip()
                    
                    # Try to parse as number first
                    try:
                        color_num = int(color_input)
                        if 1 <= color_num <= len(color_options):
                            new_color = color_options[color_num - 1]
                        else:
                            print("Invalid color number")
                            continue
                    except ValueError:
                        # Try to match color name
                        new_color = None
                        for color in color_options:
                            if color.lower().startswith(color_input.lower()):
                                new_color = color
                                break
                        
                        if new_color is None:
                            print("Invalid color name")
                            continue
                    
                    edited_colors[idx] = new_color
                    print(f"Position {pos} changed to: {new_color}")
                    
                    # Show updated grid
                    print("\nUpdated colors:")
                    for row in range(3):
                        row_colors = []
                        for col in range(3):
                            idx = row * 3 + col
                            color = edited_colors[idx][:3] if edited_colors[idx] != "Unknown" else "???"
                            row_colors.append(f"{idx+1}:{color}")
                        print("  " + "  ".join(row_colors))
                else:
                    print("Position must be between 1 and 9")
            except ValueError:
                print("Invalid command. Use position number (1-9), 'done', or 'reset'")
                
        except KeyboardInterrupt:
            print("\nEditing cancelled")
            break
    
    return edited_colors

# ============================================================================
# CUBE VALIDATION FUNCTIONS
# ============================================================================

def validate_cube_state(cube_state):
    """
    Validate if the detected cube configuration is valid according to Rubik's cube rules.
    
    Checks:
    1. Exactly 9 stickers of each of the 6 colors
    2. All 12 edges are distinct and geometrically possible
    3. All 8 corners are distinct and geometrically possible
    
    Args:
        cube_state: List of 54 color names in face order [White, Red, Green, Yellow, Orange, Blue]
    
    Returns:
        dict: Validation results with 'valid' boolean and 'errors' list
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    if len(cube_state) != 54:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Invalid cube state length: {len(cube_state)} (expected 54)")
        return validation_result
    
    # Step 1: Check color count (must be exactly 9 of each color)
    color_counts = {}
    for color in cube_state:
        if color == "Unknown" or color == "X":
            validation_result['valid'] = False
            validation_result['errors'].append("Cube contains undetected colors (Unknown/X)")
            continue
        color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    for color in expected_colors:
        count = color_counts.get(color, 0)
        if count != 9:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid {color} count: {count} (expected 9)")
    
    # Check for unexpected colors
    for color in color_counts:
        if color not in expected_colors:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Unexpected color detected: {color}")
    
    # If basic color validation fails, don't continue with geometric checks
    if not validation_result['valid']:
        return validation_result
    
    # Step 2: Extract and validate edges (12 edges, each with 2 stickers)
    # Face layout: White(0-8), Red(9-17), Green(18-26), Yellow(27-35), Orange(36-44), Blue(45-53)
    # Each face: 0 1 2
    #            3 4 5  (4 is center)
    #            6 7 8
    
    edges = [
        # White face edges (top face)
        (cube_state[1], cube_state[46]),   # White top - Blue top
        (cube_state[3], cube_state[37]),   # White left - Orange top  
        (cube_state[5], cube_state[19]),   # White right - Red top
        (cube_state[7], cube_state[28]),   # White bottom - Green top
        
        # Middle layer edges
        (cube_state[12], cube_state[21]),  # Red left - Green right
        (cube_state[14], cube_state[39]),  # Red right - Orange left
        (cube_state[23], cube_state[41]),  # Green left - Orange right
        (cube_state[25], cube_state[48]),  # Green right - Blue left
        
        # Yellow face edges (bottom face)
        (cube_state[30], cube_state[16]),  # Yellow top - Red bottom
        (cube_state[32], cube_state[43]),  # Yellow right - Orange bottom
        (cube_state[34], cube_state[52]),  # Yellow bottom - Blue bottom
        (cube_state[36], cube_state[25]),  # Yellow left - Green bottom
    ]
    
    # Define impossible edge combinations (same color or opposite colors)
    impossible_edges = set()
    
    # Same color edges are impossible
    for color in expected_colors:
        impossible_edges.add((color, color))
    
    # Opposite color edges are impossible (White-Yellow, Red-Orange, Green-Blue)
    opposite_pairs = [("White", "Yellow"), ("Red", "Orange"), ("Green", "Blue")]
    for color1, color2 in opposite_pairs:
        impossible_edges.add((color1, color2))
        impossible_edges.add((color2, color1))
    
    # Check each edge
    seen_edges = set()
    for i, (color1, color2) in enumerate(edges):
        # Normalize edge (smaller color first for comparison)
        edge = tuple(sorted([color1, color2]))
        
        # Check if edge is impossible
        if (color1, color2) in impossible_edges or (color2, color1) in impossible_edges:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Impossible edge {i+1}: {color1}-{color2}")
        
        # Check if edge is duplicate
        if edge in seen_edges:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Duplicate edge: {color1}-{color2}")
        else:
            seen_edges.add(edge)
    
    # Step 3: Extract and validate corners (8 corners, each with 3 stickers)
    corners = [
        # White face corners
        (cube_state[0], cube_state[36], cube_state[47]),  # White-Orange-Blue
        (cube_state[2], cube_state[18], cube_state[10]),  # White-Green-Red
        (cube_state[6], cube_state[9], cube_state[38]),   # White-Red-Orange
        (cube_state[8], cube_state[45], cube_state[20]),  # White-Blue-Green
        
        # Yellow face corners  
        (cube_state[27], cube_state[15], cube_state[24]), # Yellow-Red-Green
        (cube_state[29], cube_state[26], cube_state[42]), # Yellow-Green-Orange
        (cube_state[33], cube_state[44], cube_state[17]), # Yellow-Orange-Blue
        (cube_state[35], cube_state[51], cube_state[11]), # Yellow-Blue-Red
    ]
    
    # Check each corner
    seen_corners = set()
    for i, corner in enumerate(corners):
        color1, color2, color3 = corner
        
        # Check for impossible same-color corners
        if len(set(corner)) < 3:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Corner {i+1} has repeated colors: {color1}-{color2}-{color3}")
            continue
        
        # Check for impossible opposite-color corners
        corner_colors = set(corner)
        for color_a, color_b in opposite_pairs:
            if color_a in corner_colors and color_b in corner_colors:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Corner {i+1} has opposite colors: {color1}-{color2}-{color3}")
                break
        
        # Normalize corner (sort colors for comparison)
        normalized_corner = tuple(sorted(corner))
        
        # Check if corner is duplicate
        if normalized_corner in seen_corners:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Duplicate corner: {color1}-{color2}-{color3}")
        else:
            seen_corners.add(normalized_corner)
    
    # Step 4: Check that we have exactly 12 unique edges and 8 unique corners
    if len(seen_edges) != 12:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Expected 12 unique edges, found {len(seen_edges)}")
    
    if len(seen_corners) != 8:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Expected 8 unique corners, found {len(seen_corners)}")
    
    return validation_result

def rotate_face_90(face):
    """
    Rotate a 3x3 face 90 degrees clockwise.
    
    Face positions:     After 90° rotation:
    0 1 2               6 3 0
    3 4 5       →       7 4 1  
    6 7 8               8 5 2
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: Rotated face
    """
    if len(face) != 9:
        return face
    
    # Mapping for 90-degree clockwise rotation
    rotation_map = [6, 3, 0, 7, 4, 1, 8, 5, 2]
    return [face[i] for i in rotation_map]

def rotate_face_180(face):
    """
    Rotate a 3x3 face 180 degrees.
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: Rotated face
    """
    # 180° = two 90° rotations
    return rotate_face_90(rotate_face_90(face))

def rotate_face_270(face):
    """
    Rotate a 3x3 face 270 degrees clockwise (or 90 degrees counter-clockwise).
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: Rotated face
    """
    # 270° = three 90° rotations
    return rotate_face_90(rotate_face_90(rotate_face_90(face)))

def get_all_face_rotations(face):
    """
    Get all 4 possible rotations of a face (0°, 90°, 180°, 270°).
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: List of 4 rotated faces [0°, 90°, 180°, 270°]
    """
    return [
        face,                    # 0° (original)
        rotate_face_90(face),    # 90°
        rotate_face_180(face),   # 180°
        rotate_face_270(face)    # 270°
    ]

def fix_cube_face_order(cube_state):
    """
    Fix cube face order by placing each face in the correct position based on center pieces.
    
    Standard cube notation expects faces in order: White, Red, Green, Yellow, Orange, Blue
    This function reorders the faces so each center piece matches its expected position.
    
    Args:
        cube_state: List of 54 colors in current face order
    
    Returns:
        tuple: (fixed_cube_state, face_mapping) where face_mapping shows the reordering
    """
    if len(cube_state) != 54:
        return cube_state, {}
    
    # Extract faces (9 stickers each)
    faces = []
    for i in range(6):
        start_idx = i * 9
        face = cube_state[start_idx:start_idx + 9]
        faces.append(face)
    
    # Get center colors (position 4 in each 3x3 face)
    center_colors = [face[4] for face in faces]
    
    # Expected face order and their center colors
    expected_order = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    
    # Create mapping from current position to correct position
    face_mapping = {}
    fixed_faces = [None] * 6
    
    for current_pos, center_color in enumerate(center_colors):
        if center_color in expected_order:
            correct_pos = expected_order.index(center_color)
            fixed_faces[correct_pos] = faces[current_pos]
            face_mapping[current_pos] = correct_pos
    
    # Handle any unmapped faces (put them in remaining slots)
    for i, face in enumerate(fixed_faces):
        if face is None:
            # Find first unmapped original face
            for orig_pos, orig_face in enumerate(faces):
                if orig_pos not in face_mapping:
                    fixed_faces[i] = orig_face
                    face_mapping[orig_pos] = i
                    break
    
    # Flatten back to single list
    fixed_cube_state = []
    for face in fixed_faces:
        if face:
            fixed_cube_state.extend(face)
        else:
            # Fallback: add placeholder if something went wrong
            fixed_cube_state.extend(["Unknown"] * 9)
    
    return fixed_cube_state, face_mapping

def is_cube_theoretically_valid(cube_state):
    """
    Check if a cube can theoretically be made valid through rotation alone.
    
    This checks fundamental constraints that rotation cannot fix:
    - Color count must be exactly 9 of each color
    - No unknown/undetected colors
    - Must have all 6 expected colors
    
    Args:
        cube_state: List of 54 colors
    
    Returns:
        tuple: (is_valid, error_reasons) where error_reasons is a list of issues
    """
    if len(cube_state) != 54:
        return False, ["Incomplete cube state (not 54 stickers)"]
    
    errors = []
    
    # Check for unknown colors
    unknown_count = cube_state.count("Unknown") + cube_state.count("X")
    if unknown_count > 0:
        errors.append(f"Contains {unknown_count} undetected colors")
    
    # Check color counts
    color_counts = {}
    for color in cube_state:
        if color not in ["Unknown", "X"]:
            color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    
    # Check if we have all expected colors
    missing_colors = [color for color in expected_colors if color not in color_counts]
    if missing_colors:
        errors.append(f"Missing colors: {', '.join(missing_colors)}")
    
    # Check for unexpected colors
    unexpected_colors = [color for color in color_counts if color not in expected_colors]
    if unexpected_colors:
        errors.append(f"Unexpected colors: {', '.join(unexpected_colors)}")
    
    # Check color counts
    for color in expected_colors:
        count = color_counts.get(color, 0)
        if count != 9:
            if count == 0:
                continue  # Already reported as missing
            errors.append(f"Wrong {color} count: {count} (need exactly 9)")
    
    return len(errors) == 0, errors

def fix_cube_complete(cube_state):
    """
    Complete cube fixing process: reorder faces by centers, then find optimal rotations.
    
    Two-stage process:
    1. Reorder faces based on center pieces (W=Up, Y=Down, etc.)
    2. Try all rotation combinations to find a valid cube configuration
    
    Args:
        cube_state: List of 54 colors in capture order
    
    Returns:
        tuple: (fixed_cube_state, face_reordering, rotations_applied, final_score, is_valid)
    """
    if len(cube_state) != 54:
        return cube_state, {}, [0] * 6, 0, False
    
    print("🔄 Stage 1: Reordering faces by center pieces...")
    
    # Stage 1: Reorder faces based on center pieces
    reordered_cube, face_mapping = fix_cube_face_order(cube_state)
    
    # Stage 2: Find optimal face rotations
    print("🔄 Stage 2: Finding optimal face orientations...")
    
    # Check if cube can theoretically be made valid
    is_theoretically_valid, theoretical_errors = is_cube_theoretically_valid(reordered_cube)
    
    if not is_theoretically_valid:
        print("❌ Cannot create valid cube - fundamental issues detected:")
        for error in theoretical_errors:
            print(f"   • {error}")
        return reordered_cube, face_mapping, [0] * 6, 0, False
    
    # Extract faces from reordered cube
    faces = []
    for i in range(6):
        start_idx = i * 9
        face = reordered_cube[start_idx:start_idx + 9]
        faces.append(face)
    
    # Get all possible rotations for each face
    face_rotations = [get_all_face_rotations(face) for face in faces]
    rotation_degrees = [0, 90, 180, 270]
    
    best_score = -1
    best_cube_state = reordered_cube
    best_rotations = [0] * 6
    
    # Try ALL possible rotation combinations systematically
    # 6 faces × 4 rotations each = 4^6 = 4096 total combinations
    tested_combinations = 0
    
    # Nested loops for all combinations: for white in range(4): for red in range(4): etc.
    for white_rot in range(4):      # White face: 0°, 90°, 180°, 270°
        for red_rot in range(4):    # Red face: 0°, 90°, 180°, 270°
            for green_rot in range(4):  # Green face: 0°, 90°, 180°, 270°
                for yellow_rot in range(4):  # Yellow face: 0°, 90°, 180°, 270°
                    for orange_rot in range(4):  # Orange face: 0°, 90°, 180°, 270°
                        for blue_rot in range(4):  # Blue face: 0°, 90°, 180°, 270°
                            
                            # Create test cube with this rotation combination
                            test_cube = []
                            rotations = [white_rot, red_rot, green_rot, yellow_rot, orange_rot, blue_rot]
                            
                            for face_idx, rotation_idx in enumerate(rotations):
                                rotated_face = face_rotations[face_idx][rotation_idx]
                                test_cube.extend(rotated_face)
                            
                            tested_combinations += 1
                            
                            # Check if this combination creates a valid cube
                            validation_result = validate_cube_state(test_cube)
                            if validation_result['valid']:
                                # Found perfect solution!
                                best_cube_state = test_cube
                                best_rotations = [rotation_degrees[r] for r in rotations]
                                best_score = 100
                                print(f"✅ Found valid cube after {tested_combinations} combinations!")
                                # Return immediately - we found the solution
                                final_validation = validate_cube_state(best_cube_state)
                                is_valid_solution = final_validation['valid']
                                return best_cube_state, face_mapping, best_rotations, best_score, is_valid_solution
                            
                            # Track best score for non-perfect solutions
                            score = calculate_cube_score(test_cube)
                            if score > best_score:
                                best_score = score
                                best_cube_state = test_cube
                                best_rotations = [rotation_degrees[r] for r in rotations]
                            
                            # Progress indicator for long searches
                            if tested_combinations % 1000 == 0:
                                print(f"   Tested {tested_combinations}/4096 combinations...")
    
    print(f"⚠️  Tested all {tested_combinations} combinations - no perfect solution found")
    
    # Final validation
    final_validation = validate_cube_state(best_cube_state)
    is_valid_solution = final_validation['valid']
    
    return best_cube_state, face_mapping, best_rotations, best_score, is_valid_solution

def calculate_cube_score(cube_state):
    """
    Calculate a score for how "valid" a cube configuration is.
    Higher scores indicate better cube validity.
    
    Args:
        cube_state: List of 54 colors
    
    Returns:
        int: Score (0-100+, higher is better)
    """
    if len(cube_state) != 54:
        return 0
    
    score = 0
    
    # Check color counts (most important)
    color_counts = {}
    for color in cube_state:
        if color not in ["Unknown", "X"]:
            color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    for color in expected_colors:
        count = color_counts.get(color, 0)
        if count == 9:
            score += 15  # Perfect color count
        elif 7 <= count <= 11:
            score += 10  # Close to correct
        elif 5 <= count <= 13:
            score += 5   # Somewhat close
    
    # Check center pieces (important for face identification)
    center_positions = [4, 13, 22, 31, 40, 49]
    for i, pos in enumerate(center_positions):
        if pos < len(cube_state):
            center_color = cube_state[pos]
            expected_color = expected_colors[i]
            if center_color == expected_color:
                score += 5  # Correct center
    
    # Bonus for no unknown colors
    if "Unknown" not in cube_state and "X" not in cube_state:
        score += 10
    
    return score

def print_cube_net(cube_state):
    """
    Print the cube as a net (unfolded layout) showing all 6 faces.
    
    Layout:
        U U U
        U U U  
        U U U
    L L L F F F R R R B B B
    L L L F F F R R R B B B
    L L L F F F R R R B B B
        D D D
        D D D
        D D D
    
    Where: U=Up(White), L=Left(Orange), F=Front(Green), R=Right(Red), B=Back(Blue), D=Down(Yellow)
    
    Args:
        cube_state: List of 54 colors in face order [White, Red, Green, Yellow, Orange, Blue]
    """
    if len(cube_state) != 54:
        print("Cannot display cube net - incomplete cube state")
        return
    
    # Extract faces (9 stickers each)
    faces = {}
    face_names = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    face_letters = ["U", "R", "F", "D", "L", "B"]
    
    for i, name in enumerate(face_names):
        start_idx = i * 9
        face = cube_state[start_idx:start_idx + 9]
        # Use single letter for each color
        face_display = []
        color_letters = {
            "White": "W",
            "Red": "R", 
            "Green": "G",
            "Yellow": "Y",
            "Orange": "O",
            "Blue": "B"
        }
        for color in face:
            if color in color_letters:
                face_display.append(color_letters[color])
            else:
                face_display.append("?")
        faces[name] = face_display
    
    print("\n" + "="*50)
    print("CUBE NET LAYOUT")
    print("="*50)
    
    # Print the net in classic cross pattern
    # Top face (White/Up)
    print("      " + " ".join(faces["White"][0:3]))
    print("      " + " ".join(faces["White"][3:6]))
    print("      " + " ".join(faces["White"][6:9]))
    
    # Middle row: Left, Front, Right, Back
    for row in range(3):
        left_row = faces["Orange"][row*3:(row+1)*3]
        front_row = faces["Green"][row*3:(row+1)*3]
        right_row = faces["Red"][row*3:(row+1)*3]
        back_row = faces["Blue"][row*3:(row+1)*3]
        
        print(" ".join(left_row) + " " + " ".join(front_row) + " " + 
              " ".join(right_row) + " " + " ".join(back_row))
    
    # Bottom face (Yellow/Down)
    print("      " + " ".join(faces["Yellow"][0:3]))
    print("      " + " ".join(faces["Yellow"][3:6]))
    print("      " + " ".join(faces["Yellow"][6:9]))
    
    print("\nColors: W=White, R=Red, G=Green, Y=Yellow, O=Orange, B=Blue")
    print("="*50)

def print_validation_results(validation_result):
    """
    Print cube validation results in a user-friendly format.
    
    Args:
        validation_result: Dictionary from validate_cube_state()
    """
    print("\n" + "="*50)
    print("CUBE VALIDATION RESULTS")
    print("="*50)
    
    if validation_result['valid']:
        print("✅ CUBE IS VALID!")
        print("The detected cube configuration follows Rubik's cube rules.")
    else:
        print("❌ CUBE IS INVALID!")
        print("The detected cube configuration has errors.")
    
    if validation_result['errors']:
        print(f"\n🚫 ERRORS ({len(validation_result['errors'])}):")
        for i, error in enumerate(validation_result['errors'], 1):
            print(f"  {i}. {error}")
    
    if validation_result['warnings']:
        print(f"\n⚠️  WARNINGS ({len(validation_result['warnings'])}):")
        for i, warning in enumerate(validation_result['warnings'], 1):
            print(f"  {i}. {warning}")
    
    if not validation_result['errors'] and not validation_result['warnings']:
        print("\n🎉 Perfect detection! No issues found.")
    
    print("="*50)

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """
    Main program loop for Rubik's cube color detection.
    
    Process:
    1. Initialize camera with optimized settings
    2. Capture each of 6 cube faces in standard order
    3. Allow user to edit any misdetected colors
    4. Generate final cube string in standard notation
    """
    # Initialize camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Camera not accessible. Please check camera connection.")
        return
    
    # Optimize camera settings for performance and quality
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Lower resolution for better performance
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv2.CAP_PROP_FPS, 30)            # Standard frame rate
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)      # Minimal buffer to reduce lag

    # Standard cube face order for consistent solving
    # This order ensures proper cube state representation for solvers
    face_order = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    cube_state = []  # Will store all 54 sticker colors (9 per face × 6 faces)

    print("=== Rubik's Cube Color Detection ===")
    print("Capture faces in order:", " → ".join(face_order))
    
    # Main capture loop - process each face
    for face in face_order:
        print(f"\n📷 Capturing {face} face...")
        
        # Step 1: Show live preview until user presses SPACE or ESC
        if not show_live_preview(cam, face):
            print("Capture cancelled by user")
            break
            
        # Step 2: Capture and analyze the face
        colors = capture_face(cam)
        
        # Step 3: Allow user to correct any mistakes
        while True:
            edit_choice = input("Edit colors? (y/n): ").strip().lower()
            if edit_choice in ['y', 'yes']:
                colors = edit_face_colors(face, colors)
                break
            elif edit_choice in ['n', 'no']:
                break
            else:
                print("Please enter 'y' or 'n'")
        
        # Step 4: Store final colors
        cube_state.extend(colors)
        cube_notation = [COLOR_TO_CUBE.get(color, "X") for color in colors]
        print(f"✅ {face}: {''.join(cube_notation)}")

    # Cleanup camera resources
    cam.release()
    cv2.destroyAllWindows()

    # Generate final results
    cube_notation_list = [COLOR_TO_CUBE.get(color, "X") for color in cube_state]
    cube_string = "".join(cube_notation_list)
    
    # Display initial results
    print(f"\n📊 Captured {len(cube_state)}/54 stickers")
    print(f"Raw cube string: {cube_string}")
    
    # Complete cube fixing process
    if len(cube_state) == 54:
        print("\n" + "="*60)
        print("CUBE FIXING PROCESS")
        print("="*60)
        
        fixed_cube_state, face_mapping, rotations_applied, final_score, is_valid = fix_cube_complete(cube_state)
        
        # Show what was done
        if face_mapping:
            reordering_made = any(orig != new for orig, new in face_mapping.items())
            if reordering_made:
                print("✅ Stage 1: Faces reordered by center pieces")
            else:
                print("✅ Stage 1: Face order was already correct")
        
        rotations_made = any(r != 0 for r in rotations_applied)
        if rotations_made:
            face_names = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
            rotated_faces = [f"{face_names[i]}({rotations_applied[i]}°)" 
                           for i in range(6) if rotations_applied[i] != 0]
            print(f"✅ Stage 2: Rotated faces: {', '.join(rotated_faces)}")
        else:
            print("✅ Stage 2: No face rotations needed")
        
        # Update cube state
        cube_state = fixed_cube_state
        cube_notation_list = [COLOR_TO_CUBE.get(color, "X") for color in cube_state]
        cube_string = "".join(cube_notation_list)
        cube_state_string = str(cube_state)
        
        status = "✅" if is_valid else "⚠️"
        print(f"{status} Final result: Score {final_score}/100 {'(VALID CUBE!)' if is_valid else '(needs improvement)'}")
        
        print("="*60)
    
    # Final validation after all fixes
    if len(cube_state) == 54:
        print("\n" + "="*60)
        print("FINAL CUBE VALIDATION")
        print("="*60)
        
        validation_result = validate_cube_state(cube_state)
        print_validation_results(validation_result)
        
        if validation_result['valid']:
            print("\n🎉 SUCCESS! Cube is valid and ready for solving")
            print(f"Final cube string: {cube_string}")
            print(kociemba.solve(cube_string))
        else:
            print("\n❌ IMPOSSIBLE CUBE - Cannot be solved in current state")
            print("Possible causes: Color detection errors, physical cube issues, or impossible configuration")
            print("Try: Re-capture with better lighting, edit colors, or check cube assembly")
            
        print("="*60)
    else:
        print("\n⚠️  Cannot validate incomplete cube state")
    
    # Display cube net
    if len(cube_state) == 54:
        print_cube_net(cube_state)

# Program entry point
if __name__ == "__main__":
    print("Rubik's Cube Color Detection System")
    print("===================================")
    main()
