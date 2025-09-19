"""
Image processing utilities for Rubik's Cube Color Detection System
"""

import cv2
import numpy as np


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


def adaptive_brighten_image(image, base_brightness=25):
    """
    Adaptively brighten image based on overall brightness level.
    Applies more aggressive brightening to very dark images.
    
    Args:
        image: Input image
        base_brightness: Base brightness adjustment
    
    Returns:
        numpy.ndarray: Adaptively brightened image
    """
    # Calculate average brightness
    avg_brightness = np.mean(image)
    
    # Adaptive brightness adjustment
    if avg_brightness < 60:
        # Very dark image - apply strong brightening
        brightness = base_brightness + 40
        alpha = 1.2  # Also increase contrast slightly
    elif avg_brightness < 100:
        # Moderately dark - apply medium brightening
        brightness = base_brightness + 20
        alpha = 1.1
    else:
        # Normal brightness - use base settings
        brightness = base_brightness
        alpha = 1.0
    
    # Apply adaptive enhancement
    brightened = cv2.convertScaleAbs(image, alpha=alpha, beta=brightness)
    return brightened


def prepare_frame(frame, target_size=(600, 600), brightness=40):
    """
    Prepare camera frame for processing: crop to square, resize, enhance.
    
    Args:
        frame: Input camera frame
        target_size: Target size tuple (width, height)
        brightness: Brightness adjustment amount
    
    Returns:
        numpy.ndarray: Processed frame
    """
    # Crop to square aspect ratio to avoid distortion
    height, width = frame.shape[:2]
    if width > height:
        # Landscape: crop excess width from left and right
        start_x = (width - height) // 2
        frame = frame[:, start_x:start_x + height]
    elif height > width:
        # Portrait: crop excess height from top and bottom
        start_y = (height - width) // 2
        frame = frame[start_y:start_y + width, :]
    
    # Resize to target size
    frame = cv2.resize(frame, target_size)
    
    # Apply enhancements
    frame = correct_white_balance(frame)
    frame = brighten_image(frame, brightness=brightness)
    
    return frame