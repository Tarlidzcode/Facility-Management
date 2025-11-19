#!/usr/bin/env python3
"""
Simple script to run the Flask application with temp database.
"""
import sys
import os
import tempfile

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set environment variable to use temp database
temp_db = os.path.join(tempfile.gettempdir(), "office_eathon.db")
os.environ['DATABASE_URL'] = f'sqlite:///{temp_db}'

print(f"📁 Using database: {temp_db}")

try:
    from app import create_app
    
    print("🚀 Starting Office Management System...")
    app = create_app()
    
    print("✅ Application created successfully!")
    print("🌐 Starting server on http://localhost:5001")
    print("-" * 50)
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001,
        use_reloader=False  # Disable reloader
    )
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
