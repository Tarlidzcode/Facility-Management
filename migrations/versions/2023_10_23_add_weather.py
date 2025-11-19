"""Add weather and WiFi sensor support

Revision ID: 2023_10_23_add_weather
Revises: 2023_10_23_update_models
Create Date: 2023-10-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2023_10_23_add_weather'
down_revision = '2023_10_23_update_models'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to temperature_sensors
    op.add_column('temperature_sensors', sa.Column('sensor_type', sa.String(length=50), nullable=True))
    op.add_column('temperature_sensors', sa.Column('ip_address', sa.String(length=50), nullable=True))
    op.add_column('temperature_sensors', sa.Column('mac_address', sa.String(length=50), nullable=True))
    op.add_column('temperature_sensors', sa.Column('last_connection', sa.DateTime(), nullable=True))
    op.add_column('temperature_sensors', sa.Column('calibration_offset', sa.Float(), nullable=True))

    # Create weather_stations table
    op.create_table('weather_stations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('office_id', sa.Integer(), nullable=True),
        sa.Column('api_provider', sa.String(length=50), nullable=True),
        sa.Column('location_name', sa.String(length=200), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('last_update', sa.DateTime(), nullable=True),
        sa.Column('api_key', sa.String(length=200), nullable=True),
        sa.Column('update_interval', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['office_id'], ['offices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create weather_data table
    op.create_table('weather_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('station_id', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('pressure', sa.Float(), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=True),
        sa.Column('wind_direction', sa.Float(), nullable=True),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('condition_code', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['station_id'], ['weather_stations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add weather_data_id to temperature_readings
    op.add_column('temperature_readings', 
        sa.Column('weather_data_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(None, 'temperature_readings', 'weather_data', 
        ['weather_data_id'], ['id']
    )

def downgrade():
    # Drop foreign key first
    op.drop_constraint(None, 'temperature_readings', type_='foreignkey')
    op.drop_column('temperature_readings', 'weather_data_id')

    # Drop weather tables
    op.drop_table('weather_data')
    op.drop_table('weather_stations')

    # Remove new columns from temperature_sensors
    op.drop_column('temperature_sensors', 'calibration_offset')
    op.drop_column('temperature_sensors', 'last_connection')
    op.drop_column('temperature_sensors', 'mac_address')
    op.drop_column('temperature_sensors', 'ip_address')
    op.drop_column('temperature_sensors', 'sensor_type')