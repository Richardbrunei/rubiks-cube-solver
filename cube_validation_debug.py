#!/usr/bin/env python3
"""
Rubik's Cube Validation Debug Tool

This tool provides detailed debugging and analysis for cube validation.
It takes a cube string as input and performs comprehensive validation checks.

Usage:
    python cube_validation_debug.py
    
Then enter a cube string when prompted, or use one of the test cases.
"""
#UUUUUUUUURRRRRRRRRFFFFFFLDFDDDFDDFLBLLLLLLDDDBBBBBBBBL

import sys
from cube_validation import (
    validate_cube_state, 
    extract_edges, 
    extract_corners,
    validate_edges,
    validate_corners,
    is_cube_theoretically_valid,
    fix_cube_complete
)


def parse_cube_string(cube_string):
    """
    Parse various cube string formats into a list of 54 colors.
    
    Supports:
    - Space-separated colors: "White Red Green ..."
    - Comma-separated colors: "White,Red,Green,..."
    - Single character codes: "WRGYOR..." (W=White, R=Red, G=Green, Y=Yellow, O=Orange, B=Blue)
    - UDLRFB notation: "UUUUUUUUUDDDDDDDDDLLLLLLLLLRRRRRRRRR..." (U=Up/White, D=Down/Yellow, L=Left/Orange, R=Right/Red, F=Front/Green, B=Back/Blue)
    """
    cube_string = cube_string.strip()
    
    # Try space-separated
    if ' ' in cube_string:
        colors = cube_string.split()
        return colors
    
    # Try comma-separated
    if ',' in cube_string:
        colors = [c.strip() for c in cube_string.split(',')]
        return colors
    
    # Try UDLRFB notation (standard cube notation)
    if len(cube_string) == 54 and all(c in 'UDLRFB' for c in cube_string.upper()):
        udlrfb_to_color = {
            'U': 'White',   # Up face
            'D': 'Yellow',  # Down face  
            'L': 'Orange',  # Left face
            'R': 'Red',     # Right face
            'F': 'Green',   # Front face
            'B': 'Blue'     # Back face
        }
        colors = [udlrfb_to_color[c.upper()] for c in cube_string]
        return colors
    
    # Try single character codes (WRGYOR)
    if len(cube_string) == 54 and all(c in 'WRGYOR' for c in cube_string.upper()):
        char_to_color = {
            'W': 'White', 'R': 'Red', 'G': 'Green', 
            'Y': 'Yellow', 'O': 'Orange', 'B': 'Blue'
        }
        colors = [char_to_color[c.upper()] for c in cube_string]
        return colors
    
    # If none of the above, assume it's already a list-like string
    # Try to evaluate it safely
    try:
        import ast
        colors = ast.literal_eval(cube_string)
        if isinstance(colors, list):
            return colors
    except:
        pass
    
    # Last resort: split by any whitespace
    colors = cube_string.split()
    return colors


def display_cube_net(cube_state):
    """Display the cube in a clean net format"""
    if len(cube_state) != 54:
        print("❌ Invalid cube state length")
        return
    
    # Extract faces
    faces = {}
    face_names = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    for i, name in enumerate(face_names):
        start_idx = i * 9
        faces[name] = cube_state[start_idx:start_idx + 9]
    
    # Color abbreviations for display
    color_abbrev = {
        'White': 'W', 'Red': 'R', 'Green': 'G', 
        'Yellow': 'Y', 'Orange': 'O', 'Blue': 'B',
        'Unknown': 'X', 'X': 'X'
    }
    
    def get_face_grid(face):
        """Convert face to 3x3 grid of abbreviations"""
        abbrevs = [color_abbrev.get(color, '?') for color in face]
        return [
            [abbrevs[0], abbrevs[1], abbrevs[2]],
            [abbrevs[3], abbrevs[4], abbrevs[5]],
            [abbrevs[6], abbrevs[7], abbrevs[8]]
        ]
    
    print("\n" + "="*60)
    print("CUBE NET VISUALIZATION")
    print("="*60)
    print("Face order: White(U), Red(R), Green(F), Yellow(D), Orange(L), Blue(B)")
    print()
    
    # Get face grids
    white_grid = get_face_grid(faces["White"])
    red_grid = get_face_grid(faces["Red"])
    green_grid = get_face_grid(faces["Green"])
    yellow_grid = get_face_grid(faces["Yellow"])
    orange_grid = get_face_grid(faces["Orange"])
    blue_grid = get_face_grid(faces["Blue"])
    
    # Display net format:
    #       W W W
    #       W W W  
    #       W W W
    # O O O R R R G G G B B B
    # O O O R R R G G G B B B
    # O O O R R R G G G B B B
    #       Y Y Y
    #       Y Y Y
    #       Y Y Y
    
    # Top face (White)
    for row in white_grid:
        print(f"      {' '.join(row)}")
    
    print()
    
    # Middle row (Orange, Red, Green, Blue)
    for i in range(3):
        line = f"{' '.join(orange_grid[i])} {' '.join(red_grid[i])} {' '.join(green_grid[i])} {' '.join(blue_grid[i])}"
        print(line)
    
    print()
    
    # Bottom face (Yellow)
    for row in yellow_grid:
        print(f"      {' '.join(row)}")


def display_cube_faces(cube_state):
    """Display the cube in a visual 3D net format with face labels"""
    if len(cube_state) != 54:
        print("❌ Invalid cube state length")
        return
    
    # Extract faces
    faces = {}
    face_names = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    for i, name in enumerate(face_names):
        start_idx = i * 9
        faces[name] = cube_state[start_idx:start_idx + 9]
    
    # Color abbreviations for display
    color_abbrev = {
        'White': 'W', 'Red': 'R', 'Green': 'G', 
        'Yellow': 'Y', 'Orange': 'O', 'Blue': 'B',
        'Unknown': 'X', 'X': 'X'
    }
    
    def format_face(face, name):
        abbrevs = [color_abbrev.get(color, '?') for color in face]
        return f"{name} face:\n{abbrevs[0]} {abbrevs[1]} {abbrevs[2]}\n{abbrevs[3]} {abbrevs[4]} {abbrevs[5]}\n{abbrevs[6]} {abbrevs[7]} {abbrevs[8]}"
    
    print("\n" + "="*60)
    print("CUBE FACES (Individual)")
    print("="*60)
    
    # Display in net format
    print("        " + format_face(faces["White"], "White").replace('\n', '\n        '))
    print()
    
    # Middle row: Orange, Red, Green, Blue
    orange_lines = format_face(faces["Orange"], "Orange").split('\n')
    red_lines = format_face(faces["Red"], "Red").split('\n')
    green_lines = format_face(faces["Green"], "Green").split('\n')
    blue_lines = format_face(faces["Blue"], "Blue").split('\n')
    
    for i in range(len(orange_lines)):
        if i == 0:
            print(f"{orange_lines[i]:<12} {red_lines[i]:<12} {green_lines[i]:<12} {blue_lines[i]}")
        else:
            print(f"{orange_lines[i]:<12} {red_lines[i]:<12} {green_lines[i]:<12} {blue_lines[i]}")
    
    print()
    print("        " + format_face(faces["Yellow"], "Yellow").replace('\n', '\n        '))


def analyze_cube_errors(cube_state):
    """Provide detailed error analysis"""
    print("\n" + "="*60)
    print("DETAILED ERROR ANALYSIS")
    print("="*60)
    
    if len(cube_state) != 54:
        print(f"❌ CRITICAL: Invalid length {len(cube_state)} (expected 54)")
        return
    
    # Color count analysis
    color_counts = {}
    for color in cube_state:
        color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    
    print("Color Distribution:")
    total_errors = 0
    for color in expected_colors:
        count = color_counts.get(color, 0)
        if count == 9:
            print(f"  ✅ {color}: {count}")
        else:
            print(f"  ❌ {color}: {count} (expected 9, difference: {count-9:+d})")
            total_errors += abs(count - 9)
    
    # Check for unknown colors
    unknown_colors = [color for color in color_counts if color not in expected_colors]
    if unknown_colors:
        print(f"  ❌ Unknown colors found: {unknown_colors}")
        total_errors += sum(color_counts[color] for color in unknown_colors)
    
    print(f"\nTotal color errors: {total_errors}")
    
    # Center analysis
    centers = [cube_state[4], cube_state[13], cube_state[22], cube_state[31], cube_state[40], cube_state[49]]
    print(f"\nCenter Analysis:")
    face_names = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    center_errors = 0
    for i, (expected, actual) in enumerate(zip(face_names, centers)):
        if expected == actual:
            print(f"  ✅ {face_names[i]} face center: {actual}")
        else:
            print(f"  ❌ {face_names[i]} face center: {actual} (expected {expected})")
            center_errors += 1
    
    print(f"Center errors: {center_errors}")
    
    # Edge analysis
    try:
        edges = extract_edges(cube_state)
        edges_valid = validate_edges(edges, debug=True)
        if not edges_valid:
            print("❌ Edge validation failed")
    except Exception as e:
        print(f"❌ Edge extraction failed: {e}")
    
    # Corner analysis
    try:
        corners = extract_corners(cube_state)
        corners_valid = validate_corners(corners, debug=True)
        if not corners_valid:
            print("❌ Corner validation failed")
    except Exception as e:
        print(f"❌ Corner extraction failed: {e}")


def suggest_fixes(cube_state):
    """Suggest possible fixes for the cube"""
    print("\n" + "="*60)
    print("FIX SUGGESTIONS")
    print("="*60)
    
    is_theoretically_valid, errors = is_cube_theoretically_valid(cube_state)
    
    if not is_theoretically_valid:
        print("❌ Cube cannot be fixed through rotation alone.")
        print("Issues that need manual correction:")
        for error in errors:
            print(f"  • {error}")
        return
    
    print("✅ Cube has correct color distribution - attempting automatic fix...")
    
    try:
        fixed_cube, face_mapping, rotations, is_valid = fix_cube_complete(cube_state)
        
        if is_valid:
            print("🎉 SUCCESS! Found a valid cube configuration:")
            print(f"Face reordering: {face_mapping}")
            print(f"Rotations applied: {rotations}")
            print("\nFixed cube string:")
            print(' '.join(fixed_cube))
            
            print("\nValidating fixed cube:")
            validate_cube_state(fixed_cube, debug=True)
        else:
            print("❌ Could not find a valid configuration through rotation.")
            print("The cube may have fundamental issues that require manual correction.")
    
    except Exception as e:
        print(f"❌ Fix attempt failed: {e}")


def get_test_cases():
    """Return some test cube strings for debugging"""
    return {
        "valid_solved": "White White White White White White White White White Red Red Red Red Red Red Red Red Red Green Green Green Green Green Green Green Green Green Yellow Yellow Yellow Yellow Yellow Yellow Yellow Yellow Yellow Orange Orange Orange Orange Orange Orange Orange Orange Orange Blue Blue Blue Blue Blue Blue Blue Blue Blue",
        
        "invalid_colors": "White White White White White White White White White Red Red Red Red Red Red Red Red Red Green Green Green Green Green Green Green Green Green Yellow Yellow Yellow Yellow Yellow Yellow Yellow Yellow Yellow Orange Orange Orange Orange Orange Orange Orange Orange Orange Purple Purple Purple Purple Purple Purple Purple Purple Purple",
        
        "wrong_centers": "Red White White White White White White White White White Red Red Red Red Red Red Red Red Green Green Green Green Green Green Green Green Green Yellow Yellow Yellow Yellow Yellow Yellow Yellow Yellow Yellow Orange Orange Orange Orange Orange Orange Orange Orange Orange Blue Blue Blue Blue Blue Blue Blue Blue Blue",
        
        "short_string": "White Red Green Yellow Orange Blue",
        
        "single_char_wrgyor": "WWWWWWWWWRRRRRRRRRGGGGGGGGGYYYYYYYYYYOOOOOOOOOBBBBBBBBBB",
        
        "udlrfb_solved": "UUUUUUUUURRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB",
        
        "udlrfb_scrambled": "UFRUFLDRUBRLBDFRLFDLUFBDLRUFDLRUBFDBUFRLBDFRULBDFRULD"
    }


def interactive_mode():
    """Run the debug tool in interactive mode"""
    print("="*60)
    print("RUBIK'S CUBE VALIDATION DEBUG TOOL")
    print("="*60)
    print()
    print("This tool analyzes cube strings and provides detailed validation feedback.")
    print()
    print("Supported formats:")
    print("1. Space-separated: 'White Red Green Yellow Orange Blue ...'")
    print("2. Comma-separated: 'White,Red,Green,Yellow,Orange,Blue,...'")
    print("3. UDLRFB notation: 'UUUUUUUUURRRRRRRRR...' (U=Up/White, D=Down/Yellow, L=Left/Orange, R=Right/Red, F=Front/Green, B=Back/Blue)")
    print("4. Single characters: 'WRGYOR...' (W=White, R=Red, G=Green, Y=Yellow, O=Orange, B=Blue)")
    print("5. Test cases: 'test1', 'test2', etc.")
    print()
    
    test_cases = get_test_cases()
    print("Available test cases:")
    for i, (name, _) in enumerate(test_cases.items(), 1):
        print(f"  test{i} - {name}")
    print()
    
    while True:
        try:
            user_input = input("Enter cube string (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Check for test cases
            if user_input.lower().startswith('test'):
                try:
                    test_num = int(user_input[4:]) if len(user_input) > 4 else 1
                    test_names = list(test_cases.keys())
                    if 1 <= test_num <= len(test_names):
                        test_name = test_names[test_num - 1]
                        cube_string = test_cases[test_name]
                        print(f"\nUsing test case '{test_name}':")
                        print(f"Cube string: {cube_string[:100]}{'...' if len(cube_string) > 100 else ''}")
                    else:
                        print(f"Invalid test number. Use test1 to test{len(test_names)}")
                        continue
                except ValueError:
                    print("Invalid test case format. Use 'test1', 'test2', etc.")
                    continue
            else:
                cube_string = user_input
            
            # Parse the cube string
            try:
                cube_state = parse_cube_string(cube_string)
                print(f"\nParsed {len(cube_state)} colors from input")
            except Exception as e:
                print(f"❌ Failed to parse cube string: {e}")
                continue
            
            # Display the cube net
            display_cube_net(cube_state)
            
            # Display individual faces
            display_cube_faces(cube_state)
            
            # Run validation with debug output
            print("\n" + "="*60)
            print("VALIDATION RESULTS")
            print("="*60)
            is_valid = validate_cube_state(cube_state, debug=True)
            
            if not is_valid:
                # Detailed error analysis
                analyze_cube_errors(cube_state)
                
                # Suggest fixes
                suggest_fixes(cube_state)
            
            print("\n" + "="*60)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode
        cube_string = ' '.join(sys.argv[1:])
        cube_state = parse_cube_string(cube_string)
        
        display_cube_net(cube_state)
        display_cube_faces(cube_state)
        is_valid = validate_cube_state(cube_state, debug=True)
        
        if not is_valid:
            analyze_cube_errors(cube_state)
            suggest_fixes(cube_state)
    else:
        # Interactive mode
        interactive_mode()