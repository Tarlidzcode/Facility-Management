"""
Start app with temp database
"""
import os
import tempfile

# Set database path
temp_dir = tempfile.gettempdir()
db_path = os.path.join(temp_dir, "office_eathon.db")
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

print(f"📁 Using database: {db_path}")

# Now run the app
if __name__ == '__main__':
    from app import create_app
    from flask import request
    
    print("🚀 Starting Office Management System...")
    app = create_app()
    
    # Add request logging middleware
    @app.before_request
    def log_request():
        print(f"🌐 {request.method} {request.path} - {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        print(f"✅ Response: {response.status_code}")
        return response
    
    print("✅ Application created successfully!")
    print("🌐 Starting server on http://localhost:5001")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5001,
        use_reloader=False
    )
