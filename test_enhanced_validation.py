"""
Test script for enhanced cube validation with corner rotations,
edge parity, and permutation parity checks.
"""

from cube_validation import validate_cube_state

# Test 1: Valid solved cube
print("="*60)
print("TEST 1: Valid Solved Cube")
print("="*60)

solved_cube = [
    # White face (0-8)
    "White", "White", "White",
    "White", "White", "White",
    "White", "White", "White",
    
    # Red face (9-17)
    "Red", "Red", "Red",
    "Red", "Red", "Red",
    "Red", "Red", "Red",
    
    # Green face (18-26)
    "Green", "Green", "Green",
    "Green", "Green", "Green",
    "Green", "Green", "Green",
    
    # Yellow face (27-35)
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    
    # Orange face (36-44)
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    
    # Blue face (45-53)
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
]

result = validate_cube_state(solved_cube, debug=False)
print(f"Result: {'✅ VALID' if result else '❌ INVALID'}")

# Test 2: Invalid cube with wrong color counts
print("\n" + "="*60)
print("TEST 2: Invalid Cube - Wrong Color Counts")
print("="*60)

invalid_cube = solved_cube.copy()
invalid_cube[0] = "Red"  # Replace a white with red (10 reds, 8 whites)

result = validate_cube_state(invalid_cube, debug=False)
print(f"Result: {'✅ VALID' if result else '❌ INVALID'}")

# Test 3: Cube with single corner twist (invalid corner rotation)
print("\n" + "="*60)
print("TEST 3: Invalid Cube - Single Corner Twist")
print("="*60)
print("Cube string: UUBUUUUUURURRRRRRFFFFFFFFFDDDDDDDDLLLLLLLLLRBBBBBBBBB")
print("Note: A single corner twist creates invalid corner rotations")
print("(rotation sum not divisible by 3)")

# Convert cube notation string to color names
# U=White, R=Red, F=Green, D=Yellow, L=Orange, B=Blue
notation_to_color = {
    'U': 'White',
    'R': 'Red',
    'F': 'Green',
    'D': 'Yellow',
    'L': 'Orange',
    'B': 'Blue'
}

corner_twist_string = "UUBUUUUUURRURRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLRBBBBBBBB"
corner_twist_cube = [notation_to_color[char] for char in corner_twist_string]

result = validate_cube_state(corner_twist_cube, debug=False)
print(f"Result: {'✅ VALID' if result else '❌ INVALID'}")
print("This cube has a single corner twisted - impossible to solve!")

# Test 4: Cube with single edge flip (no corner twist)
print("\n" + "="*60)
print("TEST 4: Invalid Cube - Single Edge Flip")
print("="*60)
print("Cube string: UUUUUUUUURRRRRRRRRFFFLFFFFFDDDDDDDDDLLLLLFLLLBBBBBBBBB")
print("Note: This cube has a single flipped edge (Front-Left edge)")
print("Edge parity check should fail")

# Single edge flip - FL edge is flipped (Green-Orange edge)
# Swapped positions 21 (Green-left) and 41 (Orange-right)
edge_flip_string = "UUUUUUUUURRRRRRRRRFFFLFFFFFDDDDDDDDDLLLLLFLLLBBBBBBBBB"
edge_flip_cube = [notation_to_color[char] for char in edge_flip_string]

result = validate_cube_state(edge_flip_cube, debug=False)
print(f"Result: {'✅ VALID' if result else '❌ INVALID'}")
print("This cube has a single flipped edge - impossible to solve!")

# Test 5: Cube with both edge flip and corner twist
print("\n" + "="*60)
print("TEST 5: Invalid Cube - Edge Flip AND Corner Twist")
print("="*60)
print("Cube string: UUBUUUUUURRURRRRRRFFFLFFFFFDDDDDDDDDLLLLLFLLLRBBBBBBBB")
print("Note: This cube has both a flipped edge and a twisted corner")
print("Corner rotation check will fail first (fail-fast validation)")

both_errors_string = "UUBUUUUUURRURRRRRRFFFLFFFFFDDDDDDDDDLLLLLFLLLRBBBBBBBB"
both_errors_cube = [notation_to_color[char] for char in both_errors_string]

result = validate_cube_state(both_errors_cube, debug=False)
print(f"Result: {'✅ VALID' if result else '❌ INVALID'}")
print("This cube has BOTH errors - doubly impossible to solve!")

print("\n" + "="*60)
print("VALIDATION ENHANCEMENTS SUMMARY")
print("="*60)
print("""
The cube validation now includes three advanced checks:

1. CORNER ROTATIONS
   - Checks if corners are twisted correctly
   - Sum of all corner rotations must be divisible by 3
   - Catches single corner twists (impossible to solve)

2. EDGE PARITY
   - Checks edge piece orientations
   - Count of specific edge positions must be even
   - Catches single edge flips (impossible to solve)

3. PERMUTATION PARITY
   - Checks if pieces can be rearranged correctly
   - Total swaps needed must be even
   - Catches impossible piece arrangements

These checks ensure the cube is not just structurally valid,
but actually SOLVABLE using standard Rubik's cube algorithms!
""")
