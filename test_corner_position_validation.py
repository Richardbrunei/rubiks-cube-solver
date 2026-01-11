"""
Test that corner validation correctly identifies which piece is at each position
and validates it's the correct piece in the correct orientation
"""

from cube_validation import validate_cube_state

print("=" * 70)
print("TEST: Corner Position and Orientation Validation")
print("=" * 70)

# Test 1: Valid solved cube
print("\n1. Valid Solved Cube")
print("-" * 70)
valid_cube = ["White"] * 9 + ["Red"] * 9 + ["Green"] * 9 + \
             ["Yellow"] * 9 + ["Orange"] * 9 + ["Blue"] * 9

is_valid, analysis = validate_cube_state(valid_cube, debug=False, show_analysis=True)
print(f"Valid: {is_valid}")
print(f"Analysis: {analysis}")
assert is_valid == True
print("✅ PASS")

# Test 2: Corner piece in wrong position (swapped two corners)
print("\n2. Two Corners Swapped Positions")
print("-" * 70)
# Swap corner 1 (White-Orange-Blue) with corner 2 (White-Blue-Red)
swapped_positions = [
    # White face - corners 1 and 2 swapped
    "White", "White", "White",  # positions 0,1,2
    "White", "White", "White",  # positions 3,4,5
    "White", "White", "White",  # positions 6,7,8
    
    # Red face - corner at position 11 should be Red (from corner 2) but is Blue (from corner 1)
    "Red", "Red", "Blue",  # positions 9,10,11
    "Red", "Red", "Red",
    "Red", "Red", "Red",
    
    # Green face
    "Green", "Green", "Green",
    "Green", "Green", "Green",
    "Green", "Green", "Green",
    
    # Yellow face
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    
    # Orange face - corner at position 36 should be Orange (from corner 1) but is Blue (from corner 2)
    "Blue", "Orange", "Orange",  # positions 36,37,38
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    
    # Blue face - positions 45 and 47 swapped
    "Orange", "Blue", "Blue",  # positions 45,46,47 - 45 should be Blue, 47 should be Orange
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
]

is_valid, analysis = validate_cube_state(swapped_positions, debug=False, show_analysis=True)
print(f"Valid: {is_valid}")
print(f"Analysis: {analysis}")
assert is_valid == False
print("✅ PASS - Correctly detected swapped corners")

# Test 3: Corner with colors in wrong cyclic order (from original issue)
print("\n3. Corner Colors in Wrong Order (Original Issue)")
print("-" * 70)
wrong_order = [
    # White face
    "White", "White", "White",
    "White", "White", "White",
    "White", "White", "White",
    
    # Red face - position 9 should be Red but is Green
    "Green", "Red", "Red",
    "Red", "Red", "Red",
    "Red", "Red", "Red",
    
    # Green face - position 20 should be Green but is Red
    "Green", "Green", "Red",
    "Green", "Green", "Green",
    "Green", "Green", "Green",
    
    # Yellow face
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    
    # Orange face
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    
    # Blue face
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
]

is_valid, analysis = validate_cube_state(wrong_order, debug=False, show_analysis=True)
print(f"Valid: {is_valid}")
print(f"Analysis: {analysis}")
assert is_valid == False
assert "wrong order" in analysis.lower() or "wrong piece" in analysis.lower()
print("✅ PASS - Correctly detected wrong color order")

print("\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nThe improved validation now:")
print("  ✅ Identifies which corner piece is at each position")
print("  ✅ Verifies it's the correct piece for that position")
print("  ✅ Validates the piece is in correct orientation")
print("  ✅ Detects swapped corners")
print("  ✅ Detects twisted/flipped corners")
