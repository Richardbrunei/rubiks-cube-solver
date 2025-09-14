"""
Color detection functions for Rubik's Cube Color Detection System
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from config import COLOR_RANGES


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