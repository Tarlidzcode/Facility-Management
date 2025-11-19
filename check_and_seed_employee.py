"""
Quick script to check if employees exist and seed if needed
"""
import os
import tempfile

# Set database path
temp_dir = tempfile.gettempdir()
db_path = os.path.join(temp_dir, "office_eathon.db")
os.environ['DATABASE_URL'] = f'sqlite:///{db_path.replace(chr(92), "/")}'

print(f"📁 Using database: {db_path}")

from app import create_app, db
from models import User, Employee, Office

app = create_app()

with app.app_context():
    print("\n🔍 Checking database...")
    
    # Check employees
    employees = Employee.query.all()
    print(f"\n👥 Total employees in database: {len(employees)}")
    
    if len(employees) == 0:
        print("\n⚠️  No employees found! Creating test employee...")
        
        # Check if office exists
        office = Office.query.first()
        if not office:
            print("Creating office...")
            office = Office(
                name="MRI Software Cape Town",
                address="123 Main St, Cape Town",
                latitude=-33.9249,
                longitude=18.4241
            )
            db.session.add(office)
            db.session.commit()
            print(f"✅ Created office: {office.name}")
        
        # Create user
        user = User(
            email='eathon.groenewald@mrisoftware.com',
            name='Eathon Groenewald'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created user: {user.email}")
        
        # Create employee
        employee = Employee(
            first_name='Eathon',
            last_name='Groenewald',
            email='eathon.groenewald@mrisoftware.com',
            department='Engineering',
            position='Software Developer',
            phone='0821234567',
            office_id=office.id,
            user_id=user.id
        )
        db.session.add(employee)
        db.session.commit()
        print(f"✅ Created employee: {employee.full_name}")
        
        print("\n✅ Test employee created successfully!")
    else:
        print("\n📋 Existing employees:")
        for emp in employees[:10]:
            print(f"   - {emp.email} | {emp.full_name} | Dept: {emp.department}")
            print(f"     User ID: {emp.user_id} | Office ID: {emp.office_id}")
    
    print(f"\n✅ Database ready! You can now use the login feature.")
    print(f"\n🔐 Test credentials:")
    test_emp = Employee.query.filter_by(email='eathon.groenewald@mrisoftware.com').first()
    if test_emp:
        print(f"   Email: {test_emp.email}")
        print(f"   Password: password123")
    else:
        print("   Email: (use any existing employee email above)")
        print("   Password: password123")
