"""
Employee Check-In Portal
A standalone Flask application for employee check-in/check-out
Runs on port 5002 and communicates with the main app's database
"""
import os
import sys
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

# Import models and database from main app
from app import db
from models import Employee, User, PresenceLog, Office, PresenceStatus

def create_employee_portal():
    """Create the employee portal Flask application"""
    app = Flask(__name__)
    
    # Get the database path from environment or use default temp location
    db_path = os.path.join(os.environ.get('TEMP', '/tmp'), 'office_eathon.db')
    db_uri = f'sqlite:///{db_path}'
    
    print(f"📁 Employee Portal using database: {db_path}")
    print(f"🔌 Using DB URI: {db_uri}")
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'employee-portal-secret-key-2025')
    
    # Enable CORS
    CORS(app)
    
    # Initialize database with this app
    db.init_app(app)
    
    # Routes
    @app.route('/')
    def index():
        """Main employee login page"""
        return render_template('employee_login.html')
    
    @app.route('/api/employee/check-in', methods=['POST'])
    def employee_check_in():
        """Handle employee check-in/check-out"""
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            status = data.get('status', 'in')  # 'in' or 'out'
            
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Find user by email
            user = User.query.filter_by(email=email.lower().strip()).first()
            
            if not user:
                print(f"❌ User not found: {email}")
                # List available employees for debugging
                all_employees = db.session.query(Employee, User).join(User).all()
                print(f"📋 Available employees ({len(all_employees)}):")
                for emp, usr in all_employees:
                    print(f"   - {usr.email} | {usr.name}")
                return jsonify({'error': 'Invalid email or password'}), 404
            
            # Simple password check (in production, use proper hashing)
            if password != 'password123':
                print(f"❌ Invalid password for user: {email}")
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Get employee record
            employee = Employee.query.filter_by(user_id=user.id).first()
            
            if not employee:
                print(f"❌ No employee record for user: {email}")
                return jsonify({'error': 'Employee record not found'}), 404
            
            # Create presence log entry
            presence_status = PresenceStatus.IN if status == 'in' else PresenceStatus.OUT
            
            new_log = PresenceLog(
                user_id=user.id,
                status=presence_status,
                location=f"Office {employee.office_id}",
                notes=f"Employee {status} via portal"
            )
            
            db.session.add(new_log)
            db.session.commit()
            
            print(f"✅ {user.name} checked {status} successfully")
            
            return jsonify({
                'success': True,
                'message': f'Successfully checked {status}',
                'user': {
                    'name': user.name,
                    'email': user.email,
                    'department': employee.department,
                    'status': presence_status.value
                },
                'timestamp': new_log.created_at.isoformat() if hasattr(new_log, 'created_at') else datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            print(f"❌ Error during check-in: {str(e)}")
            db.session.rollback()
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    @app.route('/api/employee/status/<email>', methods=['GET'])
    def get_employee_status(email):
        """Get the current status of an employee"""
        try:
            user = User.query.filter_by(email=email.lower().strip()).first()
            
            if not user:
                return jsonify({'error': 'Employee not found'}), 404
            
            employee = Employee.query.filter_by(user_id=user.id).first()
            
            if not employee:
                return jsonify({'error': 'Employee record not found'}), 404
            
            # Get latest presence log
            latest_log = PresenceLog.query.filter_by(
                user_id=user.id
            ).order_by(PresenceLog.created_at.desc()).first()
            
            current_status = latest_log.status.value if latest_log else 'OUT'
            
            return jsonify({
                'user': {
                    'name': user.name,
                    'email': user.email,
                    'department': employee.department
                },
                'status': current_status,
                'last_update': latest_log.created_at.isoformat() if latest_log else None
            }), 200
            
        except Exception as e:
            print(f"❌ Error getting status: {str(e)}")
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'Employee Portal',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    return app

def main():
    """Main entry point for the employee portal"""
    print("🚀 Starting Employee Check-In Portal...")
    print("📍 This is a standalone service for employee check-in/check-out")
    
    app = create_employee_portal()
    
    # Verify database connection
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Count employees
            employee_count = Employee.query.count()
            print(f"👥 Found {employee_count} employees in database")
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            print("⚠️ Make sure the main app has been run at least once to create the database")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("🌐 Employee Portal is running on http://localhost:5002")
    print("📱 Employees can access the check-in page at:")
    print("   http://localhost:5002")
    print("="*60)
    print("\n🔐 Default credentials:")
    print("   Email: eathon.groenewald@mrisoftware.com")
    print("   Password: password123")
    print("\n🔧 Press Ctrl+C to stop the portal")
    print("="*60 + "\n")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True,
        use_reloader=False  # Disable reloader to avoid running twice
    )

if __name__ == '__main__':
    main()
