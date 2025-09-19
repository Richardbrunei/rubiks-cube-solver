"""
Display and printing functions for Rubik's Cube Color Detection System
"""


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


def print_validation_results(is_valid):
    """
    Print cube validation results in a user-friendly format.
    
    Args:
        is_valid: Boolean result from validate_cube_state()
    """
    print("\n" + "="*50)
    print("CUBE VALIDATION RESULTS")
    print("="*50)
    
    if is_valid:
        print("✅ CUBE IS VALID!")
        print("The detected cube configuration follows Rubik's cube rules.")
        print("\n🎉 Perfect! Cube is ready for solving.")
    else:
        print("❌ CUBE IS INVALID!")
        print("The detected cube configuration has errors.")
        print("This could be due to:")
        print("  • Incorrect color detection")
        print("  • Physical cube assembly issues")
        print("  • Impossible cube configuration")
    
    print("="*50)