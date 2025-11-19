"""
Employee Login Portal Server
Runs on separate port (5002) from main app (5001)
Shares the same database for presence tracking
"""
import os
import tempfile
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime

# Set database path (same as main app)
temp_dir = tempfile.gettempdir()
db_path = os.path.join(temp_dir, "office_eathon.db")

# Convert to forward slashes for SQLite URI
db_uri_path = db_path.replace('\\', '/')
os.environ['DATABASE_URL'] = f'sqlite:///{db_uri_path}'

print(f"📁 Using database: {db_path}")

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'employee-login-portal-secret-key'
CORS(app)  # Enable CORS for API calls

# Import models after setting DATABASE_URL
from models import db, Employee, User, PresenceLog, PresenceStatus
from presence_utils import get_current_presence_summary

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_uri_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

@app.route('/')
def index():
    """Main employee login page"""
    return render_template('employee_login.html')

@app.route('/api/employee/check-in', methods=['POST'])
def employee_check_in():
    """Employee check-in/check-out endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        status = data.get('status', 'in')  # 'in' or 'out'
        
        print(f"🔐 Employee check-in attempt: {email} - Status: {status}")
        
        # Validate credentials
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # For now, accept password123 for all users (simple auth)
        if password != 'password123':
            return jsonify({'error': 'Invalid password'}), 401
        
        # Find employee by email
        employee = Employee.query.filter(
            db.func.lower(Employee.email) == email
        ).first()
        
        if not employee:
            print(f"❌ Employee not found: {email}")
            return jsonify({'error': 'Employee not found'}), 404
        
        if not employee.user_id:
            print(f"❌ Employee has no associated user: {email}")
            return jsonify({'error': 'Employee account not properly configured'}), 400
        
        # Create presence log
        presence_status = PresenceStatus.IN if status == 'in' else PresenceStatus.OUT
        
        presence_log = PresenceLog(
            user_id=employee.user_id,
            status=presence_status,
            location='Office' if status == 'in' else None,
            notes=f"Employee check-{status} via login portal"
        )
        
        db.session.add(presence_log)
        db.session.commit()
        
        print(f"✅ {employee.full_name} checked {status} successfully")

        # Compute current presence summary (employees + visitors)
        presence_summary = get_current_presence_summary(include_visitors=True)

        return jsonify({
            'success': True,
            'user': {
                'name': employee.full_name,
                'email': employee.email,
                'department': employee.department
            },
            'status': status,
            'time': datetime.now().strftime('%I:%M %p'),
            'presence': presence_summary
        })
        
    except Exception as e:
        print(f"❌ Error in employee_check_in: {e}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred during check-in'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'employee-login', 'port': 5002})

if __name__ == '__main__':
    print("🚀 Starting Employee Login Portal...")
    print("=" * 60)
    print("📍 Server URL: http://localhost:5002")
    print("🔐 Login Page: http://localhost:5002")
    print("🌐 API Endpoint: POST http://localhost:5002/api/employee/check-in")
    print("=" * 60)
    print("💡 This portal shares the database with main app (port 5001)")
    print("📊 Presence logs will appear in the main presence tracking page")
    print("=" * 60)
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5002,
        use_reloader=False
    )
