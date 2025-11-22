#!/usr/bin/env python3
"""
Production startup script for Rubik's Cube Backend API
Optimized for deployment on platforms like Render, Heroku, etc.
"""

import os
import sys

def main():
    """Main startup function for production"""
    print("[BACKEND] Starting Rubik's Cube API in production mode...")
    print("=" * 60)
    
    # Get port from environment variable (required for Render/Heroku)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"[INFO] Server will listen on {host}:{port}")
    print(f"[INFO] Environment: {os.environ.get('RENDER', 'local')}")
    print("=" * 60)
    
    try:
        # Import and run the Flask application
        from backend_api import app
        
        # Run with production settings
        app.run(
            host=host,
            port=port,
            debug=False,  # Disable debug in production
            threaded=True  # Enable threading for better performance
        )
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        return 0
    except Exception as e:
        print(f"[ERROR] Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
