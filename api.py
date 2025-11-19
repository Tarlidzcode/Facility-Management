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
from flask import Response

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


# --- Lightweight demo endpoints for stock/order actions used by the frontend ---
@api_bp.route('/stock/remove', methods=['POST'])
def remove_stock_item():
    # This is a demo/stub endpoint. In a real app you'd authenticate and
    # remove the item from the DB. For the demo return success so the UI
    # can remove the row.
    payload = request.get_json() or {}
    item = payload.get('item')
    if not item:
        return jsonify({'error': 'missing item'}), 400
    # Log to server console for visibility during development
    print(f"[demo] remove_stock_item called for: {item}")
    return jsonify({'msg': 'removed', 'item': item}), 200


_demo_orders = {}
_demo_order_seq = 1


@api_bp.route('/orders', methods=['POST'])
def create_order():
    # Demo create order — doesn't persist to DB beyond in-memory dict
    global _demo_order_seq
    payload = request.get_json() or {}
    supplier = payload.get('supplier')
    if not supplier:
        return jsonify({'error': 'missing supplier'}), 400
    order_id = _demo_order_seq
    _demo_order_seq += 1
    order = {
        'id': order_id,
        'supplier': supplier,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat()
    }
    _demo_orders[order_id] = order
    print(f"[demo] created order: {order}")
    return jsonify({'order_id': order_id, 'order': order}), 201


@api_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    # Demo cancel — remove from in-memory store
    o = _demo_orders.get(order_id)
    if not o:
        return jsonify({'error': 'order not found'}), 404
    # mark cancelled
    o['status'] = 'cancelled'
    print(f"[demo] cancelled order {order_id}")
    # Optionally remove from store
    _demo_orders.pop(order_id, None)
    return jsonify({'msg': 'cancelled', 'order_id': order_id}), 200


# Demo endpoint: list supported suppliers (for completeness)
@api_bp.route('/suppliers', methods=['GET'])
def list_suppliers():
    suppliers = [
        'Pick N Pay', 'Checkers', 'Shoprite', 'Woolworths', 'Spar', 'Makro'
    ]
    return jsonify({'suppliers': suppliers}), 200


# Simulated external order endpoint: would contact merchant APIs in a real app
@api_bp.route('/external_order', methods=['POST'])
def external_order():
    data = request.get_json() or {}
    supplier = data.get('supplier')
    items = data.get('items') or []
    if not supplier or not items:
        return jsonify({'error': 'missing supplier or items'}), 400
    # Simulate different merchant behaviours — simple success/failure heuristics
    # e.g. Make 'Makro' respond slowly or with partial success
    global _demo_order_seq, _demo_orders
    order_id = _demo_order_seq
    _demo_order_seq += 1
    status = 'accepted'
    message = f'Order placed with {supplier}. Estimated fulfilment: 2-5 days.'
    if supplier == 'Makro' and len(items) > 3:
        status = 'partial'
        message = f'{supplier} accepted part of the order. Check merchant portal for details.'
    # store in demo orders
    _demo_orders[order_id] = {'id': order_id, 'supplier': supplier, 'items': items, 'status': status}
    print(f"[demo] external_order -> {supplier} items={len(items)} status={status}")
    return jsonify({'order_id': order_id, 'status': status, 'message': message}), 201


# AI assistant endpoint for office management questions
# Uses Azure OpenAI to provide intelligent responses about the app
@api_bp.route('/ai', methods=['POST'])
def ai_reply():
    """
    AI Assistant endpoint using Azure OpenAI
    Answers questions about the office management system with REAL data
    """
    try:
        from ai import get_ai_response
        from models import Employee, User, PresenceLog, PresenceStatus, StockItem, CoffeeOrder, TemperatureReading, TemperatureSensor
        from sqlalchemy import desc, func
        from datetime import datetime, timedelta
        
        # Get user message
        payload = request.get_json() or {}
        message = (payload.get('message') or '').strip()
        
        if not message:
            return jsonify({
                "reply": "👋 Hello! I'm your Office Management AI Assistant! Ask me about coffee, temperature, employees, stock, or any features."
            }), 200
        
        # Gather REAL office data from database
        context_data = {}
        
        try:
            # PRESENCE DATA - Who's in the office?
            employees_in = db.session.query(Employee, User).join(User).filter(Employee.status == 'active').all()
            present_employees = []
            total_checked_in = 0
            
            for emp, user in employees_in:
                latest_log = PresenceLog.query.filter_by(user_id=user.id).order_by(desc(PresenceLog.created_at)).first()
                if latest_log and latest_log.status == PresenceStatus.IN:
                    present_employees.append({
                        'name': emp.full_name,
                        'department': emp.department,
                        'time': latest_log.created_at.strftime('%I:%M %p')
                    })
                    total_checked_in += 1
            
            context_data['presence'] = {
                'total_in_office': total_checked_in,
                'total_employees': len(employees_in),
                'employees_present': present_employees[:10]  # Limit to 10 for context
            }
            
            # STOCK DATA - Low stock items
            low_stock_items = StockItem.query.filter(
                StockItem.quantity <= StockItem.reorder_point
            ).limit(10).all()
            
            context_data['stock'] = {
                'low_stock_count': len(low_stock_items),
                'low_stock_items': [{
                    'name': item.name,
                    'quantity': item.quantity,
                    'reorder_point': item.reorder_point,
                    'unit': item.unit
                } for item in low_stock_items]
            }
            
            # COFFEE DATA - Recent orders and usage
            today = datetime.now().date()
            todays_orders = CoffeeOrder.query.filter(
                func.date(CoffeeOrder.created_at) == today
            ).count()
            
            recent_orders = CoffeeOrder.query.order_by(desc(CoffeeOrder.created_at)).limit(5).all()
            
            context_data['coffee'] = {
                'orders_today': todays_orders,
                'recent_orders': [{
                    'user': order.user.name if order.user else 'Unknown',
                    'type': order.coffee_type,
                    'time': order.created_at.strftime('%I:%M %p')
                } for order in recent_orders if order.user]
            }
            
            # TEMPERATURE DATA - Latest readings
            latest_readings = TemperatureReading.query.order_by(desc(TemperatureReading.created_at)).limit(5).all()
            
            if latest_readings:
                context_data['temperature'] = {
                    'latest_readings': [{
                        'sensor': reading.sensor.name if reading.sensor else 'Unknown',
                        'temperature': reading.temperature,
                        'humidity': reading.humidity,
                        'time': reading.created_at.strftime('%I:%M %p')
                    } for reading in latest_readings if reading.sensor]
                }
            
        except Exception as data_error:
            print(f"Error gathering context data: {data_error}")
            # Continue with whatever data we have
        
        # Get AI response with REAL data
        ai_response = get_ai_response(message, context_data if context_data else None)
        
        return jsonify({"reply": ai_response}), 200
        
    except Exception as e:
        print(f"AI Assistant Error: {e}")
        import traceback
        print(traceback.format_exc())
        # Fallback response
        return jsonify({
            "reply": "🤖 I'm having trouble right now, but I'm here to help with your office management questions! Try asking about coffee, temperature, employees, or stock management."
        }), 200


# Streaming AI assistant endpoint (Server-Sent Events)
@api_bp.route('/ai_stream', methods=['POST'])
def ai_reply_stream():
    """Stream AI assistant response as SSE for real-time typing effect."""
    try:
        from ai import stream_ai_response, get_ai_response
        from models import Employee, User, PresenceLog, PresenceStatus, StockItem, CoffeeOrder, TemperatureReading, TemperatureSensor
        from sqlalchemy import desc, func
        from datetime import datetime
    except Exception as e:  # noqa: BLE001
        return jsonify({'error': f'Initialization failed: {e}'}), 500

    payload = request.get_json() or {}
    message = (payload.get('message') or '').strip()
    if not message:
        return jsonify({'error': 'Empty message'}), 400

    # Prepare context (reuse logic but simplified to avoid heavy duplication)
    context_data = {}
    try:
        # Presence
        employees_in = db.session.query(Employee, User).join(User).filter(Employee.status == 'active').all()
        from sqlalchemy import desc as _desc, func as _func  # local aliasing
        present_employees = []
        total_checked_in = 0
        for emp, user in employees_in:
            latest_log = PresenceLog.query.filter_by(user_id=user.id).order_by(_desc(PresenceLog.created_at)).first()
            if latest_log and latest_log.status == PresenceStatus.IN:
                present_employees.append({
                    'name': emp.full_name,
                    'department': emp.department,
                    'time': latest_log.created_at.strftime('%I:%M %p')
                })
                total_checked_in += 1
        context_data['presence'] = {
            'total_in_office': total_checked_in,
            'total_employees': len(employees_in),
            'employees_present': present_employees[:10]
        }
        # Stock
        low_stock_items = StockItem.query.filter(StockItem.quantity <= StockItem.reorder_point).limit(10).all()
        context_data['stock'] = {
            'low_stock_count': len(low_stock_items),
            'low_stock_items': [{
                'name': i.name,
                'quantity': i.quantity,
                'reorder_point': i.reorder_point,
                'unit': i.unit
            } for i in low_stock_items]
        }
        # Coffee
        today = datetime.now().date()
        todays_orders = CoffeeOrder.query.filter(func.date(CoffeeOrder.created_at) == today).count()
        recent_orders = CoffeeOrder.query.order_by(desc(CoffeeOrder.created_at)).limit(5).all()
        context_data['coffee'] = {
            'orders_today': todays_orders,
            'recent_orders': [{
                'user': o.user.name if o.user else 'Unknown',
                'type': o.coffee_type,
                'time': o.created_at.strftime('%I:%M %p')
            } for o in recent_orders if o.user]
        }
        # Temperature
        latest_readings = TemperatureReading.query.order_by(desc(TemperatureReading.created_at)).limit(3).all()
        if latest_readings:
            context_data['temperature'] = {
                'latest_readings': [{
                    'sensor': r.sensor.name if r.sensor else 'Unknown',
                    'temperature': r.temperature,
                    'humidity': r.humidity,
                    'time': r.created_at.strftime('%I:%M %p')
                } for r in latest_readings if r.sensor]
            }
    except Exception as e:  # noqa: BLE001
        print(f"Context build error (stream): {e}")

    def event_stream():  # inner generator
        try:
            for chunk in stream_ai_response(message, context_data if context_data else None):
                # Send each chunk as SSE data line
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
            # Signal completion
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:  # noqa: BLE001
            err_msg = f"Streaming error: {e}"
            yield f"data: {json.dumps({'error': err_msg, 'done': True})}\n\n"

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no'
    }
    return Response(event_stream(), headers=headers)
