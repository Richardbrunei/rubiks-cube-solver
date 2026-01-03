"""
Test the new corner color order validation
"""

from cube_validation import validate_cube_state

print("=" * 70)
print("TEST: Corner Color Order Validation")
print("=" * 70)

# Test 1: Valid solved cube
print("\n1. Valid Solved Cube")
print("-" * 70)
valid_cube = ["White"] * 9 + ["Red"] * 9 + ["Green"] * 9 + \
             ["Yellow"] * 9 + ["Orange"] * 9 + ["Blue"] * 9

is_valid, analysis = validate_cube_state(valid_cube, debug=False, show_analysis=True)
print(f"Valid: {is_valid}")
print(f"Analysis: {analysis}")
assert is_valid == True, "Valid cube should pass"
print("✅ PASS")

# Test 2: Cube with swapped corner colors (from image)
print("\n2. Cube with Swapped Corner Colors")
print("-" * 70)
swapped_corner_cube = [
    # White face
    "White", "White", "White",
    "White", "White", "White",
    "White", "White", "White",
    
    # Red face - has green in position 9 (top-left corner)
    "Green", "Red", "Red",
    "Red", "Red", "Red",
    "Red", "Red", "Red",
    
    # Green face - has red in position 20 (top-right corner)
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

is_valid, analysis = validate_cube_state(swapped_corner_cube, debug=False, show_analysis=True)
print(f"Valid: {is_valid}")
print(f"Analysis: {analysis}")
assert is_valid == False, "Cube with swapped corners should fail"
assert "swapped" in analysis.lower() or "wrong colors" in analysis.lower(), "Should mention swapped/wrong colors"
print("✅ PASS")

# Test 3: Another swapped corner scenario
print("\n3. Different Swapped Corner")
print("-" * 70)
another_swap = [
    # White face - swap orange and blue at corner 0
    "White", "White", "White",
    "White", "White", "White",
    "White", "White", "White",
    
    # Red face
    "Red", "Red", "Red",
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
    
    # Orange face - position 36 should be Orange but we'll put Blue
    "Blue", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    
    # Blue face - position 47 should be Blue but we'll put Orange
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
    "Blue", "Orange", "Blue",
]

is_valid, analysis = validate_cube_state(another_swap, debug=False, show_analysis=True)
print(f"Valid: {is_valid}")
print(f"Analysis: {analysis}")
assert is_valid == False, "Cube with swapped corners should fail"
print("✅ PASS")

print("\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nThe validation now correctly detects:")
print("  ✅ Swapped corner colors")
print("  ✅ Wrong corner color combinations")
print("  ✅ Maintains validation for correct cubes")
