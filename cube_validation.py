"""
Cube validation and fixing functions for Rubik's Cube Color Detection System
"""

import numpy as np
from config import COLOR_TO_CUBE


def validate_cube_state(cube_state, debug=False, show_analysis=False):
    """
    Validate cube state with clear step-by-step validation and debugging output.
    
    Face order: White(0-8), Red(9-17), Green(18-26), Yellow(27-35), Orange(36-44), Blue(45-53)
    
    Each face layout with indices:
    White face:    Red face:      Green face:    Yellow face:   Orange face:   Blue face:
    0  1  2        9  10 11      18 19 20       27 28 29       36 37 38       45 46 47
    3  4  5        12 13 14      21 22 23       30 31 32       39 40 41       48 49 50
    6  7  8        15 16 17      24 25 26       33 34 35       42 43 44       51 52 53
    
    Center positions: White(4), Red(13), Green(22), Yellow(31), Orange(40), Blue(49)
    Edge positions: 1,3,5,7 for each face
    Corner positions: 0,2,6,8 for each face
    
    Args:
        cube_state: List of 54 color names in face order [White, Red, Green, Yellow, Orange, Blue]
        debug: If True, print debugging information
        show_analysis: If True, return tuple (is_valid, analysis_string) instead of just bool
    
    Returns:
        bool or tuple: 
            - If show_analysis=False: True if valid, False if invalid
            - If show_analysis=True: (is_valid, analysis_string)
    """
    analysis_lines = []
    
    if debug:
        print("="*60)
        print("CUBE VALIDATION DEBUG")
        print("="*60)
    
    # Step 1: Check cube length
    if len(cube_state) != 54:
        msg = f"Invalid length: {len(cube_state)} (expected 54)"
        if debug:
            print(f"❌ {msg}")
        if show_analysis:
            analysis_lines.append(msg)
            return False, "\n".join(analysis_lines)
        return False
    
    if debug:
        print(f"✅ Length check: {len(cube_state)} stickers")
    
    # Step 2: Check color counts
    color_counts = {}
    for color in cube_state:
        if color == "Unknown" or color == "X":
            msg = "Contains unknown colors"
            if debug:
                print(f"❌ {msg}")
            if show_analysis:
                analysis_lines.append(msg)
                return False, "\n".join(analysis_lines)
            return False
        color_counts[color] = color_counts.get(color, 0) + 1
    
    expected_colors = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
    
    if debug:
        print(f"\nColor counts:")
        for color in expected_colors:
            count = color_counts.get(color, 0)
            status = "✅" if count == 9 else "❌"
            print(f"  {status} {color}: {count}")
    
    # Validate color counts
    color_errors = []
    for color in expected_colors:
        count = color_counts.get(color, 0)
        if count != 9:
            color_errors.append(f"{color}: {count}")
    
    # Check for unexpected colors
    for color in color_counts:
        if color not in expected_colors:
            msg = f"Unexpected color: {color}"
            if debug:
                print(f"❌ {msg}")
            if show_analysis:
                analysis_lines.append(msg)
                return False, "\n".join(analysis_lines)
            return False
    
    if color_errors:
        msg = f"Wrong color counts: {', '.join(color_errors)} (expected 9 each)"
        if debug:
            print(f"❌ {msg}")
        if show_analysis:
            analysis_lines.append(msg)
            return False, "\n".join(analysis_lines)
        return False
    
    # Step 3: Check center pieces
    centers = [
        cube_state[4],   # White center
        cube_state[13],  # Red center
        cube_state[22],  # Green center
        cube_state[31],  # Yellow center
        cube_state[40],  # Orange center
        cube_state[49],  # Blue center
    ]
    
    if debug:
        print(f"\nCenter pieces:")
        face_names = ["White", "Red", "Green", "Yellow", "Orange", "Blue"]
        for i, (expected, actual) in enumerate(zip(face_names, centers)):
            status = "✅" if expected == actual else "❌"
            print(f"  {status} {face_names[i]} face center: {actual}")
    
    # Validate centers (each face should have its own color as center)
    center_errors = []
    for i, (expected, actual) in enumerate(zip(expected_colors, centers)):
        if expected != actual:
            center_errors.append(f"{expected} face has {actual}")
    
    if center_errors:
        msg = f"Wrong centers: {', '.join(center_errors)}"
        if debug:
            print(f"❌ {msg}")
        if show_analysis:
            analysis_lines.append(msg)
            return False, "\n".join(analysis_lines)
        return False
    
    # Step 4: Extract and validate edges
    edges = extract_edges(cube_state)
    
    if debug:
        print(f"\nEdges array ({len(edges)} edges):")
        for i, (color1, color2) in enumerate(edges):
            print(f"  {i+1:2d}. {color1} - {color2}")
    
    edges_valid, edge_error = validate_edges(edges, debug, show_analysis)
    if not edges_valid:
        if show_analysis:
            analysis_lines.append(edge_error)
            return False, "\n".join(analysis_lines)
        return False
    
    # Step 5: Extract and validate corners
    corners = extract_corners(cube_state)
    
    if debug:
        print(f"\nCorners array ({len(corners)} corners):")
        for i, (color1, color2, color3) in enumerate(corners):
            print(f"  {i+1}. {color1} - {color2} - {color3}")
    
    corners_valid, corner_error = validate_corners(corners, debug, show_analysis)
    if not corners_valid:
        if show_analysis:
            analysis_lines.append(corner_error)
            return False, "\n".join(analysis_lines)
        return False
    
    # Step 6: Check corner rotations (sum must be divisible by 3)
    corner_rotation_valid, rotation_error = validate_corner_rotations(cube_state, debug, show_analysis)
    if not corner_rotation_valid:
        if show_analysis:
            analysis_lines.append(rotation_error)
            return False, "\n".join(analysis_lines)
        return False
    
    # Step 7: Check edge parity (must be even)
    edge_parity_valid, parity_error = validate_edge_parity(cube_state, debug, show_analysis)
    if not edge_parity_valid:
        if show_analysis:
            analysis_lines.append(parity_error)
            return False, "\n".join(analysis_lines)
        return False
    
    # Step 8: Check permutation parity (total swaps must be even)
    permutation_valid, permutation_error = validate_permutation_parity(cube_state, debug, show_analysis)
    if not permutation_valid:
        if show_analysis:
            analysis_lines.append(permutation_error)
            return False, "\n".join(analysis_lines)
        return False
    
    if debug:
        print(f"\n✅ CUBE IS VALID!")
    if show_analysis:
        analysis_lines.append("Cube is valid")
        return True, "\n".join(analysis_lines)
    
    return True


def extract_edges(cube_state):
    """
    Extract all 12 edges from cube state with correct position mapping.
    
    In a standard cube net layout:
         U U U
         U U U
         U U U
    L L L F F F R R R B B B
    L L L F F F R R R B B B  
    L L L F F F R R R B B B
         D D D
         D D D
         D D D
    
    Face order: White(0-8), Red(9-17), Green(18-26), Yellow(27-35), Orange(36-44), Blue(45-53)
    """
    
    edges = [
        # Top layer edges (White face connects to adjacent faces)
        (cube_state[1], cube_state[46]),   # White-top connects to Blue-top (1-46)
        (cube_state[3], cube_state[37]),   # White-left connects to Orange-top (3-37)
        (cube_state[5], cube_state[10]),   # White-right connects to Red-top (5-10)
        (cube_state[7], cube_state[19]),   # White-bottom connects to Green-top (7-19)
        
        # Middle layer edges (connecting side faces in cycle: Red→Green→Orange→Blue→Red)
        (cube_state[12], cube_state[23]),  # Red-left connects to Green-right (12-23)
        (cube_state[50], cube_state[39]),  # Blue-right connects to Orange-left (50-39) (this has not been removed yet)
        (cube_state[21], cube_state[41]),  # Green-left connects to Orange-right (21-41)
        (cube_state[14], cube_state[48]),  # red-right connects to Blue-left (14-48)
        
        # Bottom layer edges (Yellow face connects to adjacent faces)
        (cube_state[28], cube_state[25]),  # Yellow-top connects to green-bottom (28-16)
        (cube_state[30], cube_state[43]),  # Yellow-left connects to orange-bottom (30-24)
        (cube_state[32], cube_state[16]),  # Yellow-right connects to red-bottom (32-43)
        (cube_state[34], cube_state[52]),  # Yellow-bottom connects to Blue-bottom (34-52)
    ]
    
    return edges


def extract_corners(cube_state):
    """Extract all 8 corners from cube state"""
    # Each corner connects 3 faces at positions 0,2,6,8 of each face
    
    corners = [
        # White face corners
        (cube_state[0], cube_state[36], cube_state[47]),  # White-topleft, Orange-topleft, Blue-topright
        (cube_state[2], cube_state[45], cube_state[11]),  # White-topright, Blue-topleft, Red-topright
        (cube_state[6], cube_state[38], cube_state[18]),  # White-bottomleft, Orange-topright, Green-topleft
        (cube_state[8], cube_state[20], cube_state[9]),   # White-bottomright, Green-topright, Red-topleft
        
        # Yellow face corners
        (cube_state[27], cube_state[24], cube_state[44]), # Yellow-topleft, Green-bottomleft, Orange-bottomright
        (cube_state[29], cube_state[26], cube_state[15]), # Yellow-topright, Green-bottomright, Red-bottomleft
        (cube_state[33], cube_state[42], cube_state[53]), # Yellow-bottomleft, Orange-bottomleft, Blue-bottomright
        (cube_state[35], cube_state[51], cube_state[17]), # Yellow-bottomright, Blue-bottomleft, Red-bottomright
    ]
    
    return corners


def validate_edges(edges, debug=False, show_analysis=False):
    """Validate that edges are geometrically possible and unique"""
    
    if debug:
        print(f"\nEdge validation:")
    
    # Define impossible edge combinations (opposite faces can't share an edge)
    opposite_pairs = [("White", "Yellow"), ("Red", "Orange"), ("Green", "Blue")]
    impossible_edges = set()
    for color1, color2 in opposite_pairs:
        impossible_edges.add((color1, color2))
        impossible_edges.add((color2, color1))
    
    # Check each edge
    seen_edges = set()
    for i, (color1, color2) in enumerate(edges):
        # Check for same color edges (impossible)
        if color1 == color2:
            msg = f"Edge {i+1} has same color: {color1}"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
        
        # Check for impossible edges (opposite colors)
        if (color1, color2) in impossible_edges:
            msg = f"Edge {i+1} has opposite colors: {color1}-{color2}"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
        
        # Check for duplicate edges
        edge = tuple(sorted([color1, color2]))
        if edge in seen_edges:
            msg = f"Duplicate edge {i+1}: {color1}-{color2}"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
        seen_edges.add(edge)
    
    # Must have exactly 12 unique edges
    if len(seen_edges) != 12:
        msg = f"Expected 12 unique edges, found {len(seen_edges)}"
        if debug:
            print(f"  ❌ {msg}")
        if show_analysis:
            return False, msg
        return False, None
    
    if debug:
        print(f"  ✅ All {len(edges)} edges are valid and unique")
    
    return True, None


def validate_corners(corners, debug=False, show_analysis=False):
    """Validate that corners are geometrically possible and unique"""
    
    if debug:
        print(f"\nCorner validation:")
    
    # Define impossible corner combinations
    opposite_pairs = [("White", "Yellow"), ("Red", "Orange"), ("Green", "Blue")]
    
    # Check each corner
    seen_corners = set()
    for i, (color1, color2, color3) in enumerate(corners):
        corner_colors = {color1, color2, color3}
        
        # Check for repeated colors in corner (impossible - each corner must have 3 different colors)
        if len(corner_colors) < 3:
            msg = f"Corner {i+1} has repeated colors: {color1}-{color2}-{color3}"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
        
        # Check for opposite colors in same corner (impossible in physical cube)
        for opp1, opp2 in opposite_pairs:
            if opp1 in corner_colors and opp2 in corner_colors:
                msg = f"Corner {i+1} has opposite colors: {color1}-{color2}-{color3}"
                if debug:
                    print(f"  ❌ {msg}")
                if show_analysis:
                    return False, msg
                return False, None
        
        # Check for duplicate corners
        corner = tuple(sorted([color1, color2, color3]))
        if corner in seen_corners:
            msg = f"Duplicate corner {i+1}: {color1}-{color2}-{color3}"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
        seen_corners.add(corner)
    
    # Must have exactly 8 unique corners
    if len(seen_corners) != 8:
        msg = f"Expected 8 unique corners, found {len(seen_corners)}"
        if debug:
            print(f"  ❌ {msg}")
        if show_analysis:
            return False, msg
        return False, None
    
    if debug:
        print(f"  ✅ All {len(corners)} corners are valid and unique")
    
    return True, None


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


def count_validation_errors(cube_state):
    """
    Count the number of validation errors in a cube state.
    Used to find the "least bad" configuration when no perfect solution exists.
    
    Returns:
        int: Number of validation errors (lower is better)
    """
    if len(cube_state) != 54:
        return 999  # Very high error count for invalid length
    
    # Simple scoring: valid = 0 errors, invalid = 1 error
    # For more granular scoring, we could check individual aspects
    return 0 if validate_cube_state(cube_state) else 1


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
    Simplified cube fixing: try all 4096 rotation combinations and return first valid one.
    
    Args:
        cube_state: List of 54 colors in capture order
    
    Returns:
        tuple: (fixed_cube_state, face_mapping, rotations_applied, is_valid)
    """
    if len(cube_state) != 54:
        return cube_state, {}, [0] * 6, False
    
    print("🔄 Stage 1: Reordering faces by center pieces...")
    
    # Stage 1: Reorder faces based on center pieces
    reordered_cube, face_mapping = fix_cube_face_order(cube_state)
    
    # Stage 2: Try all rotation combinations
    print("🔄 Stage 2: Testing all rotation combinations...")
    
    # Check if cube can theoretically be made valid
    is_theoretically_valid_result, theoretical_errors = is_cube_theoretically_valid(reordered_cube)
    
    if not is_theoretically_valid_result:
        print("❌ Cannot create valid cube - fundamental issues detected:")
        for error in theoretical_errors:
            print(f"   • {error}")
        return reordered_cube, face_mapping, [0] * 6, False
    
    # Extract faces from reordered cube
    faces = []
    for i in range(6):
        start_idx = i * 9
        face = reordered_cube[start_idx:start_idx + 9]
        faces.append(face)
    
    # Get all possible rotations for each face
    face_rotations = [get_all_face_rotations(face) for face in faces]
    rotation_degrees = [0, 90, 180, 270]
    
    tested_combinations = 0
    
    # Try all 4096 combinations - return first valid one
    for white_rot in range(4):
        for red_rot in range(4):
            for green_rot in range(4):
                for yellow_rot in range(4):
                    for orange_rot in range(4):
                        for blue_rot in range(4):
                            
                            # Create test cube with this rotation combination
                            test_cube = []
                            rotations = [white_rot, red_rot, green_rot, yellow_rot, orange_rot, blue_rot]
                            
                            for face_idx, rotation_idx in enumerate(rotations):
                                rotated_face = face_rotations[face_idx][rotation_idx]
                                test_cube.extend(rotated_face)
                            
                            tested_combinations += 1
                            
                            # Check if this combination creates a valid cube
                            if validate_cube_state(test_cube):
                                # Found valid solution!
                                applied_rotations = [rotation_degrees[r] for r in rotations]
                                print(f"✅ Found valid cube after {tested_combinations} combinations!")
                                return test_cube, face_mapping, applied_rotations, True
                            
                            # Progress indicator
                            if tested_combinations % 1000 == 0:
                                print(f"   Tested {tested_combinations}/4096 combinations...")
    
    print(f"⚠️  Tested all {tested_combinations} combinations - no valid solution found")
    
    # Return original reordered cube if no solution found
    return reordered_cube, face_mapping, [0] * 6, False



def validate_corner_rotations(cube_state, debug=False, show_analysis=False):
    """
    Validate corner rotations using the white/yellow face method.
    
    Each corner has a rotation value:
    - 0: White or yellow square is on the white or yellow face (correct orientation)
    - 1: White or yellow square is rotated clockwise from the face
    - -1: White or yellow square is rotated counter-clockwise from the face
    
    The sum of all 8 corner rotations must be divisible by 3.
    
    Args:
        cube_state: List of 54 color names
        debug: If True, print debugging information
        show_analysis: If True, return error message
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if debug:
        print(f"\nCorner rotation check:")
    
    # Define the 8 corner positions with their 3 stickers each
    # Format: (position_index, expected_face_if_rotation_0)
    corners_positions = [
        # White face corners (positions 0, 2, 6, 8)
        [(0, "White"), (36, "Orange"), (47, "Blue")],      # White-Orange-Blue
        [(2, "White"), (45, "Blue"), (11, "Red")],         # White-Blue-Red
        [(6, "White"), (18, "Green"), (38, "Orange")],     # White-Orange-Green
        [(8, "White"), (9, "Red"), (20, "Green")],         # White-Green-Red
        
        # Yellow face corners (positions 27, 29, 33, 35)
        [(27, "Yellow"), (24, "Green"), (44, "Orange")],   # Yellow-Green-Orange
        [(29, "Yellow"), (15, "Red"), (26, "Green")],      # Yellow-Green-Red
        [(33, "Yellow"), (42, "Orange"), (53, "Blue")],    # Yellow-Orange-Blue
        [(35, "Yellow"), (51, "Blue"), (17, "Red")],       # Yellow-Blue-Red
    ]
    
    rotation_sum = 0
    
    for i, corner in enumerate(corners_positions):
        # Get the actual colors at these positions
        colors = [cube_state[pos] for pos, _ in corner]
        
        # Find where white or yellow is located
        white_yellow_pos = None
        for j, color in enumerate(colors):
            if color in ["White", "Yellow"]:
                white_yellow_pos = j
                break
        
        if white_yellow_pos is None:
            msg = f"Corner {i+1} missing white/yellow"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
        
        # Calculate rotation value
        # Position 0 = correct orientation (rotation 0)
        # Position 1 = clockwise rotation (rotation 1)
        # Position 2 = counter-clockwise rotation (rotation -1)
        if white_yellow_pos == 0:
            rotation = 0
        elif white_yellow_pos == 1:
            rotation = 1
        else:  # white_yellow_pos == 2
            rotation = -1
        
        rotation_sum += rotation
        
        if debug:
            rotation_name = ["correct", "clockwise", "counter-clockwise"][white_yellow_pos]
            print(f"  Corner {i+1}: {colors} - {rotation_name} (rotation: {rotation})")
    
    is_valid = (rotation_sum % 3) == 0
    
    if debug:
        print(f"  Total rotation sum: {rotation_sum}")
        print(f"  Divisible by 3: {is_valid}")
        if is_valid:
            print(f"  ✅ Corner rotations are valid")
        else:
            print(f"  ❌ Corner rotations are invalid (sum must be divisible by 3)")
    
    if not is_valid:
        msg = f"Corner rotation sum {rotation_sum} not divisible by 3"
        if show_analysis:
            return False, msg
        return False, None
    
    return True, None


def validate_edge_parity(cube_state, debug=False, show_analysis=False):
    """
    Validate edge parity by checking edge orientations.
    
    For each edge, check if it's correctly oriented:
    - Edges with White/Yellow: White or Yellow should be on U/D face (first position)
    - Edges with Red/Orange (no W/Y): Red or Orange should be on L/R face
    
    Count flipped edges. Must be even for valid parity.
    
    Args:
        cube_state: List of 54 color names
        debug: If True, print debugging information
        show_analysis: If True, return error message
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if debug:
        print(f"\nEdge parity check:")
    
    # Extract edges using existing function - matches extract_edges() order
    edges = extract_edges(cube_state)
    
    # Define orientation rules matching extract_edges order
    # Format: (edge_index, pos1, pos2, description, check_type)
    edge_rules = [
        # Top layer (White face) - White/Yellow should be on first position
        (0, 1, 46, "White-Blue", "UD"),
        (1, 3, 37, "White-Orange", "UD"),
        (2, 5, 10, "White-Red", "UD"),
        (3, 7, 19, "White-Green", "UD"),
        
        # Middle layer - Red/Orange should be on Red/Orange face
        (4, 12, 23, "Red-Green", "LR"),
        (5, 50, 39, "Blue-Orange", "LR"),
        (6, 21, 41, "Green-Orange", "LR"),
        (7, 14, 48, "Red-Blue", "LR"),
        
        # Bottom layer (Yellow face) - White/Yellow should be on first position
        (8, 28, 25, "Yellow-Green", "UD"),
        (9, 30, 43, "Yellow-Orange", "UD"),
        (10, 32, 16, "Yellow-Red", "UD"),
        (11, 34, 52, "Yellow-Blue", "UD"),
    ]
    
    flipped_edges = 0
    
    for edge_idx, pos1, pos2, desc, check_type in edge_rules:
        color1, color2 = edges[edge_idx]
        is_correct = False
        
        if check_type == "UD":
            # White or Yellow should be on U/D face (first position)
            if color1 in ["White", "Yellow"]:
                is_correct = True
        elif check_type == "LR":
            # Red or Orange should be on L/R face
            if pos1 in [12, 14, 16] and color1 == "Red":  # Red face
                is_correct = True
            elif pos1 in [39, 41, 43] and color1 == "Orange":  # Orange face
                is_correct = True
            elif pos2 in [12, 14, 16] and color2 == "Red":  # Red face
                is_correct = True
            elif pos2 in [39, 41, 43] and color2 == "Orange":  # Orange face
                is_correct = True
        
        if not is_correct:
            flipped_edges += 1
            if debug:
                print(f"  ✗ Edge {edge_idx+1} ({desc}): {color1}-{color2} - FLIPPED")
        else:
            if debug:
                print(f"  ✓ Edge {edge_idx+1} ({desc}): {color1}-{color2} - correct")
    
    is_valid = (flipped_edges % 2) == 0
    
    if debug:
        print(f"  Flipped edges: {flipped_edges}")
        print(f"  Parity: {'even' if is_valid else 'odd'}")
        if is_valid:
            print(f"  ✅ Edge parity is valid (even)")
        else:
            print(f"  ❌ Edge parity is invalid (must be even)")
    
    if not is_valid:
        msg = f"Edge parity invalid: {flipped_edges} flipped edges (must be even)"
        if show_analysis:
            return False, msg
        return False, None
    
    return True, None


def validate_permutation_parity(cube_state, debug=False, show_analysis=False):
    """
    Validate permutation parity by counting swaps needed to solve.
    
    Counts the number of swaps needed to place all pieces in their correct
    positions. The total number of swaps for both edges and corners must be even.
    
    Args:
        cube_state: List of 54 color names
        debug: If True, print debugging information
        show_analysis: If True, return error message
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if debug:
        print(f"\nPermutation parity check:")
    
    # Use existing extract_corners function
    corners = extract_corners(cube_state)
    
    # Define what each corner position should contain (in order)
    expected_corners = [
        tuple(sorted(["White", "Orange", "Blue"])),
        tuple(sorted(["White", "Blue", "Red"])),
        tuple(sorted(["White", "Orange", "Green"])),
        tuple(sorted(["White", "Green", "Red"])),
        tuple(sorted(["Yellow", "Green", "Orange"])),
        tuple(sorted(["Yellow", "Green", "Red"])),
        tuple(sorted(["Yellow", "Orange", "Blue"])),
        tuple(sorted(["Yellow", "Blue", "Red"])),
    ]
    
    # Create mapping: which piece should be in which position
    corner_mapping = []
    for corner in corners:
        corner_sorted = tuple(sorted(corner))
        try:
            correct_pos = expected_corners.index(corner_sorted)
            corner_mapping.append(correct_pos)
        except ValueError:
            msg = f"Invalid corner piece: {corner}"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
    
    # Count swaps for corners
    corner_swaps = count_swaps(corner_mapping.copy())
    
    if debug:
        print(f"  Corner swaps needed: {corner_swaps}")
    
    # Use existing extract_edges function
    edges = extract_edges(cube_state)
    
    # Define what each edge position should contain (in order matching extract_edges)
    expected_edges = [
        tuple(sorted(["White", "Blue"])),
        tuple(sorted(["White", "Orange"])),
        tuple(sorted(["White", "Red"])),
        tuple(sorted(["White", "Green"])),
        tuple(sorted(["Red", "Green"])),
        tuple(sorted(["Blue", "Orange"])),
        tuple(sorted(["Green", "Orange"])),
        tuple(sorted(["Red", "Blue"])),
        tuple(sorted(["Yellow", "Green"])),
        tuple(sorted(["Yellow", "Orange"])),
        tuple(sorted(["Yellow", "Red"])),
        tuple(sorted(["Yellow", "Blue"])),
    ]
    
    # Create mapping for edges
    edge_mapping = []
    for edge in edges:
        edge_sorted = tuple(sorted(edge))
        try:
            correct_pos = expected_edges.index(edge_sorted)
            edge_mapping.append(correct_pos)
        except ValueError:
            msg = f"Invalid edge piece: {edge}"
            if debug:
                print(f"  ❌ {msg}")
            if show_analysis:
                return False, msg
            return False, None
    
    # Count swaps for edges
    edge_swaps = count_swaps(edge_mapping.copy())
    
    if debug:
        print(f"  Edge swaps needed: {edge_swaps}")
    
    total_swaps = corner_swaps + edge_swaps
    is_valid = (total_swaps % 2) == 0
    
    if debug:
        print(f"  Total swaps: {total_swaps}")
        print(f"  Parity: {'even' if is_valid else 'odd'}")
        if is_valid:
            print(f"  ✅ Permutation parity is valid (even)")
        else:
            print(f"  ❌ Permutation parity is invalid (must be even)")
    
    if not is_valid:
        msg = f"Permutation parity invalid: {total_swaps} total swaps (must be even)"
        if show_analysis:
            return False, msg
        return False, None
    
    return True, None


def count_swaps(pieces):
    """
    Count the number of swaps needed to sort pieces into correct positions.
    
    Args:
        pieces: List where pieces[i] indicates which piece is in position i
    
    Returns:
        int: Number of swaps needed
    """
    swaps = 0
    for pos in range(len(pieces)):
        while pieces[pos] != pos:
            # Swap piece at current position with piece at its target position
            dst = pieces[pos]
            pieces[pos], pieces[dst] = pieces[dst], pieces[pos]
            swaps += 1
    return swaps
