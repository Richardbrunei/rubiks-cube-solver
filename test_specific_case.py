"""
Test the specific case from the image where validation incorrectly passes
"""

from cube_validation import validate_cube_state

# Based on the image:
# White face: all white (top, empty in image)
# Orange face (left): all orange
# Green face (front): has 1 red in top-right position
# Red face (right): has 1 green in top-left position  
# Blue face (back): all blue
# Yellow face (bottom): all yellow

cube_from_image = [
    # White face (0-8) - all white
    "White", "White", "White",
    "White", "White", "White",
    "White", "White", "White",
    
    # Red face (9-17) - has green in position 9 (top-left)
    "Green", "Red", "Red",
    "Red", "Red", "Red",
    "Red", "Red", "Red",
    
    # Green face (18-26) - has red in position 20 (top-right)
    "Green", "Green", "Red",
    "Green", "Green", "Green",
    "Green", "Green", "Green",
    
    # Yellow face (27-35) - all yellow
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    
    # Orange face (36-44) - all orange
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    
    # Blue face (45-53) - all blue
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
]

print("Testing cube from image...")
print("=" * 70)

# Test with debug to see what's happening
print("\nWith debug=True:")
is_valid_debug = validate_cube_state(cube_from_image, debug=True, show_analysis=False)
print(f"\nResult: {is_valid_debug}")

print("\n" + "=" * 70)
print("\nWith show_analysis=True:")
is_valid, analysis = validate_cube_state(cube_from_image, debug=False, show_analysis=True)
print(f"Valid: {is_valid}")
print(f"Analysis: {analysis}")

print("\n" + "=" * 70)
print("\nExpected Issues:")
print("1. This cube has a swapped edge piece (Green-Red)")
print("2. The Green-Red edge appears in two places:")
print("   - Position 9 (Red face top-left) + Position 20 (Green face top-right)")
print("3. This should be detected as a duplicate edge")
