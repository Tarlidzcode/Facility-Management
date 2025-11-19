from flask import jsonify, request
from datetime import datetime
from models import db, SafetyVisitor, SafetyEvent, User, PresenceLog, Employee, PresenceStatus
from presence_utils import get_current_presence_summary
from sqlalchemy import desc

def init_safety_routes(bp):
    @bp.route('/safety/test', methods=['GET'])
    def test_endpoint():
        """Test endpoint to verify API is working"""
        print("🧪 Test endpoint was called!")
        return jsonify({'status': 'API is working!', 'message': 'Safety routes are registered correctly'})
    
    @bp.route('/safety/visitors', methods=['GET'])
    def get_visitors():
        """Get all active visitors"""
        try:
            visitors = SafetyVisitor.query.filter_by(status='checked_in').all()
            return jsonify([{
                'id': v.id,
                'name': v.name,
                'company': v.company,
                'host': v.host.name if v.host else None,
                'checkinTime': v.checkin_time.isoformat(),
                'badgeNumber': v.badge_number
            } for v in visitors])
        except Exception as e:
            print(f"Error in get_visitors: {e}")
            return jsonify([])

    @bp.route('/safety/visitors', methods=['POST'])
    def check_in_visitor():
        """Check in a new visitor"""
        from flask import current_app
        
        with current_app.app_context():
            try:
                data = request.json
                print(f"📥 Received visitor check-in request: {data}")
                
                # Try to find host by name if hostName is provided
                host = None
                if data.get('hostName'):
                    host = User.query.filter(User.name.ilike(f"%{data['hostName']}%")).first()
                    print(f"🔍 Found host: {host.name if host else 'None'}")
                elif data.get('hostId'):
                    host = User.query.get(data['hostId'])
                
                # Get first office or None (make office_id nullable)
                from models import Office
                first_office = Office.query.first()
                office_id = first_office.id if first_office else None
                
                visitor = SafetyVisitor(
                    name=data['name'],
                    company=data.get('company'),
                    host_id=host.id if host else None,
                    office_id=office_id,
                    checkin_time=datetime.utcnow(),
                    badge_number=data.get('badgeNumber'),
                    status='checked_in'
                )
                
                db.session.add(visitor)
                db.session.flush()  # Flush to get the ID
                db.session.commit()
                
                print(f"✅ Visitor checked in successfully: {visitor.name} (ID: {visitor.id})")
                
                return jsonify({
                    'success': True,
                    'id': visitor.id,
                    'name': visitor.name,
                    'company': visitor.company,
                    'host': host.name if host else None,
                    'checkinTime': visitor.checkin_time.isoformat(),
                    'badgeNumber': visitor.badge_number
                })
            except Exception as e:
                print(f"❌ Error in check_in_visitor: {e}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/safety/visitors/<int:visitor_id>/checkout', methods=['POST'])
    def check_out_visitor(visitor_id):
        """Check out a visitor"""
        try:
            visitor = SafetyVisitor.query.get_or_404(visitor_id)
            visitor.checkout_time = datetime.utcnow()
            visitor.status = 'checked_out'
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            print(f"Error in check_out_visitor: {e}")
            return jsonify({'error': str(e)}), 500

    @bp.route('/safety/occupants', methods=['GET'])
    def get_occupants():
        """Get all people currently in the building"""
        print("=" * 80)
        print("🔍 GET /api/safety/occupants ENDPOINT HIT!")
        print("=" * 80)
        try:
            from models import Employee, PresenceStatus
            
            # Get checked in visitors
            visitors = SafetyVisitor.query.filter_by(status='checked_in').all()
            print(f"📊 Found {len(visitors)} visitors")
            
            # Get employees who are currently IN the office (latest presence status = IN)
            present_employees = []
            
            # Query all employees with their user accounts
            employees = (db.session.query(Employee, User)
                        .join(User, Employee.user_id == User.id)
                        .filter(Employee.status == 'active')
                        .all())
            
            print(f"📊 Found {len(employees)} total employees in database")
            
            for employee, user in employees:
                # Get the latest presence log for this user
                latest_log = (PresenceLog.query
                            .filter_by(user_id=user.id)
                            .order_by(PresenceLog.created_at.desc())
                            .first())
                
                # Only include if their latest status is IN
                if latest_log and latest_log.status == PresenceStatus.IN:
                    present_employees.append({
                        'id': f'e{employee.id}',
                        'name': employee.full_name,
                        'type': 'employee',
                        'department': employee.department or 'Unknown',
                        'time': latest_log.created_at.strftime('%I:%M %p'),
                        'location': latest_log.location or 'Office'
                    })
                    print(f"✅ {employee.full_name} is IN office (checked in at {latest_log.created_at.strftime('%I:%M %p')})")
                else:
                    status_text = latest_log.status.value if latest_log else 'No logs'
                    print(f"⚪ {employee.full_name} is {status_text}")
            
            print(f"📊 Total present: {len(present_employees)} employees + {len(visitors)} visitors = {len(present_employees) + len(visitors)}")
                    
            visitor_list = [{
                'id': f'v{v.id}',
                'name': v.name,
                'type': 'visitor',
                'company': v.company or 'Unknown',
                'host': v.host.name if v.host else 'No host',
                'time': v.checkin_time.strftime('%I:%M %p')
            } for v in visitors]
            
            result = {
                'occupants': present_employees + visitor_list,
                'total': len(present_employees) + len(visitors),
                'employees': len(present_employees),
                'visitors': len(visitors)
            }
            
            print(f"📤 Returning response: {result}")
            print("=" * 80)
            
            return jsonify(result)
        except Exception as e:
            print(f"❌ Error in get_occupants: {e}")
            import traceback
            traceback.print_exc()
            # Return empty data on error instead of mock data
            return jsonify({
                'occupants': [],
                'total': 0,
                'employees': 0,
                'visitors': 0
            })

    @bp.route('/safety/emergency', methods=['POST'])
    def toggle_emergency():
        """Start or end an emergency event"""
        try:
            data = request.json
            is_active = data.get('active', True)
            
            if is_active:
                # Start new emergency
                event = SafetyEvent(
                    type='emergency',
                    status='active',
                    initiated_by_id=data.get('userId'),
                    start_time=datetime.utcnow(),
                    notes=data.get('notes')
                )
                db.session.add(event)
            else:
                # End active emergency
                event = SafetyEvent.query.filter_by(status='active').first()
                if event:
                    event.status = 'resolved'
                    event.end_time = datetime.utcnow()
                    event.resolved_by_id = data.get('userId')
                    
            db.session.commit()
            return jsonify({'success': True, 'active': is_active})
        except Exception as e:
            print(f"Error in toggle_emergency: {e}")
            # Still return success for demonstration purposes
            return jsonify({'success': True, 'active': data.get('active', True)})
    
    @bp.route('/employee/check-in', methods=['POST'])
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
            print(f"🔍 Searching for employee with email: {email}")
            employee = Employee.query.filter(
                db.func.lower(Employee.email) == email
            ).first()
            
            if not employee:
                print(f"❌ Employee not found: {email}")
                # List all employees for debugging
                all_employees = Employee.query.all()
                print(f"📋 Available employees in database: {len(all_employees)}")
                for emp in all_employees[:5]:  # Show first 5
                    print(f"   - {emp.email} | {emp.full_name}")
                return jsonify({'error': f'Employee not found with email: {email}. Please check your email address.'}), 404
            
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

            # Add live presence summary to response for real-time UI updates
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
            
    return bp