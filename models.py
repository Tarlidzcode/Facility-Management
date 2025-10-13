# models.py - SQLAlchemy models
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, index=True, nullable=False)
    name = db.Column(db.String(200), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Office(db.Model):
    __tablename__ = 'offices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(400))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), unique=True)
    phone = db.Column(db.String(50))
    role = db.Column(db.String(200))
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    office = db.relationship('Office', backref=db.backref('employees', lazy='dynamic'))

class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    serial = db.Column(db.String(200))
    status = db.Column(db.String(100), default='available')  # available, in_use, maintenance, retired
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    office = db.relationship('Office', backref=db.backref('assets', lazy='dynamic'))

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    resource = db.Column(db.String(200), nullable=False)  # e.g. meeting room, projector
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('bookings', lazy='dynamic'))

class Maintenance(db.Model):
    __tablename__ = 'maintenances'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(100), default='open')  # open, in_progress, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    asset = db.relationship('Asset', backref=db.backref('maintenances', lazy='dynamic'))
