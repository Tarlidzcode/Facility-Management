#!/usr/bin/env python3
"""
Simple script to start the Flask app locally
"""
import os
import sys

# Change to the app directory  
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)
sys.path.insert(0, app_dir)

try:
    # Import and run the app
    from app import create_app
    
    print("🚀 Starting Office Management System...")
    print("📍 Working directory:", os.getcwd())
    
    app = create_app()
    
    print("✅ Application created successfully!")
    print("🌐 Starting server on http://localhost:5001")
    print("📦 Stock Management ready with clean JavaScript!")
    print("🛒 Features: Order system, SA retailers, search, pending orders")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001,
        use_reloader=False
    )
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔧 Make sure you're in the correct directory")
    print("📦 Check if dependencies are installed: pip install -r requirements.txt")
    
    # Try fallback approach
    try:
        import app as app_module
        if hasattr(app_module, 'app'):
            print("🔄 Trying fallback approach...")
            app_module.app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e2:
        print(f"❌ Fallback failed: {e2}")

input("\n✋ Press Enter to exit...")