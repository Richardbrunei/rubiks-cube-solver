"""
Camera interface and user interaction functions for Rubik's Cube Color Detection System
"""

import cv2
from config import COLOR_TO_CUBE, CAMERA_RESOLUTION, GRID_STEP, DETECTION_SIZE, BRIGHTNESS_ADJUSTMENT, PERFORMANCE_FRAME_SKIP
from color_detection import detect_color_advanced, get_dominant_color
from image_processing import correct_white_balance, brighten_image, adaptive_brighten_image


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
        frame = cv2.flip(frame, 1)
        
        # Step 2: Crop to square aspect ratio and resize
        height, width = frame.shape[:2]
        if width > height:
            start_x = (width - height) // 2
            frame = frame[:, start_x:start_x + height]
        elif height > width:
            start_y = (height - width) // 2
            frame = frame[start_y:start_y + width, :]
        
        frame = cv2.resize(frame, CAMERA_RESOLUTION)
        
        # Step 3: Apply image enhancements
        frame = correct_white_balance(frame)
        frame = adaptive_brighten_image(frame, base_brightness=BRIGHTNESS_ADJUSTMENT)
        
        # Step 4: Define 3x3 grid parameters
        start_x = (CAMERA_RESOLUTION[0] - 2 * GRID_STEP) // 2
        start_y = (CAMERA_RESOLUTION[1] - 2 * GRID_STEP) // 2
        
        # Step 5: Draw grid lines
        for i in range(4):
            x_pos = start_x + i * GRID_STEP
            y_pos = start_y + i * GRID_STEP
            cv2.line(frame, (x_pos, start_y), (x_pos, start_y + 3 * GRID_STEP), (255, 255, 255), 1)
            cv2.line(frame, (start_x, y_pos), (start_x + 3 * GRID_STEP, y_pos), (255, 255, 255), 1)
        
        # Step 6: Perform color detection (performance optimized)
        if frame_count % PERFORMANCE_FRAME_SKIP == 0:
            positions = [(start_x + col * GRID_STEP + GRID_STEP // 2, start_y + row * GRID_STEP + GRID_STEP // 2) 
                        for row in range(3) for col in range(3)]
            
            for i, (x, y) in enumerate(positions):
                patch = frame[y-DETECTION_SIZE:y+DETECTION_SIZE, x-DETECTION_SIZE:x+DETECTION_SIZE]
                if patch.size > 0:
                    label = detect_color_advanced(patch, use_fast=True)
                    cached_colors[i] = label[:3] if label != "Unknown" else "?"
        
        # Step 7: Draw detection squares and labels
        for i, (row, col) in enumerate([(r, c) for r in range(3) for c in range(3)]):
            x = start_x + col * GRID_STEP + GRID_STEP // 2
            y = start_y + row * GRID_STEP + GRID_STEP // 2
            
            cv2.rectangle(frame, (x-DETECTION_SIZE, y-DETECTION_SIZE), 
                         (x+DETECTION_SIZE, y+DETECTION_SIZE), (0, 255, 0), 2)
            
            display_label = cached_colors[i]
            cv2.putText(frame, display_label, (x-12, y+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, display_label, (x-12, y+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Step 8: Add UI text
        cv2.putText(frame, f"Capturing: {face_name} face", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "SPACE: Capture | ESC: Exit", (10, 570),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Step 9: Display and handle input
        cv2.imshow("Cube Face Capture", frame)
        frame_count += 1
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            return True
        elif key == 27:
            return False


def capture_face(cam):
    """
    Capture and analyze one cube face, returning detected colors.
    
    Returns:
        list: 9 color names in reading order (left-to-right, top-to-bottom)
    """
    ret, frame = cam.read()
    if not ret:
        return ["X"] * 9

    # Process mirrored frame for color detection
    mirrored_frame = cv2.flip(frame, 1)
    
    # Crop to square and resize
    height, width = mirrored_frame.shape[:2]
    if width > height:
        start_x = (width - height) // 2
        mirrored_frame = mirrored_frame[:, start_x:start_x + height]
    elif height > width:
        start_y = (height - width) // 2
        mirrored_frame = mirrored_frame[start_y:start_y + width, :]
    
    mirrored_frame = cv2.resize(mirrored_frame, CAMERA_RESOLUTION)
    mirrored_frame = correct_white_balance(mirrored_frame)
    mirrored_frame = adaptive_brighten_image(mirrored_frame, base_brightness=BRIGHTNESS_ADJUSTMENT)
    
    # Detect colors
    colors = []
    start_x = (CAMERA_RESOLUTION[0] - 2 * GRID_STEP) // 2
    start_y = (CAMERA_RESOLUTION[1] - 2 * GRID_STEP) // 2
    
    for row in range(3):
        for col in range(3):
            x = start_x + col * GRID_STEP + GRID_STEP // 2
            y = start_y + row * GRID_STEP + GRID_STEP // 2
            patch = mirrored_frame[y-DETECTION_SIZE:y+DETECTION_SIZE, x-DETECTION_SIZE:x+DETECTION_SIZE]
            color_name = detect_color_advanced(patch)
            colors.append(color_name)

    # Create display frame (unmirrored)
    display_frame = frame.copy()
    height, width = display_frame.shape[:2]
    if width > height:
        start_x = (width - height) // 2
        display_frame = display_frame[:, start_x:start_x + height]
    elif height > width:
        start_y = (height - width) // 2
        display_frame = display_frame[start_y:start_y + width, :]
    
    display_frame = cv2.resize(display_frame, CAMERA_RESOLUTION)
    display_frame = correct_white_balance(display_frame)
    display_frame = adaptive_brighten_image(display_frame, base_brightness=BRIGHTNESS_ADJUSTMENT)
    
    # Draw visualization on unmirrored display
    for row in range(3):
        for col in range(3):
            x = start_x + col * GRID_STEP + GRID_STEP // 2
            y = start_y + row * GRID_STEP + GRID_STEP // 2
            
            # Get color from mirrored detection (flip column index)
            mirrored_col = 2 - col
            color_idx = row * 3 + mirrored_col
            color_name = colors[color_idx]
            
            # Get patch for visualization
            patch = display_frame[y-DETECTION_SIZE:y+DETECTION_SIZE, x-DETECTION_SIZE:x+DETECTION_SIZE]
            dom_color = get_dominant_color(patch)

            # Draw visualization
            cv2.rectangle(display_frame, (x-DETECTION_SIZE, y-DETECTION_SIZE), (x+DETECTION_SIZE, y+DETECTION_SIZE),
                          (int(dom_color[0]), int(dom_color[1]), int(dom_color[2])), -1)
            
            display_label = color_name[:3] if color_name != "Unknown" else "?"
            cv2.putText(display_frame, display_label, (x-12, y+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.putText(display_frame, "Captured (Unmirrored)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Cube Face Capture", display_frame)
    cv2.waitKey(2000)
    
    # Return colors in unmirrored order
    unmirrored_colors = []
    for row in range(3):
        for col in range(3):
            mirrored_col = 2 - col
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
                    
                    try:
                        color_num = int(color_input)
                        if 1 <= color_num <= len(color_options):
                            new_color = color_options[color_num - 1]
                        else:
                            print("Invalid color number")
                            continue
                    except ValueError:
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