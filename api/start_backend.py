#!/usr/bin/env python3
"""
Startup script for the Rubik's Cube Color Detection Backend API
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask_cors', 'cv2', 'numpy', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("[ERROR] Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n[INFO] Install missing packages with:")
        print("   pip install -r ../requirements.txt")
        return False
    
    return True

def main():
    """Main startup function"""
    print("[BACKEND] Starting Rubik's Cube Color Detection Backend...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend_api.py'):
        print("[ERROR] backend_api.py not found in current directory")
        print("   Please run this script from the api/ directory")
        return 1
    
    # Check dependencies
    print("[INFO] Checking dependencies...")
    if not check_dependencies():
        return 1
    
    print("[SUCCESS] All dependencies found")
    print("[INFO] Starting Flask API server...")
    print("   API will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the Flask application
        from backend_api import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        return 0
    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())