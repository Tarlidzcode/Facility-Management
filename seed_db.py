# seed_db.py
from app import create_app, db
from models import User, Office, Employee, Asset

app = create_app()

with app.app_context():
    db.create_all()
    # create admin user if not exists
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(email='admin@example.com', name='Admin User', is_admin=True)
        admin.set_password('password123')
        db.session.add(admin)

    # create sample office
    if not Office.query.filter_by(name='Main Office').first():
        o = Office(name='Main Office', address='1 Central Ave', description='Headquarters')
        db.session.add(o)
        db.session.commit()

        e = Employee(first_name='Alice', last_name='Nomaxayi', email='alice@example.com', role='Manager', office_id=o.id)
        a = Asset(name='Projector A', serial='PRJ-001', status='available', office_id=o.id)
        db.session.add_all([e,a])
    db.session.commit()
    print("Seeded DB")
