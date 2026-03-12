"""
Test that scrambled cubes with valid orientations pass validation
This verifies that corner rotation check doesn't require corners to be in solved positions
"""

from cube_validation import validate_cube_state

print("=" * 70)
print("TEST: Scrambled Cube Validation")
print("=" * 70)
print("\nThis test verifies that a scrambled cube (corners not in solved")
print("positions) can still be valid as long as orientations are correct.")

# Create a scrambled but valid cube
# This cube has corners in different positions than a solved cube,
# but all orientations are correct (white/yellow on U/D faces)
scrambled_valid_cube = [
    # White face - corners scrambled but white stickers on top
    "White", "White", "White",
    "White", "White", "White",
    "White", "White", "White",
    
    # Red face
    "Red", "Red", "Blue",      # Mixed corner colors
    "Red", "Red", "Red",
    "Green", "Red", "Red",
    
    # Green face
    "Green", "Green", "Red",
    "Green", "Green", "Green",
    "Blue", "Green", "Orange",
    
    # Yellow face - corners scrambled but yellow stickers on bottom
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    "Yellow", "Yellow", "Yellow",
    
    # Orange face
    "Orange", "Orange", "Green",
    "Orange", "Orange", "Orange",
    "Red", "Orange", "Blue",
    
    # Blue face
    "Blue", "Blue", "Orange",
    "Blue", "Blue", "Blue",
    "Orange", "Blue", "Green",
]

print("\n" + "-" * 70)
print("Test 1: Scrambled cube with correct orientations")
print("-" * 70)

is_valid, analysis = validate_cube_state(scrambled_valid_cube, debug=True, show_analysis=True)

print("\n" + "=" * 70)
print(f"Result: {'VALID' if is_valid else 'INVALID'}")
if not is_valid:
    print(f"Analysis: {analysis}")
print("=" * 70)

if is_valid:
    print("\n✅ SUCCESS: Scrambled cube with correct orientations is valid!")
    print("   Corner rotation check correctly ignores corner positions.")
else:
    print("\n❌ FAILURE: Scrambled cube should be valid!")
    print("   The validation is incorrectly checking corner positions.")

# Test 2: Create a cube with wrong orientations (twisted corners)
print("\n\n" + "-" * 70)
print("Test 2: Cube with twisted corners (invalid orientations)")
print("-" * 70)

twisted_cube = [
    # White face - one corner has white on side instead of top (twisted)
    "Orange", "White", "White",  # First corner twisted
    "White", "White", "White",
    "White", "White", "White",
    
    # Red face
    "White", "Red", "Red",  # White from twisted corner
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
    
    # Orange face
    "Blue", "Orange", "Orange",  # Blue from twisted corner
    "Orange", "Orange", "Orange",
    "Orange", "Orange", "Orange",
    
    # Blue face
    "Orange", "Blue", "Blue",  # Orange from twisted corner
    "Blue", "Blue", "Blue",
    "Blue", "Blue", "Blue",
]

is_valid2, analysis2 = validate_cube_state(twisted_cube, debug=False, show_analysis=True)

print(f"\nResult: {'VALID' if is_valid2 else 'INVALID'}")
if not is_valid2:
    print(f"Analysis: {analysis2}")

if not is_valid2:
    print("\n✅ SUCCESS: Cube with twisted corners is correctly detected as invalid!")
else:
    print("\n❌ FAILURE: Cube with twisted corners should be invalid!")

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Test 1 (Scrambled valid): {'PASS' if is_valid else 'FAIL'}")
print(f"Test 2 (Twisted invalid): {'PASS' if not is_valid2 else 'FAIL'}")
print("\nKey Point: Corner rotation validation should check ORIENTATIONS,")
print("not POSITIONS. A scrambled cube can be valid!")
