"""
Rubik's Cube Color Detection System - Main Program

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
#This is just a test
import cv2
import kociemba

# Import from our custom modules
from config import COLOR_TO_CUBE
from camera_interface import show_live_preview, capture_face, edit_face_colors
from cube_validation import validate_cube_state, fix_cube_complete
from cube_display import print_cube_net, print_validation_results


def main():
    """
    Main program function that orchestrates the entire cube detection process.
    
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
        
        fixed_cube_state, face_mapping, rotations_applied, is_valid = fix_cube_complete(cube_state)
        
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
        print(f"{status} Final result: {'VALID CUBE!' if is_valid else 'Could not create valid cube - best attempt returned'}")
        
        print("="*60)
    
    # Final validation after all fixes
    if len(cube_state) == 54:
        print("\n" + "="*60)
        print("FINAL CUBE VALIDATION")
        print("="*60)
        
        is_valid = validate_cube_state(cube_state)
        print_validation_results(is_valid)
        
        if is_valid:
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