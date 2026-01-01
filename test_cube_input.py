"""
Interactive Cube Validation Tester
Allows manual input of cube strings and displays validation analysis
"""

from cube_validation import validate_cube_state

def parse_cube_string(cube_string):
    """
    Parse a cube string into a list of color names.
    Supports both single-letter notation (URFDLB) and full color names.
    """
    # Mapping from single letters to color names
    letter_to_color = {
        'U': 'White', 'W': 'White',
        'R': 'Red',
        'F': 'Green', 'G': 'Green',
        'D': 'Yellow', 'Y': 'Yellow',
        'L': 'Orange', 'O': 'Orange',
        'B': 'Blue',
        'X': 'Unknown', '?': 'Unknown'
    }
    
    # Remove spaces and convert to uppercase
    cube_string = cube_string.replace(' ', '').upper()
    
    # If it's already color names separated by commas
    if ',' in cube_string:
        colors = [c.strip().capitalize() for c in cube_string.split(',')]
        return colors
    
    # Otherwise, treat as single-letter notation
    colors = []
    for char in cube_string:
        if char in letter_to_color:
            colors.append(letter_to_color[char])
        else:
            print(f"Warning: Unknown character '{char}', treating as Unknown")
            colors.append('Unknown')
    
    return colors


def display_cube_faces(cube_state):
    """Display the cube state in a visual format"""
    if len(cube_state) != 54:
        print(f"Invalid cube state length: {len(cube_state)}")
        return
    
    face_names = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    
    print("\nCube State (by face):")
    print("=" * 60)
    
    for i, face_name in enumerate(face_names):
        start_idx = i * 9
        face = cube_state[start_idx:start_idx + 9]
        
        # Get first letter of each color for compact display
        face_letters = []
        for color in face:
            if color == "Unknown":
                face_letters.append("?")
            else:
                face_letters.append(color[0])
        
        print(f"\n{face_name} face (center should be {face_name[0]}):")
        print(f"  {face_letters[0]} {face_letters[1]} {face_letters[2]}")
        print(f"  {face_letters[3]} {face_letters[4]} {face_letters[5]}")
        print(f"  {face_letters[6]} {face_letters[7]} {face_letters[8]}")


def main():
    print("=" * 60)
    print("RUBIK'S CUBE VALIDATION TESTER")
    print("=" * 60)
    print("\nInput Format Options:")
    print("1. Single letters (54 chars): UUUUUUUUURRRRRRRRRGGGGGGGGGDDDDDDDDDLLLLLLLLLBBBBBBBBB")
    print("   U=White, R=Red, F/G=Green, D=Yellow, L/O=Orange, B=Blue")
    print("\n2. Color names (comma-separated): White,White,White,...")
    print("\n3. Type 'solved' for a solved cube")
    print("4. Type 'quit' to exit")
    print("=" * 60)
    
    # Predefined test cubes
    test_cubes = {
        'solved': 'U' * 9 + 'R' * 9 + 'F' * 9 + 'D' * 9 + 'L' * 9 + 'B' * 9,
        'invalid_colors': 'U' * 11 + 'R' * 7 + 'F' * 9 + 'D' * 9 + 'L' * 9 + 'B' * 9,
        'wrong_center': 'UUUUURUUURRRRRRRRRGGGGGGGGGDDDDDDDDDLLLLLLLLLBBBBBBBBB',
    }
    
    while True:
        print("\n" + "-" * 60)
        cube_input = input("\nEnter cube string (or 'quit'): ").strip()
        
        if cube_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        if cube_input.lower() in test_cubes:
            cube_input = test_cubes[cube_input.lower()]
            print(f"Using predefined cube: {cube_input[:20]}...")
        
        if not cube_input:
            print("Empty input. Please try again.")
            continue
        
        # Parse the input
        try:
            cube_state = parse_cube_string(cube_input)
            
            if len(cube_state) != 54:
                print(f"\n❌ Error: Expected 54 stickers, got {len(cube_state)}")
                print("Please provide exactly 54 colors/letters.")
                continue
            
            # Display the cube
            display_cube_faces(cube_state)
            
            # Validate with analysis
            print("\n" + "=" * 60)
            print("VALIDATION RESULTS")
            print("=" * 60)
            
            is_valid, message = validate_cube_state(cube_state, debug=False, show_analysis=True)
            
            if is_valid:
                print(f"\n✅ {message}")
            else:
                print(f"\n❌ {message}")
            
            # Ask if user wants detailed debug output
            show_debug = input("\nShow detailed debug output? (y/n): ").strip().lower()
            if show_debug == 'y':
                print("\n" + "=" * 60)
                print("DETAILED DEBUG OUTPUT")
                print("=" * 60)
                validate_cube_state(cube_state, debug=True, show_analysis=False)
        
        except Exception as e:
            print(f"\n❌ Error processing input: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
