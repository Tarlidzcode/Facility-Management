"""
Initialize database in temp directory to avoid path length issues
"""
import os
import sys
import tempfile
from pathlib import Path

# Get temp directory
temp_dir = tempfile.gettempdir()
db_path = os.path.join(temp_dir, "office_eathon.db")

print(f"Creating database at: {db_path}")

# Set environment variable
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

# Now import and create app
from app import create_app, db

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # Import models
    from models import User, Office
    
    # Check if admin exists
    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            email='admin@example.com',
            name='Admin User',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created")
    
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
        print("✅ Office created")
    
    print(f"\n✅ Database initialized at: {db_path}")
    print(f"📊 Total users: {User.query.count()}")
    print(f"🏢 Total offices: {Office.query.count()}")
