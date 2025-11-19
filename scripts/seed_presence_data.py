"""
Seed Presence Tracking Data
Creates employees and presence logs for the office management system
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models import User, Employee, Office, PresenceLog, PresenceStatus

def seed_presence_data():
    """Seed the database with employee and presence data"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting presence data seeding...")
        
        # Check if office exists, create if not
        office = Office.query.filter_by(name='Cape Town Pinelands Office').first()
        if not office:
            office = Office(
                name='Cape Town Pinelands Office',
                address='Pinelands, Cape Town, South Africa',
                description='Main office location',
                location='-33.9249,18.4241'
            )
            db.session.add(office)
            db.session.commit()
            print(f"✅ Created office: {office.name}")
        else:
            print(f"✅ Office exists: {office.name}")
        
        # Define employees with departments
        employees_data = [
            # Business Operations
            {
                'first_name': 'Lilitha',
                'last_name': 'Nomaxayi',
                'email': 'lilitha.nomaxayi@mri.com',
                'department': 'Business Operations',
                'role': 'Business Operations Specialist',
                'phone': '+27 21 555 0101',
                'status': 'active'
            },
            {
                'first_name': 'Anshah',
                'last_name': 'Shabangu',
                'email': 'anshah.shabangu@mri.com',
                'department': 'Business Operations',
                'role': 'Business Operations Analyst',
                'phone': '+27 21 555 0102',
                'status': 'active'
            },
            # Data Management
            {
                'first_name': 'Eathon',
                'last_name': 'Groenewald',
                'email': 'eathon.groenewald@mri.com',
                'department': 'Data Management',
                'role': 'Data Management Specialist',
                'phone': '+27 21 555 0103',
                'status': 'active'
            },
            # Lease Administration
            {
                'first_name': 'Kayleigh',
                'last_name': 'Jonkers',
                'email': 'kayleigh.jonkers@mri.com',
                'department': 'Lease Administration',
                'role': 'Lease Administrator',
                'phone': '+27 21 555 0104',
                'status': 'active'
            },
            # GPS (Global Property Solutions)
            {
                'first_name': 'Stacy',
                'last_name': 'Clarke',
                'email': 'stacy.clarke@mri.com',
                'department': 'GPS',
                'role': 'GPS Specialist',
                'phone': '+27 21 555 0105',
                'status': 'active'
            },
            {
                'first_name': 'Amber-Lee',
                'last_name': 'November',
                'email': 'amber-lee.november@mri.com',
                'department': 'GPS',
                'role': 'GPS Analyst',
                'phone': '+27 21 555 0106',
                'status': 'active'
            },
            # Support
            {
                'first_name': 'Aden',
                'last_name': 'Weir',
                'email': 'aden.weir@mri.com',
                'department': 'Support',
                'role': 'Support Specialist',
                'phone': '+27 21 555 0107',
                'status': 'active'
            },
            {
                'first_name': 'Rushdeen',
                'last_name': 'White',
                'email': 'rushdeen.white@mri.com',
                'department': 'Support',
                'role': 'Support Engineer',
                'phone': '+27 21 555 0108',
                'status': 'active'
            },
            # Product Development
            {
                'first_name': 'Alex',
                'last_name': 'Abrahams',
                'email': 'alex.abrahams@mri.com',
                'department': 'Product Development',
                'role': 'Product Developer',
                'phone': '+27 21 555 0109',
                'status': 'active'
            },
            {
                'first_name': 'Sakhe',
                'last_name': 'Dudula',
                'email': 'sakhe.dudula@mri.com',
                'department': 'Product Development',
                'role': 'Senior Product Developer',
                'phone': '+27 21 555 0110',
                'status': 'active'
            }
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
                user.set_password('password123')  # Default password
                db.session.add(user)
                db.session.flush()
                print(f"✅ Created user: {user.name}")
            else:
                print(f"✅ User exists: {user.name}")
            
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
                    status=emp_data['status'],
                    access_level=1,
                    emergency_contact={
                        'name': 'Emergency Contact',
                        'phone': '+27 21 555 9999',
                        'relationship': 'Family'
                    }
                )
                db.session.add(employee)
                db.session.flush()
                print(f"✅ Created employee: {employee.full_name} - {employee.department}")
            else:
                print(f"✅ Employee exists: {employee.full_name}")
            
            created_employees.append((user, employee))
        
        db.session.commit()
        print(f"\n📊 Total employees created/verified: {len(created_employees)}")
        
        # Create presence logs for today
        print("\n🕐 Creating presence logs for today...")
        
        # Define who is currently in the office (60% of employees)
        in_office_count = int(len(created_employees) * 0.6)
        in_office_employees = random.sample(created_employees, in_office_count)
        
        # Generate check-in times between 7:00 AM and 10:00 AM today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        check_in_start = today + timedelta(hours=7)
        check_in_end = today + timedelta(hours=10)
        
        presence_logs_created = 0
        
        for user, employee in in_office_employees:
            # Random check-in time
            random_minutes = random.randint(0, int((check_in_end - check_in_start).total_seconds() / 60))
            check_in_time = check_in_start + timedelta(minutes=random_minutes)
            
            # Check if presence log already exists for today
            existing_log = PresenceLog.query.filter(
                PresenceLog.user_id == user.id,
                PresenceLog.created_at >= today
            ).first()
            
            if not existing_log:
                presence_log = PresenceLog(
                    user_id=user.id,
                    status=PresenceStatus.IN,
                    location=office.name,
                    notes=f"Checked in at {check_in_time.strftime('%I:%M %p')}",
                    created_at=check_in_time
                )
                db.session.add(presence_log)
                presence_logs_created += 1
                print(f"  ✅ {user.name} checked in at {check_in_time.strftime('%I:%M %p')}")
        
        # Create some employees who checked out (left early)
        checked_out_count = int(len(in_office_employees) * 0.2)
        if checked_out_count > 0:
            checked_out_employees = random.sample(in_office_employees, checked_out_count)
            
            for user, employee in checked_out_employees:
                # Random check-out time between 4:00 PM and 5:30 PM
                checkout_start = today + timedelta(hours=16)
                checkout_end = today + timedelta(hours=17, minutes=30)
                random_minutes = random.randint(0, int((checkout_end - checkout_start).total_seconds() / 60))
                checkout_time = checkout_start + timedelta(minutes=random_minutes)
                
                # Only add checkout if it's after current time or in the past
                if checkout_time <= datetime.now():
                    presence_log = PresenceLog(
                        user_id=user.id,
                        status=PresenceStatus.OUT,
                        location=office.name,
                        notes=f"Checked out at {checkout_time.strftime('%I:%M %p')}",
                        created_at=checkout_time
                    )
                    db.session.add(presence_log)
                    presence_logs_created += 1
                    print(f"  ✅ {user.name} checked out at {checkout_time.strftime('%I:%M %p')}")
        
        # Create some historical presence data (past week)
        print("\n📅 Creating historical presence logs (past 7 days)...")
        historical_logs = 0
        
        for days_ago in range(1, 8):
            past_date = today - timedelta(days=days_ago)
            
            # Random employees for each day (70-90% attendance)
            attendance_rate = random.uniform(0.7, 0.9)
            daily_attendance = int(len(created_employees) * attendance_rate)
            daily_employees = random.sample(created_employees, daily_attendance)
            
            for user, employee in daily_employees:
                # Morning check-in
                check_in_time = past_date + timedelta(hours=random.randint(7, 10), minutes=random.randint(0, 59))
                presence_log_in = PresenceLog(
                    user_id=user.id,
                    status=PresenceStatus.IN,
                    location=office.name,
                    notes=f"Checked in",
                    created_at=check_in_time
                )
                db.session.add(presence_log_in)
                historical_logs += 1
                
                # Evening check-out
                checkout_time = past_date + timedelta(hours=random.randint(16, 18), minutes=random.randint(0, 59))
                presence_log_out = PresenceLog(
                    user_id=user.id,
                    status=PresenceStatus.OUT,
                    location=office.name,
                    notes=f"Checked out",
                    created_at=checkout_time
                )
                db.session.add(presence_log_out)
                historical_logs += 1
        
        db.session.commit()
        
        print(f"\n✅ Created {presence_logs_created} presence logs for today")
        print(f"✅ Created {historical_logs} historical presence logs")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PRESENCE DATA SEEDING SUMMARY")
        print("="*60)
        print(f"Office: {office.name}")
        print(f"Total Employees: {len(created_employees)}")
        print(f"Currently In Office: {in_office_count - checked_out_count}")
        print(f"Checked Out Today: {checked_out_count}")
        print(f"\n📋 EMPLOYEES BY DEPARTMENT:")
        
        # Group by department
        departments = {}
        for user, employee in created_employees:
            dept = employee.department
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(employee.full_name)
        
        for dept, names in sorted(departments.items()):
            print(f"\n  {dept}:")
            for name in names:
                # Check if in office
                latest_log = PresenceLog.query.filter(
                    PresenceLog.user_id == User.query.filter_by(email=name.lower().replace(' ', '.') + '@mri.com').first().id,
                    PresenceLog.created_at >= today
                ).order_by(PresenceLog.created_at.desc()).first()
                
                status = "🟢 IN OFFICE" if latest_log and latest_log.status == PresenceStatus.IN else "🔴 NOT IN OFFICE"
                print(f"    • {name} - {status}")
        
        print("\n" + "="*60)
        print("✅ Presence data seeding completed successfully!")
        print("="*60)
        print("\n💡 Default password for all users: password123")
        print("🌐 Visit http://localhost:5001/presence to see the data\n")

if __name__ == '__main__':
    seed_presence_data()
