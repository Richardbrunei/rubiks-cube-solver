"""
Color detection functions for Rubik's Cube Color Detection System
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from config import COLOR_RANGES


def detect_color_low_brightness(dominant_bgr, h, s, v):
    """
    Special color detection for low brightness situations where HSV hue is unreliable.
    
    At low brightness levels, red and green can be confused because hue information
    becomes less reliable. This function uses BGR ratios and remaining HSV info.
    
    Args:
        dominant_bgr: BGR color values
        h, s, v: HSV values for additional context
    
    Returns:
        String: Detected color name
    """
    b, g, r = dominant_bgr
    
    # Normalize BGR values to get ratios
    total = b + g + r
    if total == 0:
        return "White"
    
    b_ratio = b / total
    g_ratio = g / total  
    r_ratio = r / total
    
    # Low brightness color detection using BGR ratios and HSV context
    
    # White detection - high overall brightness despite low V (can happen with overexposure correction)
    if total > 400 and max(b_ratio, g_ratio, r_ratio) - min(b_ratio, g_ratio, r_ratio) < 0.15:
        return "White"
    
    # Red detection - red channel dominant, hue near 0° or 180°
    if r_ratio > 0.45 and r_ratio > g_ratio + 0.15 and r_ratio > b_ratio + 0.15:
        if h <= 15 or h >= 165:  # Hue check for confirmation
            return "Red"
    
    # Green detection - green channel dominant, hue in green range
    if g_ratio > 0.45 and g_ratio > r_ratio + 0.15 and g_ratio > b_ratio + 0.15:
        if 35 <= h <= 85:  # Hue check for confirmation
            return "Green"
    
    # Blue detection - blue channel dominant
    if b_ratio > 0.45 and b_ratio > r_ratio + 0.15 and b_ratio > g_ratio + 0.15:
        if 90 <= h <= 140:
            return "Blue"
    
    # Orange detection - red and green both high, but red higher
    if r_ratio > 0.35 and g_ratio > 0.25 and r_ratio > g_ratio and b_ratio < 0.3:
        if 5 <= h <= 25:
            return "Orange"
    
    # Yellow detection - red and green both high and similar
    if r_ratio > 0.35 and g_ratio > 0.35 and abs(r_ratio - g_ratio) < 0.1 and b_ratio < 0.25:
        if 15 <= h <= 35:
            return "Yellow"
    
    # Fallback: use BGR distance method
    min_dist = float("inf")
    best_match = "White"
    
    for color_name, ranges in COLOR_RANGES.items():
        bgr_dist = np.linalg.norm(dominant_bgr - ranges["backup_bgr"])
        if bgr_dist < min_dist:
            min_dist = bgr_dist
            best_match = color_name
    
    return best_match


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
        String: Detected color name or "White"
    """
    if patch.size == 0:
        return "White"
    
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
    
    # Step 2.5: Low brightness detection - use BGR method for very dark colors
    # At low brightness (V < 80), hue becomes unreliable, especially for red/green confusion
    if v < 80:
        return detect_color_low_brightness(dominant_bgr, h, s, v)
    
    # Step 3: Primary Method - HSV Range Detection with Red-Orange Disambiguation
    # Score each color based on how well it matches HSV ranges
    color_scores = {}
    
    for color_name, ranges in COLOR_RANGES.items():
        score = 0
        
        if color_name == "Red":
            # Special case: Red wraps around 0° in HSV color wheel
            # Check both ranges: 0-8° and 172-180°
            if ((ranges["lower1"][0] <= h <= ranges["upper1"][0]) or 
                (ranges["lower2"][0] <= h <= ranges["upper2"][0])) and \
               (ranges["lower1"][1] <= s <= ranges["upper1"][1]) and \
               (ranges["lower1"][2] <= v <= ranges["upper1"][2]):
                # Boost score for very red hues (closer to 0° or 180°)
                if h <= 5 or h >= 175:
                    score = 120  # Higher confidence for pure red
                else:
                    score = 100
        elif color_name == "Orange":
            # Special handling for orange to distinguish from red
            if (ranges["lower"][0] <= h <= ranges["upper"][0]) and \
               (ranges["lower"][1] <= s <= ranges["upper"][1]) and \
               (ranges["lower"][2] <= v <= ranges["upper"][2]):
                # Boost score for mid-orange hues (around 12-15°)
                if 10 <= h <= 16:
                    score = 120  # Higher confidence for pure orange
                else:
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
    
    # Step 3.5: Red-Orange Disambiguation
    # If both red and orange have scores, apply additional logic
    if color_scores.get("Red", 0) > 0 and color_scores.get("Orange", 0) > 0:
        # Use hue to make final decision
        if h <= 6 or h >= 174:
            # Very close to red endpoints - definitely red
            color_scores["Orange"] = 0
        elif 10 <= h <= 16:
            # Clearly in orange range - definitely orange
            color_scores["Red"] = 0
        else:
            # Ambiguous range (6-10°) - use saturation and value
            # Red typically has higher saturation, orange is often slightly less saturated
            if s >= 180:
                color_scores["Orange"] = max(0, color_scores["Orange"] - 20)
            else:
                color_scores["Red"] = max(0, color_scores["Red"] - 20)
    
    # Step 4: Fallback Method - BGR Distance
    # If no HSV matches found, use traditional color distance in BGR space
    if max(color_scores.values()) == 0:
        min_dist = float("inf")
        best_match = "White"
        
        for color_name, ranges in COLOR_RANGES.items():
            # Calculate Euclidean distance in BGR color space
            bgr_dist = np.linalg.norm(dominant_bgr - ranges["backup_bgr"])
            if bgr_dist < min_dist:
                min_dist = bgr_dist
                best_match = color_name
        
        return best_match
    
    # Step 5: Return best match from HSV analysis
    best_color = max(color_scores, key=color_scores.get)
    return best_color if color_scores[best_color] > 0 else "White"


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