# seed_stock.py - Stock Management Database Seeder
"""
Seed the database with initial stock data for testing and demonstration.
Run this script to populate the database with sample stock items, categories, and locations.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from models import (
    StockItem, StockCategory, StockLocation, StockTransaction,
    Office, User, ActivityLog
)

def seed_stock_data():
    """Seed the database with initial stock data"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Seeding stock management data...")
        
        try:
            # Create categories
            categories_data = [
                {'name': 'Food & Beverage', 'description': 'Coffee, tea, snacks, and other food items'},
                {'name': 'Office Supplies', 'description': 'Paper, pens, and general office supplies'},
                {'name': 'Cleaning', 'description': 'Cleaning supplies and maintenance items'},
                {'name': 'Equipment', 'description': 'Office equipment and accessories'},
                {'name': 'Technology', 'description': 'IT supplies and accessories'}
            ]
            
            categories = {}
            for cat_data in categories_data:
                category = StockCategory.query.filter_by(name=cat_data['name']).first()
                if not category:
                    category = StockCategory(**cat_data)
                    db.session.add(category)
                    db.session.flush()
                categories[cat_data['name']] = category
                print(f"   ✓ Category: {cat_data['name']}")
            
            # Create locations
            locations_data = [
                {'name': 'Kitchen', 'area': 'Kitchen Area', 'description': 'Main kitchen and food preparation area'},
                {'name': 'Fridge', 'area': 'Kitchen Area', 'description': 'Refrigerated storage'},
                {'name': 'Store', 'area': 'Storage', 'description': 'Main storage room'},
                {'name': 'Storage', 'area': 'Storage', 'description': 'General storage area'},
                {'name': 'Office', 'area': 'Work Area', 'description': 'Office desks and workstations'},
                {'name': 'IT Room', 'area': 'Technical', 'description': 'IT equipment storage'}
            ]
            
            locations = {}
            for loc_data in locations_data:
                location = StockLocation.query.filter_by(name=loc_data['name']).first()
                if not location:
                    # Set office_id to 1 (assuming default office exists)
                    location = StockLocation(office_id=1, **loc_data)
                    db.session.add(location)
                    db.session.flush()
                locations[loc_data['name']] = location
                print(f"   ✓ Location: {loc_data['name']}")
            
            # Create stock items
            items_data = [
                {
                    'name': 'Coffee Beans',
                    'sku': 'CB001',
                    'description': 'Premium arabica coffee beans',
                    'quantity': 3,
                    'unit': 'kg',
                    'min_quantity': 1,
                    'reorder_point': 5,
                    'supplier': 'Bean Co.',
                    'unit_cost': 25.00,
                    'category': 'Food & Beverage',
                    'location': 'Kitchen'
                },
                {
                    'name': 'Milk',
                    'sku': 'MK001',
                    'description': 'Fresh whole milk',
                    'quantity': 10,
                    'unit': 'liters',
                    'min_quantity': 2,
                    'reorder_point': 5,
                    'supplier': 'Dairy Fresh',
                    'unit_cost': 1.50,
                    'category': 'Food & Beverage',
                    'location': 'Fridge'
                },
                {
                    'name': 'Coffee Filters',
                    'sku': 'CF001',
                    'description': 'Paper coffee filters size 4',
                    'quantity': 25,
                    'unit': 'pieces',
                    'min_quantity': 10,
                    'reorder_point': 20,
                    'supplier': 'Office Plus',
                    'unit_cost': 0.15,
                    'category': 'Office Supplies',
                    'location': 'Store'
                },
                {
                    'name': 'Printer Paper',
                    'sku': 'PP001',
                    'description': 'A4 white paper 80gsm',
                    'quantity': 2,
                    'unit': 'packs',
                    'min_quantity': 1,
                    'reorder_point': 5,
                    'supplier': 'Paper World',
                    'unit_cost': 8.50,
                    'category': 'Office Supplies',
                    'location': 'Storage'
                },
                {
                    'name': 'Tea Bags',
                    'sku': 'TB001',
                    'description': 'English Breakfast tea bags',
                    'quantity': 45,
                    'unit': 'pieces',
                    'min_quantity': 20,
                    'reorder_point': 30,
                    'supplier': 'Tea Company',
                    'unit_cost': 0.25,
                    'category': 'Food & Beverage',
                    'location': 'Kitchen'
                },
                {
                    'name': 'Sugar',
                    'sku': 'SG001',
                    'description': 'White granulated sugar',
                    'quantity': 1,
                    'unit': 'kg',
                    'min_quantity': 0.5,
                    'reorder_point': 2,
                    'supplier': 'Sweet Co.',
                    'unit_cost': 2.00,
                    'category': 'Food & Beverage',
                    'location': 'Kitchen'
                },
                {
                    'name': 'Pens',
                    'sku': 'PN001',
                    'description': 'Blue ballpoint pens',
                    'quantity': 15,
                    'unit': 'pieces',
                    'min_quantity': 5,
                    'reorder_point': 10,
                    'supplier': 'Stationery Plus',
                    'unit_cost': 1.20,
                    'category': 'Office Supplies',
                    'location': 'Office'
                },
                {
                    'name': 'Notebooks',
                    'sku': 'NB001',
                    'description': 'A5 lined notebooks',
                    'quantity': 8,
                    'unit': 'pieces',
                    'min_quantity': 3,
                    'reorder_point': 6,
                    'supplier': 'Stationery Plus',
                    'unit_cost': 3.50,
                    'category': 'Office Supplies',
                    'location': 'Office'
                },
                {
                    'name': 'Cleaning Spray',
                    'sku': 'CS001',
                    'description': 'Multi-surface cleaning spray',
                    'quantity': 0,
                    'unit': 'bottles',
                    'min_quantity': 1,
                    'reorder_point': 3,
                    'supplier': 'Clean Co.',
                    'unit_cost': 4.50,
                    'category': 'Cleaning',
                    'location': 'Storage'
                },
                {
                    'name': 'USB Cables',
                    'sku': 'UC001',
                    'description': 'USB-A to USB-C cables 1m',
                    'quantity': 12,
                    'unit': 'pieces',
                    'min_quantity': 3,
                    'reorder_point': 8,
                    'supplier': 'Tech Supply',
                    'unit_cost': 5.00,
                    'category': 'Technology',
                    'location': 'IT Room'
                }
            ]
            
            items = []
            for item_data in items_data:
                # Check if item already exists
                existing_item = StockItem.query.filter_by(sku=item_data['sku']).first()
                if existing_item:
                    print(f"   ⚠ Item already exists: {item_data['name']} (SKU: {item_data['sku']})")
                    continue
                
                # Get category and location
                category = categories.get(item_data.pop('category'))
                location = locations.get(item_data.pop('location'))
                
                # Create item
                item = StockItem(
                    category_id=category.id if category else None,
                    location_id=location.id if location else None,
                    last_restock=datetime.now() - timedelta(days=random.randint(1, 30)),
                    **item_data
                )
                
                db.session.add(item)
                db.session.flush()
                items.append(item)
                print(f"   ✓ Item: {item.name} (Qty: {item.quantity} {item.unit})")
            
            # Create some sample transactions
            print("   🔄 Creating sample transactions...")
            transaction_count = 0
            
            for item in items[:5]:  # Create transactions for first 5 items
                # Create some "in" transactions (restocking)
                for _ in range(random.randint(1, 3)):
                    transaction = StockTransaction(
                        item_id=item.id,
                        type='in',
                        quantity=random.randint(5, 20),
                        reference=f'Restock-{random.randint(1000, 9999)}',
                        notes='Initial stock replenishment',
                        created_at=datetime.now() - timedelta(days=random.randint(1, 60))
                    )
                    db.session.add(transaction)
                    transaction_count += 1
                
                # Create some "out" transactions (consumption)
                for _ in range(random.randint(1, 2)):
                    transaction = StockTransaction(
                        item_id=item.id,
                        type='out',
                        quantity=random.randint(1, 8),
                        reference='Daily usage',
                        notes='Regular consumption',
                        created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                    )
                    db.session.add(transaction)
                    transaction_count += 1
            
            print(f"   ✓ Created {transaction_count} sample transactions")
            
            # Create some activity logs
            print("   📝 Creating activity logs...")
            activity_count = 0
            
            for item in items[:3]:
                ActivityLog.create(
                    category='stock',
                    action='item_created',
                    description=f'Stock item "{item.name}" created during seeding',
                    event_data={'item_id': item.id, 'quantity': item.quantity}
                )
                activity_count += 1
                
                if item.quantity <= item.reorder_point:
                    ActivityLog.create(
                        category='stock',
                        action='reorder_needed',
                        description=f'Stock item "{item.name}" needs reordering',
                        event_data={
                            'item_id': item.id,
                            'current_quantity': item.quantity,
                            'reorder_point': item.reorder_point
                        }
                    )
                    activity_count += 1
            
            print(f"   ✓ Created {activity_count} activity logs")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ Stock data seeding completed successfully!")
            print(f"   📦 Created {len(categories_data)} categories")
            print(f"   📍 Created {len(locations_data)} locations")
            print(f"   🏷️  Created {len(items)} stock items")
            print(f"   🔄 Created {transaction_count} transactions")
            print(f"   📝 Created {activity_count} activity logs")
            
            # Print summary of current stock status
            print(f"\n📊 Stock Summary:")
            total_items = len(items)
            low_stock = sum(1 for item in items if item.quantity <= item.reorder_point)
            critical_stock = sum(1 for item in items if item.quantity <= 0)
            total_value = sum(item.quantity * (item.unit_cost or 0) for item in items)
            
            print(f"   Total Items: {total_items}")
            print(f"   Low Stock Items: {low_stock}")
            print(f"   Critical Stock Items: {critical_stock}")
            print(f"   Total Inventory Value: R{total_value:.2f}")
            
        except Exception as e:
            print(f"❌ Error seeding stock data: {e}")
            db.session.rollback()
            raise

def clear_stock_data():
    """Clear all stock data from the database"""
    app = create_app()
    
    with app.app_context():
        print("🧹 Clearing existing stock data...")
        
        try:
            # Delete in order to respect foreign key constraints
            StockTransaction.query.delete()
            StockItem.query.delete()
            StockLocation.query.delete()
            StockCategory.query.delete()
            
            # Clear stock-related activity logs
            ActivityLog.query.filter_by(category='stock').delete()
            
            db.session.commit()
            print("✅ Stock data cleared successfully!")
            
        except Exception as e:
            print(f"❌ Error clearing stock data: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Management Database Seeder')
    parser.add_argument('--clear', action='store_true', help='Clear existing stock data before seeding')
    parser.add_argument('--clear-only', action='store_true', help='Only clear stock data, do not seed')
    
    args = parser.parse_args()
    
    if args.clear_only:
        clear_stock_data()
    elif args.clear:
        clear_stock_data()
        seed_stock_data()
    else:
        seed_stock_data()