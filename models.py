# models.py - SQLAlchemy models
from datetime import datetime
from app import db
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.event import listens_for
from sqlalchemy.sql import func
import enum


# Base timestamp mixin
class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Office Management
class Office(db.Model, TimestampMixin):
    __tablename__ = 'offices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(400))
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Track temperature sensor and coffee machines in office
    temperature_sensors = relationship('TemperatureSensor', backref='office')
    coffee_machines = relationship('CoffeeMachine', backref='office')
    stock_locations = relationship('StockLocation', backref='office')
    employees = relationship('Employee', backref='office')

    manager = relationship('User', backref='managed_offices')
    
    def get_current_occupancy(self):
        """Get current occupancy count from presence logs"""
        from sqlalchemy import and_
        from datetime import datetime
        present_employees = (PresenceLog.query
            .join(Employee, Employee.user_id == PresenceLog.user_id)
            .filter(and_(
                Employee.office_id == self.id,
                PresenceLog.status == PresenceStatus.IN,
                PresenceLog.created_at <= datetime.utcnow()
            ))
            .count())
        present_visitors = (SafetyVisitor.query
            .filter_by(office_id=self.id, status='checked_in')
            .count())
        return present_employees + present_visitors

class Asset(db.Model, TimestampMixin):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    serial = db.Column(db.String(200))
    status = db.Column(db.String(100), default='available')  # available, in_use, maintenance, retired
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'), nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    office = relationship('Office', backref='assets')
    assigned_to = relationship('User', backref='assigned_assets')

class Booking(db.Model, TimestampMixin):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    resource = db.Column(db.String(200), nullable=False)  # e.g. meeting room, projector
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    
    user = relationship('User', backref='bookings')

class Maintenance(db.Model, TimestampMixin):
    __tablename__ = 'maintenances'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(100), default='open')  # open, in_progress, closed
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    asset = relationship('Asset', backref='maintenances')
    assigned_to = relationship('User', backref='assigned_maintenance')

# User and Authentication
class User(db.Model, TimestampMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, index=True, nullable=False)
    name = db.Column(db.String(200), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    department = db.Column(db.String(100))
    avatar_url = db.Column(db.String(500))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Dashboard & Activity
class DashboardMetric(db.Model, TimestampMixin):
    __tablename__ = 'dashboard_metrics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    category = db.Column(db.String(100))  # e.g., 'presence', 'temperature', 'stock'
    display_order = db.Column(db.Integer, default=0)

class ActivityLog(db.Model, TimestampMixin):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_data = db.Column(db.JSON)
    
    user = relationship('User', backref='activities')
    
    @classmethod
    def create(cls, category, action, description, event_data=None):
        """Helper method to create activity logs"""
        log = cls(
            category=category,
            action=action,
            description=description,
            event_data=event_data
        )
        try:
            db.session.add(log)
            db.session.commit()
        except:
            pass  # Silently fail if db not available
        return log

# Employee Management
class Employee(db.Model, TimestampMixin):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True)
    phone = db.Column(db.String(50))
    role = db.Column(db.String(200))
    department = db.Column(db.String(100))
    status = db.Column(db.String(50), default='active')  # active, on_leave, terminated
    emergency_contact = db.Column(db.JSON)  # Store emergency contact details
    access_level = db.Column(db.Integer, default=1)  # Security access level
    
    user = relationship('User', backref='employee_profile')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_current_presence(self):
        """Get employee's current presence status"""
        latest_log = (PresenceLog.query
            .filter_by(user_id=self.user_id)
            .order_by(PresenceLog.created_at.desc())
            .first())
        return latest_log.status if latest_log else None
    
    def record_presence(self, status, location=None, notes=None):
        """Record new presence status"""
        log = PresenceLog(
            user_id=self.user_id,
            status=status,
            location=location or self.office.name,
            notes=notes
        )
        db.session.add(log)
        db.session.commit()
        return log

# Coffee Machine Management
class CoffeeMachine(db.Model, TimestampMixin):
    __tablename__ = 'coffee_machines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    location_detail = db.Column(db.String(100))  # Specific location within office
    status = db.Column(db.String(50), default='operational')  # operational, maintenance, offline
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    bean_level = db.Column(db.Float)  # percentage
    water_level = db.Column(db.Float)  # percentage
    milk_level = db.Column(db.Float)  # percentage
    total_drinks = db.Column(db.Integer, default=0)
    
    def needs_restock(self):
        """Check if machine needs restocking"""
        threshold = 20.0  # 20% threshold for restocking
        if (self.bean_level <= threshold or 
            self.water_level <= threshold or 
            self.milk_level <= threshold):
            # Create activity log
            ActivityLog.create(
                category='coffee',
                action='restock_needed',
                description=f'Coffee machine {self.name} needs restocking',
                event_data={
                    'bean_level': self.bean_level,
                    'water_level': self.water_level,
                    'milk_level': self.milk_level
                }
            )
            return True
        return False
    
    def check_maintenance(self):
        """Check if maintenance is needed"""
        from datetime import datetime
        if (self.next_maintenance and 
            self.next_maintenance <= datetime.utcnow()):
            # Create activity log
            ActivityLog.create(
                category='coffee',
                action='maintenance_needed',
                description=f'Coffee machine {self.name} needs maintenance',
                event_data={
                    'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
                    'next_maintenance': self.next_maintenance.isoformat()
                }
            )
            return True
        return False

class CoffeeOrder(db.Model, TimestampMixin):
    __tablename__ = 'coffee_orders'
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('coffee_machines.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    drink_type = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50))
    extras = db.Column(db.JSON)  # e.g., {"extra_shot": true, "syrup": "vanilla"}
    status = db.Column(db.String(50), default='pending')  # pending, brewing, completed, failed
    
    machine = relationship('CoffeeMachine', backref='orders')
    user = relationship('User', backref='coffee_orders')

# Temperature Monitoring
class MeetingRoom(db.Model, TimestampMixin):
    __tablename__ = 'meeting_rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    floor = db.Column(db.Integer, nullable=False)  # Floor number
    capacity = db.Column(db.Integer)  # Room capacity
    target_temperature = db.Column(db.Float, default=22.0)  # Target temperature in Celsius
    current_temperature = db.Column(db.Float)  # Current temperature
    humidity = db.Column(db.Float)  # Current humidity percentage
    hvac_status = db.Column(db.String(50), default='auto')  # auto, heating, cooling, off
    hvac_mode = db.Column(db.String(50), default='auto')  # auto, heat, cool, fan
    last_adjusted = db.Column(db.DateTime)
    
    office = relationship('Office', backref='meeting_rooms')
    
    def adjust_temperature(self, new_target):
        """Adjust the target temperature for the room"""
        old_target = self.target_temperature
        self.target_temperature = new_target
        self.last_adjusted = datetime.utcnow()
        
        # Determine HVAC action based on current vs target
        if self.current_temperature and new_target:
            diff = self.current_temperature - new_target
            if diff > 1:
                self.hvac_status = 'cooling'
            elif diff < -1:
                self.hvac_status = 'heating'
            else:
                self.hvac_status = 'auto'
        
        # Log the change
        ActivityLog.create(
            category='temperature',
            action='temperature_adjusted',
            description=f'Temperature adjusted in {self.name} from {old_target}°C to {new_target}°C',
            event_data={
                'room_id': self.id,
                'room_name': self.name,
                'old_target': old_target,
                'new_target': new_target,
                'current_temp': self.current_temperature
            }
        )
        db.session.commit()
    
    def get_comfort_status(self):
        """Get comfort status based on temperature and humidity"""
        if not self.current_temperature or not self.humidity:
            return 'unknown'
        
        temp_ok = abs(self.current_temperature - self.target_temperature) <= 1.5
        humidity_ok = 30 <= self.humidity <= 60
        
        if temp_ok and humidity_ok:
            return 'comfortable'
        elif temp_ok or humidity_ok:
            return 'moderate'
        else:
            return 'uncomfortable'

class TemperatureSensor(db.Model, TimestampMixin):
    __tablename__ = 'temperature_sensors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location_detail = db.Column(db.String(100))
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('meeting_rooms.id'))  # Link to meeting room
    status = db.Column(db.String(50), default='active')  # active, offline, maintenance
    sensor_type = db.Column(db.String(50))  # 'wifi', 'wired', 'external'
    ip_address = db.Column(db.String(50))  # For WiFi sensors
    mac_address = db.Column(db.String(50))  # For device identification
    last_connection = db.Column(db.DateTime)
    calibration_offset = db.Column(db.Float, default=0.0)  # Temperature calibration offset
    
    room = relationship('MeetingRoom', backref='sensors')
    
    def get_latest_reading(self):
        return (TemperatureReading.query
                .filter_by(sensor_id=self.id)
                .order_by(TemperatureReading.created_at.desc())
                .first())

class WeatherStation(db.Model, TimestampMixin):
    __tablename__ = 'weather_stations'
    id = db.Column(db.Integer, primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    api_provider = db.Column(db.String(50))  # 'google', 'openweathermap', etc.
    location_name = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    last_update = db.Column(db.DateTime)
    api_key = db.Column(db.String(200))
    update_interval = db.Column(db.Integer, default=300)  # Update interval in seconds
    
    office = relationship('Office', backref='weather_station')
    
    def get_latest_weather(self):
        return (WeatherData.query
                .filter_by(station_id=self.id)
                .order_by(WeatherData.created_at.desc())
                .first())

class WeatherData(db.Model, TimestampMixin):
    __tablename__ = 'weather_data'
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('weather_stations.id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    wind_direction = db.Column(db.Float)
    description = db.Column(db.String(200))
    condition_code = db.Column(db.String(50))  # Weather condition code from API
    
    station = relationship('WeatherStation', backref='readings')

class TemperatureReading(db.Model, TimestampMixin):
    __tablename__ = 'temperature_readings'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('temperature_sensors.id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float)
    comfort_index = db.Column(db.Float)
    weather_data_id = db.Column(db.Integer, db.ForeignKey('weather_data.id'))  # Link to external weather
    
    sensor = relationship('TemperatureSensor', backref='readings')
    weather_data = relationship('WeatherData', backref='indoor_readings')
    
    def calculate_comfort_index(self):
        """Calculate comfort index based on temperature and humidity"""
        if self.temperature is None or self.humidity is None:
            return None
            
        # Simplified comfort index calculation
        # Based on temperature and humidity relationship
        temp = self.temperature
        humidity = self.humidity
        
        # Base comfort score (0-100)
        if temp < 18:
            comfort = 40 - (18 - temp) * 2  # Too cold
        elif temp > 26:
            comfort = 40 - (temp - 26) * 2  # Too hot
        else:
            comfort = 100 - abs(22 - temp) * 5  # Ideal range
            
        # Adjust for humidity
        if humidity < 30:
            comfort -= (30 - humidity)  # Too dry
        elif humidity > 60:
            comfort -= (humidity - 60)  # Too humid
            
        self.comfort_index = max(0, min(100, comfort))
        return self.comfort_index

# Stock Management
class StockLocation(db.Model, TimestampMixin):
    __tablename__ = 'stock_locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    area = db.Column(db.String(100))  # e.g. 'warehouse', 'storage room', 'kitchen'
    description = db.Column(db.Text)

class StockCategory(db.Model, TimestampMixin):
    __tablename__ = 'stock_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('stock_categories.id'))
    
    # Self-referential relationship for category hierarchy
    subcategories = relationship('StockCategory', 
        backref=db.backref('parent', remote_side=[id])
    )
    
class StockItem(db.Model, TimestampMixin):
    __tablename__ = 'stock_items'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('stock_categories.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('stock_locations.id'))
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    unit = db.Column(db.String(50))
    min_quantity = db.Column(db.Float, default=0)
    quantity = db.Column(db.Float, default=0)
    reorder_point = db.Column(db.Float)
    last_restock = db.Column(db.DateTime)
    supplier = db.Column(db.String(200))
    unit_cost = db.Column(db.Float)
    
    category = relationship('StockCategory', backref='items')
    location = relationship('StockLocation', backref='items')
    
    def get_status(self):
        """Get current stock status"""
        if self.quantity <= 0:
            return 'Critical'
        elif self.reorder_point and self.quantity <= self.reorder_point:
            return 'Low'
        else:
            return 'OK'
    
    def get_total_value(self):
        """Get total value of current stock"""
        if self.unit_cost and self.quantity:
            return round(self.unit_cost * self.quantity, 2)
        return 0.0
    
    def needs_reorder(self):
        """Check if item needs reordering"""
        return self.reorder_point and self.quantity <= self.reorder_point
    
    def check_stock_level(self):
        """Check if stock needs reordering and create activity log"""
        if self.needs_reorder():
            # Create activity log
            ActivityLog.create(
                category='stock',
                action='reorder_needed',
                description=f'Stock item {self.name} needs reordering',
                event_data={
                    'item_id': self.id,
                    'current_quantity': self.quantity,
                    'reorder_point': self.reorder_point
                }
            )
            return True
        return False
    
    def add_stock(self, quantity, reference='Manual restock', notes=None, user_id=None):
        """Add stock to this item"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        old_quantity = self.quantity
        self.quantity += quantity
        self.last_restock = datetime.utcnow()
        
        # Create transaction record
        transaction = StockTransaction(
            item_id=self.id,
            user_id=user_id,
            type='in',
            quantity=quantity,
            reference=reference,
            notes=notes or f'Added {quantity} {self.unit}'
        )
        
        db.session.add(transaction)
        return transaction
    
    def consume_stock(self, quantity, reference='Consumption', notes=None, user_id=None):
        """Remove stock from this item"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.quantity < quantity:
            raise ValueError("Insufficient stock")
        
        old_quantity = self.quantity
        self.quantity -= quantity
        
        # Create transaction record
        transaction = StockTransaction(
            item_id=self.id,
            user_id=user_id,
            type='out',
            quantity=quantity,
            reference=reference,
            notes=notes or f'Consumed {quantity} {self.unit}'
        )
        
        db.session.add(transaction)
        return transaction

class StockTransaction(db.Model, TimestampMixin):
    __tablename__ = 'stock_transactions'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(50), nullable=False)  # in, out, adjustment
    quantity = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100))  # e.g., order number, adjustment reason
    notes = db.Column(db.Text)
    
    item = relationship('StockItem', backref='transactions')
    user = relationship('User', backref='stock_transactions')

class StockOrder(db.Model, TimestampMixin):
    __tablename__ = 'stock_orders'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('stock_items.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    supplier = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)  # kg, g, liters, ml, pieces, etc.
    weight_or_volume = db.Column(db.Float)  # Store actual weight/volume measurement
    measurement_unit = db.Column(db.String(20))  # g, kg, ml, l for weight/volume
    priority = db.Column(db.String(20), default='normal')  # normal, urgent, critical
    status = db.Column(db.String(50), default='pending')  # pending, ordered, delivered, cancelled
    expected_delivery = db.Column(db.DateTime)
    order_reference = db.Column(db.String(100))
    total_cost = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    item = relationship('StockItem', backref='orders')
    user = relationship('User', backref='stock_orders')
    
    def mark_delivered(self, user_id=None):
        """Mark order as delivered and update stock"""
        if self.status != 'pending':
            raise ValueError("Only pending orders can be marked as delivered")
        
        self.status = 'delivered'
        # Add stock to the item
        self.item.add_stock(
            quantity=self.quantity,
            reference=f'Order delivered: {self.order_reference or self.id}',
            notes=f'Delivered from {self.supplier}',
            user_id=user_id
        )
    
    def cancel_order(self, reason=None):
        """Cancel the order"""
        if self.status == 'delivered':
            raise ValueError("Cannot cancel delivered orders")
        
        self.status = 'cancelled'
        if reason:
            self.notes = f"{self.notes or ''}\nCancelled: {reason}".strip()

# Presence Tracking
class PresenceStatus(enum.Enum):
    IN = 'in'
    OUT = 'out'
    REMOTE = 'remote'
    MEETING = 'meeting'
    BREAK = 'break'

class PresenceLog(db.Model, TimestampMixin):
    __tablename__ = 'presence_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(PresenceStatus), nullable=False)
    location = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    user = relationship('User', backref='presence_logs')

class SafetyVisitor(db.Model, TimestampMixin):
    __tablename__ = 'safety_visitors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    office_id = db.Column(db.Integer, db.ForeignKey('offices.id'))
    checkin_time = db.Column(db.DateTime, nullable=False)
    checkout_time = db.Column(db.DateTime)
    badge_number = db.Column(db.String(100))
    purpose = db.Column(db.String(200))  # Purpose of visit
    expected_duration = db.Column(db.Integer)  # Expected duration in minutes
    status = db.Column(db.String(50), default='checked_in')  # checked_in, checked_out
    access_areas = db.Column(db.JSON)  # Areas visitor has access to
    vehicle_info = db.Column(db.JSON)  # Parking/vehicle details if applicable
    
    host = relationship('User', backref='hosted_visitors')
    office = relationship('Office', backref='visitors')
    
    def is_overdue(self):
        """Check if visitor has overstayed expected duration"""
        from datetime import datetime, timedelta
        if (self.status == 'checked_in' and self.expected_duration and
            datetime.utcnow() > self.checkin_time + timedelta(minutes=self.expected_duration)):
            # Create activity log
            ActivityLog.create(
                category='safety',
                action='visitor_overdue',
                description=f'Visitor {self.name} has exceeded expected duration',
                event_data={
                    'visitor_id': self.id,
                    'expected_duration': self.expected_duration,
                    'actual_duration': (datetime.utcnow() - self.checkin_time).total_seconds() / 60
                }
            )
            return True
        return False

class SafetyEvent(db.Model, TimestampMixin):
    __tablename__ = 'safety_events'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)  # drill, emergency, incident
    status = db.Column(db.String(50), default='active')  # active, resolved, drill_complete
    initiated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    initiated_by = relationship('User', foreign_keys=[initiated_by_id], backref='initiated_safety_events')
    resolved_by = relationship('User', foreign_keys=[resolved_by_id], backref='resolved_safety_events')

# Event listeners for history tracking
@listens_for(StockItem, 'before_update')
def stock_item_history(mapper, connection, target):
    if target.quantity != target._quantity:
        ActivityLog.create(
            category='stock',
            action='quantity_change',
            description=f'Stock quantity changed for {target.name}',
            metadata={
                'item_id': target.id,
                'old_quantity': target._quantity,
                'new_quantity': target.quantity
            }
        )

# Temporarily disabled to avoid transaction conflicts during seeding
# @listens_for(PresenceLog, 'after_insert')
# def presence_activity(mapper, connection, target):
#     ActivityLog.create(
#         category='presence',
#         action='status_change',
#         description=f'Presence status changed to {target.status.value}',
#         event_data={
#             'user_id': target.user_id,
#             'status': target.status.value
#         }
#     )
