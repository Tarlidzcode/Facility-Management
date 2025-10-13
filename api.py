# api.py - main API blueprint
from flask import Blueprint, request, jsonify
import os
import json
import urllib.request
import urllib.error
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Office, Employee, Asset, Booking, Maintenance, User
from schemas import OfficeSchema, EmployeeSchema, AssetSchema, BookingSchema, MaintenanceSchema, UserSchema
from datetime import datetime

api_bp = Blueprint('api', __name__)

office_schema = OfficeSchema()
offices_schema = OfficeSchema(many=True)
employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)
asset_schema = AssetSchema()
assets_schema = AssetSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
maintenance_schema = MaintenanceSchema()
maintenances_schema = MaintenanceSchema(many=True)
user_schema = UserSchema()

# Offices CRUD
@api_bp.route('/offices', methods=['GET'])
@jwt_required()
def list_offices():
    offices = Office.query.all()
    return jsonify(offices_schema.dump(offices)), 200

@api_bp.route('/offices', methods=['POST'])
@jwt_required()
def create_office():
    data = request.get_json() or {}
    office = Office(name=data.get('name'), address=data.get('address'), description=data.get('description'))
    db.session.add(office)
    db.session.commit()
    return jsonify(office_schema.dump(office)), 201

@api_bp.route('/offices/<int:office_id>', methods=['PUT'])
@jwt_required()
def update_office(office_id):
    office = Office.query.get_or_404(office_id)
    data = request.get_json() or {}
    office.name = data.get('name', office.name)
    office.address = data.get('address', office.address)
    office.description = data.get('description', office.description)
    db.session.commit()
    return jsonify(office_schema.dump(office)), 200

@api_bp.route('/offices/<int:office_id>', methods=['DELETE'])
@jwt_required()
def delete_office(office_id):
    office = Office.query.get_or_404(office_id)
    db.session.delete(office)
    db.session.commit()
    return jsonify({"msg":"deleted"}), 200

# Employees CRUD
@api_bp.route('/employees', methods=['GET'])
@jwt_required()
def list_employees():
    employees = Employee.query.all()
    return jsonify(employees_schema.dump(employees)), 200

@api_bp.route('/employees', methods=['POST'])
@jwt_required()
def create_employee():
    data = request.get_json() or {}
    emp = Employee(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        role=data.get('role'),
        office_id=data.get('office_id')
    )
    db.session.add(emp)
    db.session.commit()
    return jsonify(employee_schema.dump(emp)), 201

@api_bp.route('/employees/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id):
    emp = Employee.query.get_or_404(id)
    data = request.get_json() or {}
    emp.first_name = data.get('first_name', emp.first_name)
    emp.last_name = data.get('last_name', emp.last_name)
    emp.email = data.get('email', emp.email)
    emp.phone = data.get('phone', emp.phone)
    emp.role = data.get('role', emp.role)
    emp.office_id = data.get('office_id', emp.office_id)
    db.session.commit()
    return jsonify(employee_schema.dump(emp)), 200

@api_bp.route('/employees/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return jsonify({"msg":"deleted"}), 200

# Assets CRUD
@api_bp.route('/assets', methods=['GET'])
@jwt_required()
def list_assets():
    assets = Asset.query.all()
    return jsonify(assets_schema.dump(assets)), 200

@api_bp.route('/assets', methods=['POST'])
@jwt_required()
def create_asset():
    data = request.get_json() or {}
    a = Asset(name=data.get('name'), serial=data.get('serial'), status=data.get('status', 'available'), office_id=data.get('office_id'))
    db.session.add(a)
    db.session.commit()
    return jsonify(asset_schema.dump(a)), 201

@api_bp.route('/assets/<int:id>', methods=['PUT'])
@jwt_required()
def update_asset(id):
    a = Asset.query.get_or_404(id)
    data = request.get_json() or {}
    a.name = data.get('name', a.name)
    a.serial = data.get('serial', a.serial)
    a.status = data.get('status', a.status)
    a.office_id = data.get('office_id', a.office_id)
    db.session.commit()
    return jsonify(asset_schema.dump(a)), 200

@api_bp.route('/assets/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_asset(id):
    a = Asset.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    return jsonify({"msg":"deleted"}), 200

# Bookings
@api_bp.route('/bookings', methods=['GET'])
@jwt_required()
def list_bookings():
    bookings = Booking.query.all()
    return jsonify(bookings_schema.dump(bookings)), 200

@api_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    data = request.get_json() or {}
    current = get_jwt_identity()
    b = Booking(
        resource=data.get('resource'),
        user_id=current['id'],
        start_time=datetime.fromisoformat(data.get('start_time')),
        end_time=datetime.fromisoformat(data.get('end_time')),
        notes=data.get('notes')
    )
    db.session.add(b)
    db.session.commit()
    return jsonify(booking_schema.dump(b)), 201

@api_bp.route('/bookings/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_booking(id):
    b = Booking.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()
    return jsonify({"msg":"deleted"}), 200

# Maintenance
@api_bp.route('/maintenances', methods=['GET'])
@jwt_required()
def list_maintenances():
    m = Maintenance.query.all()
    return jsonify(maintenances_schema.dump(m)), 200

@api_bp.route('/maintenances', methods=['POST'])
@jwt_required()
def create_maintenance():
    data = request.get_json() or {}
    m = Maintenance(asset_id=data.get('asset_id'), description=data.get('description'), status=data.get('status','open'))
    db.session.add(m)
    db.session.commit()
    return jsonify(maintenance_schema.dump(m)), 201

@api_bp.route('/maintenances/<int:id>', methods=['PUT'])
@jwt_required()
def update_maintenance(id):
    m = Maintenance.query.get_or_404(id)
    data = request.get_json() or {}
    m.description = data.get('description', m.description)
    m.status = data.get('status', m.status)
    db.session.commit()
    return jsonify(maintenance_schema.dump(m)), 200

# current user
@api_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current = get_jwt_identity()
    user = User.query.get(current['id'])
    return jsonify(user_schema.dump(user)), 200


# Dashboard data (demo endpoint used by the frontend). This is intentionally
# unauthenticated so the sample dashboard can be shown quickly. You can lock
# this down later to return real aggregated data.
@api_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # In a real app you'd aggregate database queries here. For now return
    # a simple JSON structure the frontend can consume.
    data = {
        "metrics": {
            "employees_in": 24,
            "employees_total": 32,
            "coffee_today": 47,
            "temperature": 22,
            "low_stock": 3
        },
        "coffee_series": {
            "labels": ['8am','9am','10am','11am','12pm','1pm','2pm','3pm'],
            "data": [3,12,9,6,5,4,10,8]
        },
        "temp_series": {
            "labels": ['6am','9am','12pm','3pm','6pm'],
            "data": [21.5,22.0,22.3,22.5,21.9]
        }
    }
    return jsonify(data), 200


# Simple AI endpoint for demo chat button. Intentionally unauthenticated so the
# floating help/chat button works without login. Replace with a proper AI
# integration (OpenAI, local LLM, etc.) when ready.
@api_bp.route('/ai', methods=['POST'])
def ai_reply():
    payload = request.get_json() or {}
    message = (payload.get('message') or '').strip()
    if not message:
        return jsonify({"reply": "Hi — how can I help? Ask about coffee, temperature, stock, or presence."}), 200
    # If an OpenAI key is present, call the API. Keep this optional so local
    # development works without network or keys.
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        try:
            url = 'https://api.openai.com/v1/chat/completions'
            body = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful office assistant for an office management dashboard.'},
                    {'role': 'user', 'content': message}
                ],
                'max_tokens': 200,
                'temperature': 0.2,
            }
            req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'),
                                         headers={
                                             'Content-Type': 'application/json',
                                             'Authorization': f'Bearer {openai_key}'
                                         })
            with urllib.request.urlopen(req, timeout=15) as resp:
                res = json.load(resp)
                reply = None
                if isinstance(res, dict):
                    choices = res.get('choices') or []
                    if choices:
                        msg = choices[0].get('message') or {}
                        reply = msg.get('content')
                if reply:
                    return jsonify({'reply': reply.strip()}), 200
        except urllib.error.HTTPError as he:
            # fall through to canned reply on API error
            try:
                err = he.read().decode('utf-8')
            except Exception:
                err = str(he)
            # keep a concise fallback
        except Exception:
            # network error or timeout — fall back to canned replies
            pass

    # Fallback canned replies (works offline or when OpenAI not configured)
    lm = message.lower()
    if 'coffee' in lm:
        reply = "Coffee machine beans are low (approx 12%). Water level is 68% and milk 45%. Would you like me to create a restock order?"
    elif 'temperature' in lm or 'temp' in lm:
        reply = "The current office temperature is 22°C. I can set a new target if you tell me the desired temperature."
    elif 'presence' in lm or 'who' in lm or 'in office' in lm:
        reply = "Currently 24 people are in the office and 3 are out. I can show the list or export attendance."
    elif 'stock' in lm or 'low' in lm or 'order' in lm:
        reply = "Low stock items: Coffee Beans, Paper. I can prepare a purchase order for these items."
    else:
        reply = "I can help with coffee, temperature, stock, and presence. Try asking something like: 'How much coffee is left?'"

    return jsonify({"reply": reply}), 200
