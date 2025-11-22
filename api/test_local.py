"""
Quick test script to verify backend setup before deployment
Run this to ensure everything works locally
"""

import sys
import subprocess

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        print("❌ Flask not installed")
        return False
    
    try:
        import flask_cors
        print("✅ Flask-CORS installed")
    except ImportError:
        print("❌ Flask-CORS not installed")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV not installed")
        return False
    
    try:
        import numpy
        print(f"✅ NumPy {numpy.__version__}")
    except ImportError:
        print("❌ NumPy not installed")
        return False
    
    try:
        import kociemba
        print("✅ Kociemba installed")
    except ImportError:
        print("❌ Kociemba not installed")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow installed")
    except ImportError:
        print("❌ Pillow not installed")
        return False
    
    return True

def test_backend_api():
    """Test if backend_api.py can be imported"""
    print("\nTesting backend_api.py...")
    
    try:
        import backend_api
        print("✅ backend_api.py imports successfully")
        print(f"✅ Flask app created: {backend_api.app}")
        return True
    except Exception as e:
        print(f"❌ Error importing backend_api.py: {e}")
        return False

def main():
    print("=" * 60)
    print("Backend Deployment Readiness Test")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test backend API
    api_ok = test_backend_api()
    
    print("\n" + "=" * 60)
    if imports_ok and api_ok:
        print("✅ All tests passed! Backend is ready for deployment.")
        print("\nNext steps:")
        print("1. Push to GitHub: git add . && git commit -m 'Ready for deployment' && git push")
        print("2. Deploy to Render following DEPLOYMENT.md")
    else:
        print("❌ Some tests failed. Install missing packages:")
        print("   pip install -r requirements.txt")
    print("=" * 60)

if __name__ == "__main__":
    main()
