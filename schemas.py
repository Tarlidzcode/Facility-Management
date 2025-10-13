# schemas.py - marshmallow schemas for serialization
from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    name = fields.Str()
    is_admin = fields.Bool()
    created_at = fields.DateTime()

class OfficeSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    address = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime()

class EmployeeSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    phone = fields.Str()
    role = fields.Str()
    office_id = fields.Int()
    created_at = fields.DateTime()

class AssetSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    serial = fields.Str()
    status = fields.Str()
    office_id = fields.Int()
    created_at = fields.DateTime()

class BookingSchema(Schema):
    id = fields.Int()
    resource = fields.Str()
    user_id = fields.Int()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    notes = fields.Str()
    created_at = fields.DateTime()

class MaintenanceSchema(Schema):
    id = fields.Int()
    asset_id = fields.Int()
    description = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime()
