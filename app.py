# app.py - main Flask application
import os
import atexit
from datetime import timedelta

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Optional imports for scheduler - won't fail if not installed
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    try:
        from apscheduler.triggers.interval import IntervalTrigger
    except ImportError:
        IntervalTrigger = None
    SCHEDULER_AVAILABLE = True
except ImportError:
    print("Warning: APScheduler not installed. Weather updates will be disabled.")
    SCHEDULER_AVAILABLE = False

# Create the db instance first
db = SQLAlchemy()

def init_db(app):
    """Initialize the database and create all tables"""
    with app.app_context():
        try:
            # Import models here to avoid circular imports
            from models import (
                User, Office, Asset, Booking, Maintenance, DashboardMetric, ActivityLog,
                Employee, CoffeeMachine, CoffeeOrder, TemperatureSensor, TemperatureReading,
                StockCategory, StockItem, StockTransaction, StockOrder, PresenceLog, SafetyVisitor,
                SafetyEvent, MeetingRoom
            )
            
            # Create database tables
            db.create_all()
            
            # Check if we need to seed initial data
            if not User.query.first():
                # Create a default admin user
                admin = User(
                    email='admin@example.com',
                    name='Admin',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                
        except OperationalError as e:
            print(f"Database Error: {e}")
            print("⚠️  Continuing without database - using mock data")
            # Don't crash the app, continue with mock data
        except Exception as e:
            print(f"Error initializing database: {e}")
            print("⚠️  Continuing without database - using mock data")

# Create other Flask extensions
migrate = Migrate()
jwt = JWTManager()

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Use same temp directory approach as login portal for consistency
    import tempfile
    temp_dir = tempfile.gettempdir()
    db_path = os.path.join(temp_dir, "office_eathon.db")
    
    print(f"📁 Using shared database: {db_path}")
    
    # Use forward slashes for SQLite URI on Windows (SQLAlchemy requirement)
    db_uri_path = db_path.replace('\\', '/')
    
    # Simple database URI using temp path with proper format
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_uri_path}'
    print(f"🔌 Using DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devsecret')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwtsecret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    # Make sure app context is pushed before database operations
    app.app_context().push()
    init_db(app)

    # Explicit test connection to surface any OperationalError early
    try:
        with app.app_context():
            # This will force a real connection attempt
            conn = db.engine.connect()
            conn.close()
            print("✅ Database engine connection successful.")
    except OperationalError as oe:
        print(f"❌ Database engine OperationalError: {oe}")
        print("Proceeding with mock data mode; endpoints relying on DB will be limited.")
    except Exception as ex:
        print(f"❌ Unexpected database connection error: {ex}")
        print("Proceeding with mock data mode; endpoints relying on DB will be limited.")

    # register blueprints
    from auth import auth_bp
    from api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        # Render the main dashboard view
        return render_template('dashboard.html', active='dashboard')

    @app.route('/coffee')
    def coffee_page():
        return render_template('coffee.html', active='coffee')

    @app.route('/temperature')
    def temperature_page():
        """Render the main temperature dashboard"""
        # Get all offices for the selector
        try:
            from models import Office
            offices = Office.query.all()
        except:
            offices = []  # Fallback if Office model not available
        return render_template('temperature_comparison.html', 
                             active='temperature',
                             offices=offices)

    @app.route('/api/temperature/comparison')
    def temperature_comparison():
        """Get temperature comparison data for charting"""
        try:
            from services.mock_data import get_mock_office_data
            from services.openweathermap import fetch_forecast_weather, fetch_hourly_weather

            # For now, use a default Cape Town Pinelands office without database
            office_id = 1
            office_name = 'Cape Town Pinelands Office'
            
            # Always generate indoor (mock) data for now
            indoor_data, outdoor_mock = get_mock_office_data(office_id)

            # Try to get real outdoor data from OpenWeatherMap
            outdoor_data = None
            
            # First try to get Cape Town, Pinelands weather
            try:
                owm_data = fetch_forecast_weather("Cape Town", hours=24)
                if owm_data:
                    outdoor_data = [
                        {
                            'timestamp': item.get('timestamp'),
                            'temperature': item.get('temperature'),
                            'humidity': item.get('humidity'),
                            'description': item.get('conditions')
                        }
                        for item in owm_data
                    ]
            except Exception as e:
                app.logger.warning(f"OpenWeatherMap city fetch failed: {e}")
            
            # If city lookup fails, try using coordinates (-33.9249, 18.4241)
            if not outdoor_data:
                try:
                    lat = -33.9249
                    lon = 18.4241
                    owm_data = fetch_hourly_weather(lat, lon, hours=24)
                    if owm_data:
                        outdoor_data = [
                            {
                                'timestamp': item.get('timestamp'),
                                'temperature': item.get('temperature'),
                                'humidity': item.get('humidity'),
                                'description': item.get('conditions')
                            }
                            for item in owm_data
                        ]
                except Exception as e:
                    app.logger.warning(f"OpenWeatherMap coordinate fetch failed: {e}")

            # Fallback to mock outdoor data if OpenWeatherMap failed or not available
            if not outdoor_data:
                outdoor_data = outdoor_mock

            office_data = {
                'office_name': office_name,
                'indoor_data': indoor_data,
                'outdoor_data': outdoor_data
            }

            return jsonify([office_data])
        except Exception as e:
            app.logger.error(f"Error in temperature comparison: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/_dev/seed_stock')
    def _dev_seed_stock():
        """Dev helper: seed stock data when called with the secret query param.
        
        Usage: GET /_dev/seed_stock?secret=seedme
        """
        expected = os.getenv('DEV_SEED_SECRET', 'seedme')
        secret = request.args.get('secret')
        if secret != expected:
            return jsonify({'error': 'forbidden'}), 403
        
        try:
            from models import StockItem, StockCategory, StockLocation, StockTransaction, ActivityLog
            from datetime import datetime, timedelta
            import random
            
            # Create categories
            categories_data = [
                {'name': 'Food & Beverage', 'description': 'Coffee, tea, snacks, and other food items'},
                {'name': 'Office Supplies', 'description': 'Paper, pens, and general office supplies'},
                {'name': 'Cleaning', 'description': 'Cleaning supplies and maintenance items'},
                {'name': 'Equipment', 'description': 'Office equipment and accessories'}
            ]
            
            categories = {}
            for cat_data in categories_data:
                category = StockCategory.query.filter_by(name=cat_data['name']).first()
                if not category:
                    category = StockCategory(**cat_data)
                    db.session.add(category)
                    db.session.flush()
                categories[cat_data['name']] = category
            
            # Create locations
            locations_data = [
                {'name': 'Kitchen', 'area': 'Kitchen Area'},
                {'name': 'Fridge', 'area': 'Kitchen Area'},
                {'name': 'Store', 'area': 'Storage'},
                {'name': 'Storage', 'area': 'Storage'}
            ]
            
            locations = {}
            for loc_data in locations_data:
                location = StockLocation.query.filter_by(name=loc_data['name']).first()
                if not location:
                    location = StockLocation(office_id=1, **loc_data)
                    db.session.add(location)
                    db.session.flush()
                locations[loc_data['name']] = location
            
            # Create stock items
            items_data = [
                {
                    'name': 'Coffee Beans', 'sku': 'CB001', 'quantity': 3, 'unit': 'kg',
                    'reorder_point': 5, 'supplier': 'Bean Co.', 'unit_cost': 25.00,
                    'category': 'Food & Beverage', 'location': 'Kitchen'
                },
                {
                    'name': 'Milk', 'sku': 'MK001', 'quantity': 10, 'unit': 'liters',
                    'reorder_point': 5, 'supplier': 'Dairy Fresh', 'unit_cost': 1.50,
                    'category': 'Food & Beverage', 'location': 'Fridge'
                },
                {
                    'name': 'Coffee Filters', 'sku': 'CF001', 'quantity': 25, 'unit': 'pieces',
                    'reorder_point': 20, 'supplier': 'Office Plus', 'unit_cost': 0.15,
                    'category': 'Office Supplies', 'location': 'Store'
                },
                {
                    'name': 'Printer Paper', 'sku': 'PP001', 'quantity': 2, 'unit': 'packs',
                    'reorder_point': 5, 'supplier': 'Paper World', 'unit_cost': 8.50,
                    'category': 'Office Supplies', 'location': 'Storage'
                }
            ]
            
            created_items = []
            for item_data in items_data:
                existing_item = StockItem.query.filter_by(sku=item_data['sku']).first()
                if existing_item:
                    continue
                
                category = categories.get(item_data.pop('category'))
                location = locations.get(item_data.pop('location'))
                
                item = StockItem(
                    category_id=category.id if category else None,
                    location_id=location.id if location else None,
                    last_restock=datetime.now() - timedelta(days=random.randint(1, 30)),
                    **item_data
                )
                
                db.session.add(item)
                created_items.append(item_data['name'])
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'categories_created': len(categories_data),
                'locations_created': len(locations_data),
                'items_created': len(created_items),
                'items': created_items
            })
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Stock seeding failed: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/stock')
    def stock_page():
        return render_template('stock.html', active='stock')

    # Meeting Room Temperature Management
    @app.route('/rooms')
    def rooms_page():
        """Display meeting room temperature control interface"""
        return render_template('rooms.html', active='rooms')
    
    @app.route('/api/rooms')
    def get_rooms():
        """Get all meeting rooms with current temperatures"""
        try:
            import random
            from datetime import datetime
            
            # Generate mock room data (6 rooms across 2 floors)
            rooms_data = []
            room_configs = [
                {'name': 'Boardroom A', 'floor': 1, 'capacity': 12},
                {'name': 'Conference Room B', 'floor': 1, 'capacity': 8},
                {'name': 'Meeting Room C', 'floor': 1, 'capacity': 6},
                {'name': 'Executive Suite D', 'floor': 2, 'capacity': 10},
                {'name': 'Collaboration Hub E', 'floor': 2, 'capacity': 8},
                {'name': 'Innovation Lab F', 'floor': 2, 'capacity': 12},
            ]
            
            for i, room_config in enumerate(room_configs, 1):
                current_temp = round(random.uniform(20.5, 24.5), 1)
                target_temp = 22.0
                humidity = round(random.uniform(40, 60), 1)
                
                # Determine HVAC status based on temperature
                diff = current_temp - target_temp
                if diff > 1:
                    hvac_status = 'cooling'
                elif diff < -1:
                    hvac_status = 'heating'
                else:
                    hvac_status = 'auto'
        
                # Calculate comfort status
                temp_ok = abs(current_temp - target_temp) <= 1.5
                humidity_ok = 30 <= humidity <= 60
                
                if temp_ok and humidity_ok:
                    comfort_status = 'comfortable'
                elif temp_ok or humidity_ok:
                    comfort_status = 'moderate'
                else:
                    comfort_status = 'uncomfortable'
                
                rooms_data.append({
                    'id': i,
                    'name': room_config['name'],
                    'floor': room_config['floor'],
                    'capacity': room_config['capacity'],
                    'current_temperature': current_temp,
                    'target_temperature': target_temp,
                    'humidity': humidity,
                    'hvac_status': hvac_status,
                    'hvac_mode': 'auto',
                    'comfort_status': comfort_status,
                    'last_adjusted': None
                })
            
            return jsonify(rooms_data)
        except Exception as e:
            app.logger.error(f"Error fetching rooms: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/rooms/<int:room_id>/temperature', methods=['POST'])
    def adjust_room_temperature(room_id):
        """Adjust target temperature for a specific room"""
        try:
            data = request.get_json()
            new_target = float(data.get('target_temperature'))
            
            if not 16 <= new_target <= 30:
                return jsonify({'error': 'Temperature must be between 16°C and 30°C'}), 400
            
            # For now, just return success (in production this would update the database)
            return jsonify({
                'success': True,
                'room_id': room_id,
                'target_temperature': new_target,
                'hvac_status': 'auto',
                'message': 'Temperature adjusted successfully'
            })
        except Exception as e:
            app.logger.error(f"Error adjusting temperature: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/_dev/seed_office')
    def _dev_seed_office():
        """Dev helper: create a seeded office with coords when called with the secret query param.

        Usage: GET /_dev/seed_office?secret=seedme  (change via DEV_SEED_SECRET env var)
        """
        expected = os.getenv('DEV_SEED_SECRET', 'seedme')
        secret = request.args.get('secret')
        if secret != expected:
            return jsonify({'error': 'forbidden'}), 403
        try:
            from models import Office
            office = Office.query.filter_by(name='Cape Town Pinelands Office').first()
            if not office:
                # Cape Town, Pinelands coordinates: -33.9249, 18.4241
                office = Office(name='Cape Town Pinelands Office', location='-33.9249,18.4241')
                db.session.add(office)
                db.session.commit()
                return jsonify({'created': office.id, 'name': office.name, 'location': office.location})
            return jsonify({'exists': office.id, 'name': office.name, 'location': office.location})
        except Exception as e:
            app.logger.error(f"Dev seed failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/_dev/seed_rooms')
    def _dev_seed_rooms():
        """Dev helper: create 6 meeting rooms across 2 floors
        
        Usage: GET /_dev/seed_rooms?secret=seedme
        """
        expected = os.getenv('DEV_SEED_SECRET', 'seedme')
        secret = request.args.get('secret')
        if secret != expected:
            return jsonify({'error': 'forbidden'}), 403
        try:
            import random
            
            # Since we can't query Office reliably yet, we'll just create rooms with office_id=1
            # Create 6 meeting rooms (3 per floor)
            rooms = [
                {'name': 'Boardroom A', 'floor': 1, 'capacity': 12},
                {'name': 'Conference Room B', 'floor': 1, 'capacity': 8},
                {'name': 'Meeting Room C', 'floor': 1, 'capacity': 6},
                {'name': 'Executive Suite D', 'floor': 2, 'capacity': 10},
                {'name': 'Collaboration Hub E', 'floor': 2, 'capacity': 8},
                {'name': 'Innovation Lab F', 'floor': 2, 'capacity': 12},
            ]
            
            # Import here to use within request context
            from models import MeetingRoom
            
            created_rooms = []
            for room_data in rooms:
                room = MeetingRoom(
                    name=room_data['name'],
                    office_id=1,  # Default office
                    floor=room_data['floor'],
                    capacity=room_data['capacity'],
                    target_temperature=22.0,
                    current_temperature=round(random.uniform(20.5, 24.5), 1),
                    humidity=round(random.uniform(40, 60), 1),
                    hvac_status='auto',
                    hvac_mode='auto'
                )
                db.session.add(room)
                created_rooms.append(room_data['name'])
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'rooms_created': len(created_rooms),
                'rooms': created_rooms
            })
        except Exception as e:
            import traceback
            app.logger.error(f"Seed rooms failed: {e}\n{traceback.format_exc()}")
            return jsonify({'error': str(e)}), 500

    @app.route('/_dev/seed_presence')
    def _dev_seed_presence():
        """Dev helper: seed presence tracking data
        
        Usage: GET /_dev/seed_presence?secret=seedme
        """
        expected = os.getenv('DEV_SEED_SECRET', 'seedme')
        secret = request.args.get('secret')
        if secret != expected:
            return jsonify({'error': 'forbidden'}), 403
        
        try:
            from models import User, Employee, Office, PresenceLog, PresenceStatus
            from datetime import datetime, timedelta
            import random
            
            # Check if office exists
            office = Office.query.filter_by(name='Cape Town Pinelands Office').first()
            if not office:
                office = Office(
                    name='Cape Town Pinelands Office',
                    address='Pinelands, Cape Town, South Africa',
                    description='Main office location'
                )
                db.session.add(office)
                db.session.commit()
            
            # Define employees with departments
            employees_data = [
                # Business Operations
                {'first_name': 'Lilitha', 'last_name': 'Nomaxayi', 'email': 'lilitha.nomaxayi@mrisoftware.com', 
                 'department': 'Business Operations', 'role': 'Business Operations Specialist', 'phone': '+27 21 555 0101'},
                {'first_name': 'Anshah', 'last_name': 'Shabangu', 'email': 'anshah.shabangu@mrisoftware.com', 
                 'department': 'Business Operations', 'role': 'Business Operations Analyst', 'phone': '+27 21 555 0102'},
                # Data Management
                {'first_name': 'Eathon', 'last_name': 'Groenewald', 'email': 'eathon.groenewald@mrisoftware.com', 
                 'department': 'Data Management', 'role': 'Data Management Specialist', 'phone': '+27 21 555 0103'},
                # Lease Administration
                {'first_name': 'Kayleigh', 'last_name': 'Jonkers', 'email': 'kayleigh.jonkers@mrisoftware.com', 
                 'department': 'Lease Administration', 'role': 'Lease Administrator', 'phone': '+27 21 555 0104'},
                # GPS
                {'first_name': 'Stacy', 'last_name': 'Clarke', 'email': 'stacy.clarke@mrisoftware.com', 
                 'department': 'GPS', 'role': 'GPS Specialist', 'phone': '+27 21 555 0105'},
                {'first_name': 'Amber-Lee', 'last_name': 'November', 'email': 'amber-lee.november@mrisoftware.com', 
                 'department': 'GPS', 'role': 'GPS Analyst', 'phone': '+27 21 555 0106'},
                # Support
                {'first_name': 'Aden', 'last_name': 'Weir', 'email': 'aden.weir@mrisoftware.com', 
                 'department': 'Support', 'role': 'Support Specialist', 'phone': '+27 21 555 0107'},
                {'first_name': 'Rushdeen', 'last_name': 'White', 'email': 'rushdeen.white@mrisoftware.com', 
                 'department': 'Support', 'role': 'Support Engineer', 'phone': '+27 21 555 0108'},
                # Product Development
                {'first_name': 'Alex', 'last_name': 'Abrahams', 'email': 'alex.abrahams@mrisoftware.com', 
                 'department': 'Product Development', 'role': 'Product Developer', 'phone': '+27 21 555 0109'},
                {'first_name': 'Sakhe', 'last_name': 'Dudula', 'email': 'sakhe.dudula@mrisoftware.com', 
                 'department': 'Product Development', 'role': 'Senior Product Developer', 'phone': '+27 21 555 0110'},
                {'first_name': 'Jonathan', 'last_name': 'Nel', 'email': 'jonathan.nel@mrisoftware.com', 
                 'department': 'Product Development', 'role': 'Product Manager', 'phone': '+27 21 555 0111'},
                # GPS Additional
                {'first_name': 'Melissa', 'last_name': 'Wessels', 'email': 'melissa.wessels@mrisoftware.com', 
                 'department': 'GPS', 'role': 'GPS Coordinator', 'phone': '+27 21 555 0112'},
                {'first_name': 'Marlise', 'last_name': 'Truter', 'email': 'marlise.truter@mrisoftware.com', 
                 'department': 'GPS', 'role': 'GPS Analyst', 'phone': '+27 21 555 0113'},
                # Managed Services
                {'first_name': 'Anthea', 'last_name': 'Baroutsos', 'email': 'anthea.baroutsos@mrisoftware.com', 
                 'department': 'Managed Services', 'role': 'Managed Services Specialist', 'phone': '+27 21 555 0114'}
            ]
            
            created_employees = []
            
            for emp_data in employees_data:
                # Check if user exists
                user = User.query.filter_by(email=emp_data['email']).first()
                if not user:
                    user = User(
                        email=emp_data['email'],
                        name=f"{emp_data['first_name']} {emp_data['last_name']}",
                        department=emp_data['department'],
                        is_admin=False
                    )
                    user.set_password('password123')
                    db.session.add(user)
                    db.session.flush()
                
                # Check if employee profile exists
                employee = Employee.query.filter_by(email=emp_data['email']).first()
                if not employee:
                    employee = Employee(
                        user_id=user.id,
                        office_id=office.id,
                        first_name=emp_data['first_name'],
                        last_name=emp_data['last_name'],
                        email=emp_data['email'],
                        phone=emp_data['phone'],
                        role=emp_data['role'],
                        department=emp_data['department'],
                        status='active',
                        access_level=1
                    )
                    db.session.add(employee)
                    db.session.flush()
                
                created_employees.append((user, employee))
            
            db.session.commit()
            
            # Create presence logs for today
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # 60% in office
            in_office_count = 6
            in_office_employees = random.sample(created_employees, in_office_count)
            
            check_in_start = today + timedelta(hours=7)
            check_in_end = today + timedelta(hours=10)
            
            for user, employee in in_office_employees:
                random_minutes = random.randint(0, 180)
                check_in_time = check_in_start + timedelta(minutes=random_minutes)
                
                # Check if already has log today
                existing = PresenceLog.query.filter(
                    PresenceLog.user_id == user.id,
                    PresenceLog.created_at >= today
                ).first()
                
                if not existing:
                    presence_log = PresenceLog(
                        user_id=user.id,
                        status=PresenceStatus.IN,
                        location=office.name,
                        notes=f"Checked in",
                        created_at=check_in_time
                    )
                    db.session.add(presence_log)
            
            db.session.commit()
            
            # Summary
            summary = {
                'success': True,
                'office': office.name,
                'total_employees': len(created_employees),
                'in_office_today': in_office_count,
                'employees_by_department': {}
            }
            
            for user, employee in created_employees:
                dept = employee.department
                if dept not in summary['employees_by_department']:
                    summary['employees_by_department'][dept] = []
                
                # Check status
                latest = PresenceLog.query.filter(
                    PresenceLog.user_id == user.id,
                    PresenceLog.created_at >= today
                ).order_by(PresenceLog.created_at.desc()).first()
                
                status = 'IN OFFICE' if latest and latest.status == PresenceStatus.IN else 'NOT IN OFFICE'
                summary['employees_by_department'][dept].append({
                    'name': employee.full_name,
                    'status': status
                })
            
            return jsonify(summary)
            
        except Exception as e:
            import traceback
            app.logger.error(f"Presence seeding failed: {e}\n{traceback.format_exc()}")
            return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

    @app.route('/presence')
    def presence_page():
        # use the converted presence template
        return render_template('presence.html', active='presence')
    
    @app.route('/employee/login')
    def employee_login():
        """Employee login page for check-in/check-out"""
        return render_template('employee_login.html')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    return app



if __name__ == '__main__':
    app = create_app()
    # Run without the reloader/debugger to keep a single stable process
    app.run(debug=False, host='0.0.0.0', port=5000)
