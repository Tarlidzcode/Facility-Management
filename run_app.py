#!/usr/bin/env python3
"""
Simple script to run the Flask application.
This can be executed from the current directory.
"""

import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app import create_app
    
    print("🚀 Starting Office Management System...")
    print("📍 Creating Flask application...")
    
    app = create_app()
    
    print("✅ Application created successfully!")
    print("🌐 Starting server on http://localhost:5001")
    print("💬 Chat feature with fallback responses is ready!")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001,
        use_reloader=False  # Disable reloader in Live Share environment
    )
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("🔧 Make sure you're in the correct directory and dependencies are installed")
    print("📦 Try running: pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Error starting application: {e}")
    print("🔧 Check the error details above")
    
input("\n✋ Press Enter to exit...")