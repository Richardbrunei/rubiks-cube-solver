"""
Cube validation and fixing functions for Rubik's Cube Color Detection System
"""

import numpy as np
from config import COLOR_TO_CUBE


def validate_cube_state(cube_state):
    """
    Validate if the detected cube configuration is valid according to Rubik's cube rules.
    
    Checks:
    1. Exactly 9 stickers of each of the 6 colors
    2. All 12 edges are distinct and geometrically possible
    3. All 8 corners are distinct and geometrically possible
    
    Args:
        cube_state: List of 54 color names in face order [White, Red, Green, Yellow, Orange, Blue]
    
    Returns:
        dict: Validation results with 'valid' boolean and 'errors' list
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    if len(cube_state) != 54:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Invalid cube state length: {len(cube_state)} (expected 54)")
        return validation_result
    
    # Step 1: Check color count (must be exactly 9 of each color)
    color_counts = {}
    for color in cube_state:
        if color == "Unknown" or color == "X":
            validation_result['valid'] = False
            validation_result['errors'].append("Cube contains undetected colors (Unknown/X)")
            continue
        color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    for color in expected_colors:
        count = color_counts.get(color, 0)
        if count != 9:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid {color} count: {count} (expected 9)")
    
    # Check for unexpected colors
    for color in color_counts:
        if color not in expected_colors:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Unexpected color detected: {color}")
    
    # If basic color validation fails, don't continue with geometric checks
    if not validation_result['valid']:
        return validation_result
    
    # Step 2: Extract and validate edges (12 edges, each with 2 stickers)
    edges = [
        # White face edges (top face)
        (cube_state[1], cube_state[46]),   # White top - Blue top
        (cube_state[3], cube_state[37]),   # White left - Orange top  
        (cube_state[5], cube_state[19]),   # White right - Red top
        (cube_state[7], cube_state[28]),   # White bottom - Green top
        
        # Middle layer edges
        (cube_state[12], cube_state[21]),  # Red left - Green right
        (cube_state[14], cube_state[39]),  # Red right - Orange left
        (cube_state[23], cube_state[41]),  # Green left - Orange right
        (cube_state[25], cube_state[48]),  # Green right - Blue left
        
        # Yellow face edges (bottom face)
        (cube_state[30], cube_state[16]),  # Yellow top - Red bottom
        (cube_state[32], cube_state[43]),  # Yellow right - Orange bottom
        (cube_state[34], cube_state[52]),  # Yellow bottom - Blue bottom
        (cube_state[36], cube_state[25]),  # Yellow left - Green bottom
    ]
    
    # Define impossible edge combinations
    impossible_edges = set()
    
    # Same color edges are impossible
    for color in expected_colors:
        impossible_edges.add((color, color))
    
    # Opposite color edges are impossible
    opposite_pairs = [("White", "Yellow"), ("Red", "Orange"), ("Green", "Blue")]
    for color1, color2 in opposite_pairs:
        impossible_edges.add((color1, color2))
        impossible_edges.add((color2, color1))
    
    # Check edges for validity and uniqueness
    seen_edges = set()
    for i, (color1, color2) in enumerate(edges):
        edge = tuple(sorted([color1, color2]))
        
        # Check if edge is impossible
        if (color1, color2) in impossible_edges or (color2, color1) in impossible_edges:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Impossible edge {i+1}: {color1}-{color2}")
        
        # Check if edge is duplicate
        if edge in seen_edges:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Duplicate edge: {color1}-{color2}")
        else:
            seen_edges.add(edge)
    
    # Step 3: Extract and validate corners (8 corners, each with 3 stickers)
    corners = [
        # White face corners
        (cube_state[0], cube_state[36], cube_state[47]),  # White-Orange-Blue
        (cube_state[2], cube_state[18], cube_state[10]),  # White-Green-Red
        (cube_state[6], cube_state[9], cube_state[38]),   # White-Red-Orange
        (cube_state[8], cube_state[45], cube_state[20]),  # White-Blue-Green
        
        # Yellow face corners  
        (cube_state[27], cube_state[15], cube_state[24]), # Yellow-Red-Green
        (cube_state[29], cube_state[26], cube_state[42]), # Yellow-Green-Orange
        (cube_state[33], cube_state[44], cube_state[17]), # Yellow-Orange-Blue
        (cube_state[35], cube_state[51], cube_state[11]), # Yellow-Blue-Red
    ]
    
    # Check corners for validity and uniqueness
    seen_corners = set()
    for i, (color1, color2, color3) in enumerate(corners):
        corner_colors = {color1, color2, color3}
        
        # Check for impossible same-color corners
        if len(set((color1, color2, color3))) < 3:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Corner {i+1} has repeated colors: {color1}-{color2}-{color3}")
            continue
        
        # Check for impossible opposite-color combinations in corners
        for color_a, color_b in opposite_pairs:
            if color_a in corner_colors and color_b in corner_colors:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Corner {i+1} has opposite colors: {color1}-{color2}-{color3}")
                break
        
        # Normalize corner for duplicate checking (sort colors)
        normalized_corner = tuple(sorted([color1, color2, color3]))
        
        # Check if corner is duplicate
        if normalized_corner in seen_corners:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Duplicate corner: {color1}-{color2}-{color3}")
        else:
            seen_corners.add(normalized_corner)
    
    # Step 4: Check that we have exactly 12 unique edges and 8 unique corners
    if len(seen_edges) != 12:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Expected 12 unique edges, found {len(seen_edges)}")
    
    if len(seen_corners) != 8:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Expected 8 unique corners, found {len(seen_corners)}")
    
    return validation_result


def is_cube_theoretically_valid(cube_state):
    """
    Check if a cube can theoretically be made valid through rotation alone.
    
    Returns:
        tuple: (is_valid, error_reasons) where error_reasons is a list of issues
    """
    if len(cube_state) != 54:
        return False, ["Invalid cube state length"]
    
    # Check color counts
    color_counts = {}
    for color in cube_state:
        if color in ["Unknown", "X"]:
            return False, ["Contains undetected colors"]
        color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    errors = []
    
    for color in expected_colors:
        count = color_counts.get(color, 0)
        if count != 9:
            errors.append(f"Wrong {color} count: {count}")
    
    # Check for unexpected colors
    for color in color_counts:
        if color not in expected_colors:
            errors.append(f"Unexpected color: {color}")
    
    return len(errors) == 0, errors


def calculate_cube_score(cube_state):
    """
    Calculate a score (0-100) for how close the cube is to being valid.
    
    Returns:
        int: Score from 0-100, where 100 means perfectly valid
    """
    if len(cube_state) != 54:
        return 0
    
    score = 0
    
    # Color count scoring (60 points max)
    color_counts = {}
    for color in cube_state:
        if color not in ["Unknown", "X"]:
            color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    for color in expected_colors:
        count = color_counts.get(color, 0)
        # Perfect score for exactly 9, decreasing score for deviation
        color_score = max(0, 10 - abs(9 - count))
        score += color_score
    
    # Basic validation bonus (40 points)
    validation_result = validate_cube_state(cube_state)
    if validation_result['valid']:
        score += 40
    else:
        # Partial credit based on number of errors
        error_penalty = min(40, len(validation_result['errors']) * 5)
        score += max(0, 40 - error_penalty)
    
    return min(100, score)


def rotate_face_90(face):
    """
    Rotate a 3x3 face 90 degrees clockwise.
    
    Face positions:     After 90° rotation:
    0 1 2               6 3 0
    3 4 5       →       7 4 1  
    6 7 8               8 5 2
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: Rotated face
    """
    if len(face) != 9:
        return face
    
    # Mapping for 90-degree clockwise rotation
    rotation_map = [6, 3, 0, 7, 4, 1, 8, 5, 2]
    return [face[i] for i in rotation_map]


def rotate_face_180(face):
    """
    Rotate a 3x3 face 180 degrees.
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: Rotated face
    """
    # 180° = two 90° rotations
    return rotate_face_90(rotate_face_90(face))


def rotate_face_270(face):
    """
    Rotate a 3x3 face 270 degrees clockwise (or 90 degrees counter-clockwise).
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: Rotated face
    """
    # 270° = three 90° rotations
    return rotate_face_90(rotate_face_90(rotate_face_90(face)))


def get_all_face_rotations(face):
    """
    Get all 4 possible rotations of a face (0°, 90°, 180°, 270°).
    
    Args:
        face: List of 9 colors representing a 3x3 face
    
    Returns:
        list: List of 4 rotated faces [0°, 90°, 180°, 270°]
    """
    return [
        face,                    # 0° (original)
        rotate_face_90(face),    # 90°
        rotate_face_180(face),   # 180°
        rotate_face_270(face)    # 270°
    ]


def fix_cube_face_order(cube_state):
    """
    Fix cube face order by placing each face in the correct position based on center pieces.
    
    Standard cube notation expects faces in order: White, Red, Green, Yellow, Orange, Blue
    This function reorders the faces so each center piece matches its expected position.
    
    Args:
        cube_state: List of 54 colors in current face order
    
    Returns:
        tuple: (fixed_cube_state, face_mapping) where face_mapping shows the reordering
    """
    if len(cube_state) != 54:
        return cube_state, {}
    
    # Extract faces (9 stickers each)
    faces = []
    for i in range(6):
        start_idx = i * 9
        face = cube_state[start_idx:start_idx + 9]
        faces.append(face)
    
    # Get center colors (position 4 in each 3x3 face)
    center_colors = [face[4] for face in faces]
    
    # Expected face order and their center colors
    expected_order = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    
    # Create mapping from current position to correct position
    face_mapping = {}
    fixed_faces = [None] * 6
    
    for current_pos, center_color in enumerate(center_colors):
        if center_color in expected_order:
            correct_pos = expected_order.index(center_color)
            fixed_faces[correct_pos] = faces[current_pos]
            face_mapping[current_pos] = correct_pos
    
    # Handle any unmapped faces (put them in remaining slots)
    for i, face in enumerate(fixed_faces):
        if face is None:
            # Find first unmapped original face
            for orig_pos, orig_face in enumerate(faces):
                if orig_pos not in face_mapping:
                    fixed_faces[i] = orig_face
                    face_mapping[orig_pos] = i
                    break
    
    # Flatten back to single list
    fixed_cube_state = []
    for face in fixed_faces:
        if face:
            fixed_cube_state.extend(face)
        else:
            # Fallback: add placeholder if something went wrong
            fixed_cube_state.extend(["Unknown"] * 9)
    
    return fixed_cube_state, face_mapping


def fix_cube_complete(cube_state):
    """
    Complete cube fixing process: reorder faces by centers, then find optimal rotations.
    
    Two-stage process:
    1. Reorder faces based on center pieces (W=Up, Y=Down, etc.)
    2. Try all rotation combinations to find a valid cube configuration
    
    Args:
        cube_state: List of 54 colors in capture order
    
    Returns:
        tuple: (fixed_cube_state, face_reordering, rotations_applied, final_score, is_valid)
    """
    if len(cube_state) != 54:
        return cube_state, {}, [0] * 6, 0, False
    
    print("🔄 Stage 1: Reordering faces by center pieces...")
    
    # Stage 1: Reorder faces based on center pieces
    reordered_cube, face_mapping = fix_cube_face_order(cube_state)
    
    # Stage 2: Find optimal face rotations
    print("🔄 Stage 2: Finding optimal face orientations...")
    
    # Check if cube can theoretically be made valid
    is_theoretically_valid_result, theoretical_errors = is_cube_theoretically_valid(reordered_cube)
    
    if not is_theoretically_valid_result:
        print("❌ Cannot create valid cube - fundamental issues detected:")
        for error in theoretical_errors:
            print(f"   • {error}")
        return reordered_cube, face_mapping, [0] * 6, 0, False
    
    # Extract faces from reordered cube
    faces = []
    for i in range(6):
        start_idx = i * 9
        face = reordered_cube[start_idx:start_idx + 9]
        faces.append(face)
    
    # Get all possible rotations for each face
    face_rotations = [get_all_face_rotations(face) for face in faces]
    rotation_degrees = [0, 90, 180, 270]
    
    best_score = -1
    best_cube_state = reordered_cube
    best_rotations = [0] * 6
    
    # Try ALL possible rotation combinations systematically
    # 6 faces × 4 rotations each = 4^6 = 4096 total combinations
    tested_combinations = 0
    
    # Nested loops for all combinations: for white in range(4): for red in range(4): etc.
    for white_rot in range(4):      # White face: 0°, 90°, 180°, 270°
        for red_rot in range(4):    # Red face: 0°, 90°, 180°, 270°
            for green_rot in range(4):  # Green face: 0°, 90°, 180°, 270°
                for yellow_rot in range(4):  # Yellow face: 0°, 90°, 180°, 270°
                    for orange_rot in range(4):  # Orange face: 0°, 90°, 180°, 270°
                        for blue_rot in range(4):  # Blue face: 0°, 90°, 180°, 270°
                            
                            # Create test cube with this rotation combination
                            test_cube = []
                            rotations = [white_rot, red_rot, green_rot, yellow_rot, orange_rot, blue_rot]
                            
                            for face_idx, rotation_idx in enumerate(rotations):
                                rotated_face = face_rotations[face_idx][rotation_idx]
                                test_cube.extend(rotated_face)
                            
                            tested_combinations += 1
                            
                            # Check if this combination creates a valid cube
                            validation_result = validate_cube_state(test_cube)
                            if validation_result['valid']:
                                # Found perfect solution!
                                best_cube_state = test_cube
                                best_rotations = [rotation_degrees[r] for r in rotations]
                                best_score = 100
                                print(f"✅ Found valid cube after {tested_combinations} combinations!")
                                # Return immediately - we found the solution
                                final_validation = validate_cube_state(best_cube_state)
                                is_valid_solution = final_validation['valid']
                                return best_cube_state, face_mapping, best_rotations, best_score, is_valid_solution
                            
                            # Track best score for non-perfect solutions
                            score = calculate_cube_score(test_cube)
                            if score > best_score:
                                best_score = score
                                best_cube_state = test_cube
                                best_rotations = [rotation_degrees[r] for r in rotations]
                            
                            # Progress indicator for long searches
                            if tested_combinations % 1000 == 0:
                                print(f"   Tested {tested_combinations}/4096 combinations...")
    
    print(f"⚠️  Tested all {tested_combinations} combinations - no perfect solution found")
    
    # Final validation
    final_validation = validate_cube_state(best_cube_state)
    is_valid_solution = final_validation['valid']
    
    return best_cube_state, face_mapping, best_rotations, best_score, is_valid_solution