"""Update models with integrated relationships

Revision ID: 2023_10_23_update
Revises: 
Create Date: 2023-10-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2023_10_23_update'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add temperature sensor changes first
    op.add_column('temperature_sensors', sa.Column('office_id', sa.Integer(), nullable=True))
    op.add_column('temperature_sensors', sa.Column('location_detail', sa.String(length=100), nullable=True))
    op.create_foreign_key(None, 'temperature_sensors', 'offices', ['office_id'], ['id'])
    op.drop_column('temperature_sensors', 'location')
    
    # Create stock_locations table
    op.create_table('stock_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('office_id', sa.Integer(), nullable=True),
        sa.Column('area', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['office_id'], ['offices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add new columns to existing tables
    op.add_column('stock_categories', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'stock_categories', 'stock_categories', ['parent_id'], ['id'])

    op.add_column('stock_items', sa.Column('location_id', sa.Integer(), nullable=True))
    op.add_column('stock_items', sa.Column('supplier', sa.String(length=200), nullable=True))
    op.add_column('stock_items', sa.Column('unit_cost', sa.Float(), nullable=True))
    op.create_foreign_key(None, 'stock_items', 'stock_locations', ['location_id'], ['id'])

    op.add_column('employees', sa.Column('office_id', sa.Integer(), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact', sa.JSON(), nullable=True))
    op.add_column('employees', sa.Column('access_level', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'employees', 'offices', ['office_id'], ['id'])
    op.drop_column('employees', 'location')

    op.add_column('coffee_machines', sa.Column('office_id', sa.Integer(), nullable=True))
    op.add_column('coffee_machines', sa.Column('location_detail', sa.String(length=100), nullable=True))
    op.add_column('coffee_machines', sa.Column('next_maintenance', sa.DateTime(), nullable=True))
    op.add_column('coffee_machines', sa.Column('milk_level', sa.Float(), nullable=True))
    op.add_column('coffee_machines', sa.Column('total_drinks', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'coffee_machines', 'offices', ['office_id'], ['id'])
    op.drop_column('coffee_machines', 'location')

    op.add_column('safety_visitors', sa.Column('office_id', sa.Integer(), nullable=True))
    op.add_column('safety_visitors', sa.Column('purpose', sa.String(length=200), nullable=True))
    op.add_column('safety_visitors', sa.Column('expected_duration', sa.Integer(), nullable=True))
    op.add_column('safety_visitors', sa.Column('access_areas', sa.JSON(), nullable=True))
    op.add_column('safety_visitors', sa.Column('vehicle_info', sa.JSON(), nullable=True))
    op.create_foreign_key(None, 'safety_visitors', 'offices', ['office_id'], ['id'])

def downgrade():
    # Revert temperature sensor changes
    op.drop_constraint(None, 'temperature_sensors', type_='foreignkey')
    op.add_column('temperature_sensors', sa.Column('location', sa.String(length=100), nullable=True))
    op.drop_column('temperature_sensors', 'location_detail')
    op.drop_column('temperature_sensors', 'office_id')

    # Drop new columns from safety_visitors
    op.drop_constraint(None, 'safety_visitors', type_='foreignkey')
    op.drop_column('safety_visitors', 'vehicle_info')
    op.drop_column('safety_visitors', 'access_areas')
    op.drop_column('safety_visitors', 'expected_duration')
    op.drop_column('safety_visitors', 'purpose')
    op.drop_column('safety_visitors', 'office_id')

    # Drop new columns from coffee_machines
    op.drop_constraint(None, 'coffee_machines', type_='foreignkey')
    op.add_column('coffee_machines', sa.Column('location', sa.String(length=100), nullable=True))
    op.drop_column('coffee_machines', 'total_drinks')
    op.drop_column('coffee_machines', 'milk_level')
    op.drop_column('coffee_machines', 'next_maintenance')
    op.drop_column('coffee_machines', 'location_detail')
    op.drop_column('coffee_machines', 'office_id')

    # Drop new columns from employees
    op.drop_constraint(None, 'employees', type_='foreignkey')
    op.add_column('employees', sa.Column('location', sa.String(length=100), nullable=True))
    op.drop_column('employees', 'access_level')
    op.drop_column('employees', 'emergency_contact')
    op.drop_column('employees', 'office_id')

    # Drop new columns from stock_items
    op.drop_constraint(None, 'stock_items', type_='foreignkey')
    op.drop_column('stock_items', 'unit_cost')
    op.drop_column('stock_items', 'supplier')
    op.drop_column('stock_items', 'location_id')

    # Drop new columns from stock_categories
    op.drop_constraint(None, 'stock_categories', type_='foreignkey')
    op.drop_column('stock_categories', 'parent_id')

    # Drop stock_locations table
    op.drop_table('stock_locations')