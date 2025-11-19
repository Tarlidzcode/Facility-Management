# api/stock.py - Stock Management API endpoints
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
import json

from app import db
from models import (
    StockItem, StockCategory, StockLocation, StockTransaction, StockOrder,
    ActivityLog, User, Office
)

stock_bp = Blueprint('stock', __name__)

# In-memory storage for demo orders (will reset when server restarts)
DEMO_ORDERS = []

# In-memory storage for demo stock items (will reset when server restarts)
DEMO_ITEMS = [
    {
        'id': 1,
        'name': 'Coffee Beans',
        'sku': 'CB001',
        'quantity': 3,
        'unit': 'kg',
        'location': 'Kitchen',
        'category': 'Beverages',
        'supplier': 'Makro',
        'reorder_point': 5,
        'unit_cost': 150.0,
        'description': 'Premium Arabica coffee beans',
        'updated_at': datetime.now().isoformat()
    },
    {
        'id': 2,
        'name': 'Milk',
        'sku': 'MK001',
        'quantity': 10,
        'unit': 'liters',
        'location': 'Fridge',
        'category': 'Beverages',
        'supplier': 'Checkers',
        'reorder_point': 15,
        'unit_cost': 18.0,
        'description': 'Fresh full cream milk',
        'updated_at': datetime.now().isoformat()
    },
    {
        'id': 3,
        'name': 'Coffee Filters',
        'sku': 'CF001',
        'quantity': 25,
        'unit': 'pieces',
        'location': 'Store',
        'category': 'Supplies',
        'supplier': 'Takealot',
        'reorder_point': 20,
        'unit_cost': 5.0,
        'description': 'Paper coffee filters',
        'updated_at': datetime.now().isoformat()
    },
    {
        'id': 4,
        'name': 'Printer Paper',
        'sku': 'PP001',
        'quantity': 2,
        'unit': 'packs',
        'location': 'Storage',
        'category': 'Office',
        'supplier': 'Spar',
        'reorder_point': 5,
        'unit_cost': 85.0,
        'description': 'A4 printer paper (500 sheets per pack)',
        'updated_at': datetime.now().isoformat()
    }
]

# ============ STOCK ITEMS ============

@stock_bp.route('/items', methods=['GET'])
def get_stock_items():
    """Get all stock items with optional filtering"""
    try:
        # Get query parameters
        status_filter = request.args.get('status', '')
        location_filter = request.args.get('location', '')
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        
        # Use demo items instead of database
        items_data = []
        for item in DEMO_ITEMS:
            # Determine status based on quantity vs reorder point
            if item['quantity'] <= 0:
                status = 'Critical'
            elif item.get('reorder_point') and item['quantity'] <= item['reorder_point']:
                status = 'Low'
            else:
                status = 'OK'
            
            # Apply filters
            if status_filter and status != status_filter:
                continue
            if location_filter and item.get('location') != location_filter:
                continue
            if category_filter and item.get('category') != category_filter:
                continue
            if search_query and search_query.lower() not in item['name'].lower():
                continue
            
            item_data = {
                'id': item['id'],
                'name': item['name'],
                'sku': item['sku'],
                'quantity': item['quantity'],
                'unit': item['unit'],
                'status': status,
                'location': item.get('location', 'Unknown'),
                'category': item.get('category', 'Uncategorized'),
                'supplier': item.get('supplier', ''),
                'reorder_point': item.get('reorder_point', 0),
                'min_quantity': item.get('min_quantity', 0),
                'unit_cost': item.get('unit_cost', 0),
                'description': item.get('description', ''),
                'last_restock': None,
                'last_updated': item.get('updated_at', datetime.now().isoformat())
            }
            items_data.append(item_data)
        
        return jsonify({
            'success': True,
            'items': items_data,
            'count': len(items_data),
            'mock': True
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching stock items: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        # Return mock data as fallback
        mock_items = [
            {
                'id': 1,
                'name': 'Coffee Beans',
                'sku': 'CB001',
                'quantity': 3,
                'unit': 'kg',
                'status': 'Critical',
                'location': 'Kitchen',
                'category': 'Food & Beverage',
                'supplier': 'Bean Co.',
                'reorder_point': 5,
                'min_quantity': 2,
                'unit_cost': 25.00,
                'last_restock': None,
                'last_updated': datetime.now().isoformat()
            },
            {
                'id': 2,
                'name': 'Milk',
                'sku': 'MK001',
                'quantity': 10,
                'unit': 'liters',
                'status': 'Low',
                'location': 'Fridge',
                'category': 'Food & Beverage',
                'supplier': 'Dairy Fresh',
                'reorder_point': 15,
                'min_quantity': 5,
                'unit_cost': 1.50,
                'last_restock': None,
                'last_updated': datetime.now().isoformat()
            },
            {
                'id': 3,
                'name': 'Coffee Filters',
                'sku': 'CF001',
                'quantity': 25,
                'unit': 'pieces',
                'status': 'OK',
                'location': 'Store',
                'category': 'Office Supplies',
                'supplier': 'Office Plus',
                'reorder_point': 20,
                'min_quantity': 10,
                'unit_cost': 0.15,
                'last_restock': None,
                'last_updated': datetime.now().isoformat()
            },
            {
                'id': 4,
                'name': 'Printer Paper',
                'sku': 'PP001',
                'quantity': 2,
                'unit': 'packs',
                'status': 'Low',
                'location': 'Storage',
                'category': 'Office Supplies',
                'supplier': 'Paper World',
                'reorder_point': 5,
                'min_quantity': 3,
                'unit_cost': 8.50,
                'last_restock': None,
                'last_updated': datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'items': mock_items,
            'count': len(mock_items),
            'mock': True
        })

@stock_bp.route('/items', methods=['POST'])
def create_stock_item():
    """Create a new stock item"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'quantity', 'unit']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Generate SKU if not provided
        sku = data.get('sku')
        if not sku:
            name_part = ''.join(c.upper() for c in data['name'] if c.isalnum())[:3]
            time_part = str(int(datetime.now().timestamp()))[-6:]
            sku = f"{name_part}{time_part}"
        
        # Generate new ID
        new_id = max([item['id'] for item in DEMO_ITEMS], default=0) + 1
        
        # Create new stock item
        new_item = {
            'id': new_id,
            'name': data['name'],
            'sku': sku,
            'quantity': float(data['quantity']),
            'unit': data['unit'],
            'location': data.get('location', ''),
            'category': data.get('category', ''),
            'supplier': data.get('supplier', ''),
            'reorder_point': float(data.get('reorder_point', 5)),
            'min_quantity': float(data.get('min_quantity', 0)),
            'unit_cost': float(data.get('unit_cost', 0)) if data.get('unit_cost') else 0,
            'description': data.get('description', ''),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to demo items list
        DEMO_ITEMS.append(new_item)
        
        current_app.logger.info(f"Added demo item: {new_item['name']} (ID: {new_id})")
        
        return jsonify({
            'success': True,
            'item': {
                'id': new_item['id'],
                'name': new_item['name'],
                'sku': new_item['sku'],
                'quantity': new_item['quantity'],
                'unit': new_item['unit']
            },
            'demo': True
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating stock item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        db.session.rollback()
        current_app.logger.error(f"Error creating stock item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/items/<int:item_id>', methods=['PUT'])
def update_stock_item(item_id):
    """Update an existing stock item"""
    try:
        item = StockItem.query.get_or_404(item_id)
        data = request.get_json()
        
        # Store old values for logging
        old_values = {
            'name': item.name,
            'quantity': item.quantity,
            'reorder_point': item.reorder_point
        }
        
        # Update fields
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'quantity' in data:
            item.quantity = float(data['quantity'])
        if 'unit' in data:
            item.unit = data['unit']
        if 'min_quantity' in data:
            item.min_quantity = float(data['min_quantity'])
        if 'reorder_point' in data or 'threshold' in data:
            item.reorder_point = float(data.get('reorder_point', data.get('threshold')))
        if 'supplier' in data:
            item.supplier = data['supplier']
        if 'unit_cost' in data:
            item.unit_cost = float(data['unit_cost']) if data['unit_cost'] else None
        
        # Update location if provided
        if 'location' in data and data['location']:
            location = StockLocation.query.filter_by(name=data['location']).first()
            if not location:
                location = StockLocation(name=data['location'], area='General')
                db.session.add(location)
                db.session.flush()
            item.location_id = location.id
        
        # Update category if provided
        if 'category' in data and data['category']:
            category = StockCategory.query.filter_by(name=data['category']).first()
            if not category:
                category = StockCategory(name=data['category'])
                db.session.add(category)
                db.session.flush()
            item.category_id = category.id
        
        db.session.commit()
        
        # Log significant changes
        changes = []
        if old_values['quantity'] != item.quantity:
            changes.append(f"quantity: {old_values['quantity']} → {item.quantity}")
        if old_values['reorder_point'] != item.reorder_point:
            changes.append(f"reorder point: {old_values['reorder_point']} → {item.reorder_point}")
        
        if changes:
            ActivityLog.create(
                category='stock',
                action='item_updated',
                description=f'Stock item "{item.name}" updated: {", ".join(changes)}',
                event_data={'item_id': item.id, 'changes': changes}
            )
        
        return jsonify({'success': True, 'message': 'Item updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating stock item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_stock_item(item_id):
    """Delete a stock item"""
    try:
        item = StockItem.query.get_or_404(item_id)
        item_name = item.name
        
        # Check if item has recent transactions
        recent_transactions = StockTransaction.query.filter(
            and_(
                StockTransaction.item_id == item_id,
                StockTransaction.created_at >= datetime.now() - timedelta(days=30)
            )
        ).count()
        
        if recent_transactions > 0:
            return jsonify({
                'success': False, 
                'error': 'Cannot delete item with recent transactions. Consider marking as inactive instead.'
            }), 400
        
        db.session.delete(item)
        db.session.commit()
        
        # Log the deletion
        ActivityLog.create(
            category='stock',
            action='item_deleted',
            description=f'Stock item "{item_name}" deleted',
            event_data={'item_id': item_id}
        )
        
        return jsonify({'success': True, 'message': 'Item deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting stock item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ STOCK OPERATIONS ============

@stock_bp.route('/items/<int:item_id>/restock', methods=['POST'])
def restock_item(item_id):
    """Add stock to an item (restock operation)"""
    try:
        item = StockItem.query.get_or_404(item_id)
        data = request.get_json()
        
        quantity = float(data.get('quantity', 0))
        if quantity <= 0:
            return jsonify({'success': False, 'error': 'Quantity must be positive'}), 400
        
        old_quantity = item.quantity
        item.quantity += quantity
        item.last_restock = datetime.now()
        
        # Create transaction record
        transaction = StockTransaction(
            item_id=item.id,
            type='in',
            quantity=quantity,
            reference=data.get('reference', 'Manual restock'),
            notes=data.get('notes', f'Restocked via API')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Log the restock
        ActivityLog.create(
            category='stock',
            action='item_restocked',
            description=f'Restocked {quantity} {item.unit} of "{item.name}"',
            event_data={
                'item_id': item.id,
                'quantity_added': quantity,
                'old_quantity': old_quantity,
                'new_quantity': item.quantity
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Added {quantity} {item.unit} to {item.name}',
            'new_quantity': item.quantity
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error restocking item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/items/<int:item_id>/consume', methods=['POST'])
def consume_item(item_id):
    """Remove stock from an item (consumption/usage)"""
    try:
        item = StockItem.query.get_or_404(item_id)
        data = request.get_json()
        
        quantity = float(data.get('quantity', 0))
        if quantity <= 0:
            return jsonify({'success': False, 'error': 'Quantity must be positive'}), 400
        
        if item.quantity < quantity:
            return jsonify({'success': False, 'error': 'Insufficient stock'}), 400
        
        old_quantity = item.quantity
        item.quantity -= quantity
        
        # Create transaction record
        transaction = StockTransaction(
            item_id=item.id,
            type='out',
            quantity=quantity,
            reference=data.get('reference', 'Consumption'),
            notes=data.get('notes', f'Consumed via API')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Log the consumption
        ActivityLog.create(
            category='stock',
            action='item_consumed',
            description=f'Consumed {quantity} {item.unit} of "{item.name}"',
            event_data={
                'item_id': item.id,
                'quantity_consumed': quantity,
                'old_quantity': old_quantity,
                'new_quantity': item.quantity
            }
        )
        
        # Check if item needs reordering
        if item.reorder_point and item.quantity <= item.reorder_point:
            ActivityLog.create(
                category='stock',
                action='reorder_alert',
                description=f'"{item.name}" has reached reorder point',
                event_data={
                    'item_id': item.id,
                    'current_quantity': item.quantity,
                    'reorder_point': item.reorder_point
                }
            )
        
        return jsonify({
            'success': True,
            'message': f'Consumed {quantity} {item.unit} of {item.name}',
            'new_quantity': item.quantity,
            'needs_reorder': item.reorder_point and item.quantity <= item.reorder_point
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error consuming item: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ BULK OPERATIONS ============

@stock_bp.route('/items/bulk-update', methods=['POST'])
def bulk_update_items():
    """Perform bulk operations on multiple items"""
    try:
        data = request.get_json()
        item_ids = data.get('item_ids', [])
        operation = data.get('operation')
        
        if not item_ids or not operation:
            return jsonify({'success': False, 'error': 'Missing item_ids or operation'}), 400
        
        items = StockItem.query.filter(StockItem.id.in_(item_ids)).all()
        if len(items) != len(item_ids):
            return jsonify({'success': False, 'error': 'Some items not found'}), 404
        
        updated_items = []
        
        if operation == 'update_location':
            new_location_name = data.get('location')
            if not new_location_name:
                return jsonify({'success': False, 'error': 'Location required for location update'}), 400
            
            location = StockLocation.query.filter_by(name=new_location_name).first()
            if not location:
                location = StockLocation(name=new_location_name, area='General')
                db.session.add(location)
                db.session.flush()
            
            for item in items:
                item.location_id = location.id
                updated_items.append(item.name)
        
        elif operation == 'update_category':
            new_category_name = data.get('category')
            if not new_category_name:
                return jsonify({'success': False, 'error': 'Category required for category update'}), 400
            
            category = StockCategory.query.filter_by(name=new_category_name).first()
            if not category:
                category = StockCategory(name=new_category_name)
                db.session.add(category)
                db.session.flush()
            
            for item in items:
                item.category_id = category.id
                updated_items.append(item.name)
        
        elif operation == 'restock':
            quantity = float(data.get('quantity', 0))
            if quantity <= 0:
                return jsonify({'success': False, 'error': 'Positive quantity required for restock'}), 400
            
            for item in items:
                item.quantity += quantity
                item.last_restock = datetime.now()
                
                # Create transaction
                transaction = StockTransaction(
                    item_id=item.id,
                    type='in',
                    quantity=quantity,
                    reference='Bulk restock',
                    notes=f'Bulk restock operation'
                )
                db.session.add(transaction)
                updated_items.append(item.name)
        
        elif operation == 'delete':
            for item in items:
                updated_items.append(item.name)
                db.session.delete(item)
        
        else:
            return jsonify({'success': False, 'error': 'Invalid operation'}), 400
        
        db.session.commit()
        
        # Log the bulk operation
        ActivityLog.create(
            category='stock',
            action='bulk_operation',
            description=f'Bulk {operation} performed on {len(updated_items)} items',
            event_data={
                'operation': operation,
                'item_count': len(updated_items),
                'items': updated_items
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Bulk {operation} completed',
            'updated_items': updated_items
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk operation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ ORDERS ============

@stock_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new order - Demo version (stores in memory)"""
    try:
        data = request.get_json()
        
        # Log what we received for debugging
        current_app.logger.info(f"Received order data: {data}")
        
        supplier = data.get('supplier')
        priority = data.get('priority', 'normal')
        
        # Support both formats: single item or items array
        items = data.get('items', [])
        
        # If single item format (from create order modal)
        if not items and data.get('item_name'):
            items = [{
                'name': data.get('item_name'),
                'quantity': data.get('quantity'),
                'unit': data.get('unit'),
                'category': data.get('category', 'General'),
                'estimated_cost': data.get('estimated_cost', 0),
                'notes': data.get('notes', '')
            }]
        
        # Better validation and error messages
        if not supplier:
            current_app.logger.error(f"Missing supplier. Received data: {data}")
            return jsonify({'success': False, 'error': 'Supplier is required'}), 400
        
        if not items:
            current_app.logger.error(f"Missing items. Received data: {data}")
            return jsonify({'success': False, 'error': 'At least one item is required'}), 400
        
        # Validate item data
        for idx, item in enumerate(items):
            if not item.get('name'):
                return jsonify({'success': False, 'error': f'Item {idx+1}: name is required'}), 400
            if not item.get('quantity'):
                return jsonify({'success': False, 'error': f'Item {idx+1}: quantity is required'}), 400
            if not item.get('unit'):
                return jsonify({'success': False, 'error': f'Item {idx+1}: unit is required'}), 400
        
        # Create order ID
        order_id = int(datetime.now().timestamp())
        
        # Calculate total estimated cost
        total_cost = sum(float(item.get('estimated_cost', 0)) for item in items)
        
        # Format order description
        items_desc = ', '.join([f"{item.get('quantity', 0)} {item.get('unit', '')} {item.get('name', '')}" for item in items])
        
        # Create demo order object
        demo_order = {
            'id': order_id,
            'order_id': order_id,
            'supplier': supplier,
            'priority': priority,
            'status': 'pending',
            'items': items,
            'item_name': items[0]['name'] if items else 'Unknown',
            'quantity': items[0]['quantity'] if items else 0,
            'unit': items[0]['unit'] if items else '',
            'category': items[0].get('category', 'General') if items else 'General',
            'total_cost': total_cost,
            'items_description': items_desc,
            'notes': items[0].get('notes', '') if items else '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Add to demo orders list
        DEMO_ORDERS.insert(0, demo_order)  # Insert at beginning so newest appears first
        
        current_app.logger.info(f"Demo order created successfully: {order_id}")
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': f'Order placed with {supplier} for {len(items)} item(s)',
            'items_description': items_desc,
            'total_cost': total_cost,
            'demo': True
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating order: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an existing order - Demo version (updates in memory)"""
    try:
        data = request.get_json()
        
        # Log what we received for debugging
        current_app.logger.info(f"Updating order {order_id} with data: {data}")
        
        # Find the order in DEMO_ORDERS
        order_index = None
        for idx, order in enumerate(DEMO_ORDERS):
            if order.get('id') == order_id or order.get('order_id') == order_id:
                order_index = idx
                break
        
        if order_index is None:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Get existing order
        existing_order = DEMO_ORDERS[order_index]
        
        # Update order fields
        supplier = data.get('supplier', existing_order.get('supplier'))
        priority = data.get('priority', existing_order.get('priority', 'normal'))
        
        # Support both formats: single item or items array
        items = data.get('items', [])
        
        # If single item format (from create order modal)
        if not items and data.get('item_name'):
            items = [{
                'name': data.get('item_name'),
                'quantity': data.get('quantity'),
                'unit': data.get('unit'),
                'category': data.get('category', 'General'),
                'estimated_cost': data.get('estimated_cost', 0),
                'notes': data.get('notes', '')
            }]
        
        # Use existing items if not provided
        if not items:
            items = existing_order.get('items', [])
        
        # Validate required fields
        if not supplier:
            return jsonify({'success': False, 'error': 'Supplier is required'}), 400
        
        if not items:
            return jsonify({'success': False, 'error': 'At least one item is required'}), 400
        
        # Validate item data
        for idx, item in enumerate(items):
            if not item.get('name'):
                return jsonify({'success': False, 'error': f'Item {idx+1}: name is required'}), 400
            if not item.get('quantity'):
                return jsonify({'success': False, 'error': f'Item {idx+1}: quantity is required'}), 400
            if not item.get('unit'):
                return jsonify({'success': False, 'error': f'Item {idx+1}: unit is required'}), 400
        
        # Calculate total estimated cost
        total_cost = sum(float(item.get('estimated_cost', 0)) for item in items)
        
        # Format order description
        items_desc = ', '.join([f"{item.get('quantity', 0)} {item.get('unit', '')} {item.get('name', '')}" for item in items])
        
        # Update the order
        updated_order = {
            'id': order_id,
            'order_id': order_id,
            'supplier': supplier,
            'priority': priority,
            'status': data.get('status', existing_order.get('status', 'pending')),
            'items': items,
            'item_name': items[0]['name'] if items else 'Unknown',
            'quantity': items[0]['quantity'] if items else 0,
            'unit': items[0]['unit'] if items else '',
            'category': items[0].get('category', 'General') if items else 'General',
            'total_cost': total_cost,
            'items_description': items_desc,
            'notes': items[0].get('notes', '') if items else '',
            'created_at': existing_order.get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat()
        }
        
        # Replace the order in the list
        DEMO_ORDERS[order_index] = updated_order
        
        current_app.logger.info(f"Order {order_id} updated successfully")
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': f'Order updated successfully',
            'items_description': items_desc,
            'total_cost': total_cost,
            'demo': True
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating order: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel (delete) an order - Demo version (removes from memory)"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Cancelled by user')
        
        # Log the cancellation attempt
        current_app.logger.info(f"Cancelling order {order_id}. Reason: {reason}")
        
        # Find the order in DEMO_ORDERS
        order_index = None
        for idx, order in enumerate(DEMO_ORDERS):
            if order.get('id') == order_id or order.get('order_id') == order_id:
                order_index = idx
                break
        
        if order_index is None:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Remove the order from the list
        cancelled_order = DEMO_ORDERS.pop(order_index)
        
        current_app.logger.info(f"Order {order_id} cancelled successfully. Item: {cancelled_order.get('item_name')}")
        
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully',
            'order_id': order_id,
            'reason': reason
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error cancelling order: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ ANALYTICS & SUMMARY ============

@stock_bp.route('/summary', methods=['GET'])
def get_stock_summary():
    """Get stock summary statistics"""
    try:
        # Get all items with their calculated statuses
        items = StockItem.query.all()
        
        total_items = len(items)
        low_stock_items = 0
        critical_stock_items = 0
        total_value = 0
        
        for item in items:
            # Calculate status
            if item.quantity <= 0:
                critical_stock_items += 1
            elif item.reorder_point and item.quantity <= item.reorder_point:
                low_stock_items += 1
            
            # Calculate value
            if item.unit_cost and item.quantity:
                total_value += item.unit_cost * item.quantity
        
        # Get total locations
        total_locations = StockLocation.query.count()
        
        # Get recent activity count
        recent_activity = ActivityLog.query.filter(
            and_(
                ActivityLog.category == 'stock',
                ActivityLog.created_at >= datetime.now() - timedelta(days=7)
            )
        ).count()
        
        return jsonify({
            'success': True,
            'summary': {
                'total_items': total_items,
                'low_stock_items': low_stock_items,
                'critical_stock_items': critical_stock_items,
                'total_locations': total_locations,
                'total_value': round(total_value, 2),
                'recent_activity': recent_activity,
                'pending_orders': 0  # Mock for now
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting stock summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/alerts', methods=['GET'])
def get_stock_alerts():
    """Get stock alerts (low/critical items)"""
    try:
        items = StockItem.query.all()
        alerts = []
        
        for item in items:
            if item.quantity <= 0:
                alerts.append({
                    'id': item.id,
                    'item': item.name,
                    'type': 'critical',
                    'message': f'Out of stock - {item.name}',
                    'current_quantity': item.quantity,
                    'unit': item.unit,
                    'recommended_order': item.reorder_point * 2 if item.reorder_point else 10
                })
            elif item.reorder_point and item.quantity <= item.reorder_point:
                alerts.append({
                    'id': item.id,
                    'item': item.name,
                    'type': 'low',
                    'message': f'Low stock - {item.name}',
                    'current_quantity': item.quantity,
                    'unit': item.unit,
                    'reorder_point': item.reorder_point,
                    'recommended_order': item.reorder_point * 2
                })
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting stock alerts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ LOCATIONS & CATEGORIES ============

@stock_bp.route('/locations', methods=['GET'])
def get_locations():
    """Get all stock locations"""
    try:
        locations = StockLocation.query.all()
        locations_data = [
            {
                'id': loc.id,
                'name': loc.name,
                'area': loc.area,
                'description': loc.description,
                'item_count': len(loc.items)
            }
            for loc in locations
        ]
        
        return jsonify({
            'success': True,
            'locations': locations_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching locations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@stock_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all stock categories"""
    try:
        categories = StockCategory.query.all()
        categories_data = [
            {
                'id': cat.id,
                'name': cat.name,
                'description': cat.description,
                'item_count': len(cat.items)
            }
            for cat in categories
        ]
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching categories: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ TRANSACTIONS ============

@stock_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Get stock transaction history"""
    try:
        limit = int(request.args.get('limit', 50))
        item_id = request.args.get('item_id')
        
        query = StockTransaction.query.join(StockItem)
        
        if item_id:
            query = query.filter(StockTransaction.item_id == item_id)
        
        transactions = query.order_by(StockTransaction.created_at.desc()).limit(limit).all()
        
        transactions_data = [
            {
                'id': t.id,
                'item_name': t.item.name,
                'type': t.type,
                'quantity': t.quantity,
                'reference': t.reference,
                'notes': t.notes,
                'created_at': t.created_at.isoformat(),
                'user': t.user.name if t.user else 'System'
            }
            for t in transactions
        ]
        
        return jsonify({
            'success': True,
            'transactions': transactions_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching transactions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ EXPORT ============

@stock_bp.route('/export', methods=['GET'])
def export_orders_report():
    """Export orders report with filtering by time period"""
    try:
        import csv
        from io import StringIO
        from flask import Response
        
        # Get parameters
        period = request.args.get('period', 'all')
        format_type = request.args.get('format', 'csv')
        
        # Calculate date cutoff based on period
        now = datetime.now()
        if period == 'week':
            cutoff = now - timedelta(days=7)
            period_label = 'This Week'
        elif period == 'month':
            cutoff = now - timedelta(days=30)
            period_label = 'This Month'
        else:
            cutoff = None
            period_label = 'All Time'
        
        # Filter orders by date
        if cutoff:
            filtered_orders = [
                order for order in DEMO_ORDERS 
                if datetime.fromisoformat(order['created_at']) >= cutoff
            ]
        else:
            filtered_orders = DEMO_ORDERS
        
        # Sort by date (newest first)
        filtered_orders = sorted(filtered_orders, key=lambda x: x['created_at'], reverse=True)
        
        # Generate CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Title and period
        writer.writerow(['Orders Report - ' + period_label])
        writer.writerow(['Generated:', now.strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Header row
        writer.writerow([
            'Order ID', 'Date Placed', 'Item Name', 'Quantity', 'Unit', 
            'Price (R)', 'Supplier', 'Status', 'Priority', 'Notes'
        ])
        
        # Data rows
        total_cost = 0
        for order in filtered_orders:
            date_placed = datetime.fromisoformat(order['created_at']).strftime('%Y-%m-%d %H:%M')
            writer.writerow([
                order['order_id'],
                date_placed,
                order['item_name'],
                order['quantity'],
                order['unit'],
                f"{order['total_cost']:.2f}",
                order['supplier'],
                order['status'],
                order['priority'],
                order.get('notes', 'N/A')
            ])
            total_cost += order['total_cost']
        
        # Summary section
        writer.writerow([])
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Orders:', len(filtered_orders)])
        writer.writerow(['Total Value:', f"R{total_cost:.2f}"])
        writer.writerow(['Period:', period_label])
        
        # Prepare response
        output.seek(0)
        filename = f"orders_report_{period}_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
    except Exception as e:
        current_app.logger.error(f"Error exporting orders: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@stock_bp.route('/export/stock', methods=['GET'])
def export_stock_data():
    """Export stock data as CSV"""
    try:
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Name', 'SKU', 'Quantity', 'Unit', 'Status', 'Location', 
            'Category', 'Supplier', 'Reorder Point', 'Unit Cost', 'Last Updated'
        ])
        
        # Get all items
        items = StockItem.query.join(StockLocation, isouter=True).join(StockCategory, isouter=True).all()
        
        for item in items:
            # Calculate status
            if item.quantity <= 0:
                status = 'Critical'
            elif item.reorder_point and item.quantity <= item.reorder_point:
                status = 'Low'
            else:
                status = 'OK'
            
            writer.writerow([
                item.name,
                item.sku,
                item.quantity,
                item.unit,
                status,
                item.location.name if item.location else 'Unknown',
                item.category.name if item.category else 'Uncategorized',
                item.supplier,
                item.reorder_point,
                item.unit_cost,
                item.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        output.seek(0)
        
        return jsonify({
            'success': True,
            'data': output.getvalue(),
            'filename': f'stock_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error exporting stock data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============ SUPPLIERS ============


@stock_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get list of available suppliers (SA Retailers)"""
    try:
        # Standard SA retailers
        suppliers = [
            'Pick N Pay',
            'Checkers',
            'Shoprite',
            'Woolworths',
            'Spar',
            'Makro',
            'Game',
            'Massmart',
            'Food Lovers Market',
            'OK Grocer'
        ]
        
        return jsonify({
            'success': True,
            'data': suppliers
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching suppliers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ GET ORDERS (DEMO) ============

@stock_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all stock orders - returns demo orders from memory"""
    try:
        status_filter = request.args.get('status', '')
        
        # Filter demo orders
        filtered_orders = DEMO_ORDERS
        if status_filter:
            filtered_orders = [o for o in DEMO_ORDERS if o.get('status') == status_filter]
        
        return jsonify({
            'success': True,
            'data': filtered_orders,
            'total': len(filtered_orders),
            'mock': True
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching orders: {e}")
        return jsonify({
            'success': True,
            'data': [],
            'total': 0,
            'mock': True
        })
