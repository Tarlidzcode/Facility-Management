# services/stock_service.py - Stock Management Service Layer
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, func
from sqlalchemy.exc import IntegrityError

from app import db
from models import (
    StockItem, StockCategory, StockLocation, StockTransaction,
    ActivityLog, User
)

class StockService:
    """Service layer for complex stock operations"""
    
    @staticmethod
    def get_low_stock_items(threshold_multiplier: float = 1.0) -> List[StockItem]:
        """Get items that are at or below their reorder point"""
        return StockItem.query.filter(
            and_(
                StockItem.reorder_point.isnot(None),
                StockItem.quantity <= StockItem.reorder_point * threshold_multiplier
            )
        ).all()
    
    @staticmethod
    def get_critical_stock_items() -> List[StockItem]:
        """Get items that are completely out of stock"""
        return StockItem.query.filter(StockItem.quantity <= 0).all()
    
    @staticmethod
    def get_stock_alerts() -> List[Dict]:
        """Get formatted stock alerts for the dashboard"""
        alerts = []
        
        # Critical items (out of stock)
        critical_items = StockService.get_critical_stock_items()
        for item in critical_items:
            alerts.append({
                'id': item.id,
                'item': item.name,
                'type': 'critical',
                'severity': 'high',
                'message': f'Out of stock - {item.name}',
                'current_quantity': item.quantity,
                'unit': item.unit,
                'location': item.location.name if item.location else 'Unknown',
                'recommended_order': item.reorder_point * 2 if item.reorder_point else 10,
                'supplier': item.supplier
            })
        
        # Low stock items
        low_items = StockService.get_low_stock_items()
        for item in low_items:
            if item.quantity > 0:  # Exclude items already in critical list
                alerts.append({
                    'id': item.id,
                    'item': item.name,
                    'type': 'low',
                    'severity': 'medium',
                    'message': f'Low stock - {item.name}',
                    'current_quantity': item.quantity,
                    'unit': item.unit,
                    'location': item.location.name if item.location else 'Unknown',
                    'reorder_point': item.reorder_point,
                    'recommended_order': item.reorder_point * 2,
                    'supplier': item.supplier
                })
        
        return sorted(alerts, key=lambda x: (x['severity'] == 'high', x['current_quantity']))
    
    @staticmethod
    def calculate_stock_value() -> Dict[str, float]:
        """Calculate total stock value and breakdown by category"""
        result = {
            'total_value': 0.0,
            'categories': {}
        }
        
        items = StockItem.query.join(StockCategory, isouter=True).all()
        
        for item in items:
            value = item.get_total_value()
            result['total_value'] += value
            
            category_name = item.category.name if item.category else 'Uncategorized'
            if category_name not in result['categories']:
                result['categories'][category_name] = 0.0
            result['categories'][category_name] += value
        
        # Round values
        result['total_value'] = round(result['total_value'], 2)
        for cat in result['categories']:
            result['categories'][cat] = round(result['categories'][cat], 2)
        
        return result
    
    @staticmethod
    def get_stock_movement_summary(days: int = 30) -> Dict:
        """Get stock movement summary for the last N days"""
        start_date = datetime.now() - timedelta(days=days)
        
        transactions = StockTransaction.query.filter(
            StockTransaction.created_at >= start_date
        ).all()
        
        summary = {
            'total_transactions': len(transactions),
            'items_restocked': 0,
            'items_consumed': 0,
            'total_value_in': 0.0,
            'total_value_out': 0.0,
            'most_active_items': [],
            'recent_activities': []
        }
        
        item_activity = {}
        
        for trans in transactions:
            item = trans.item
            if item.id not in item_activity:
                item_activity[item.id] = {
                    'name': item.name,
                    'transactions': 0,
                    'quantity_in': 0,
                    'quantity_out': 0
                }
            
            item_activity[item.id]['transactions'] += 1
            
            if trans.type == 'in':
                summary['items_restocked'] += 1
                item_activity[item.id]['quantity_in'] += trans.quantity
                if item.unit_cost:
                    summary['total_value_in'] += trans.quantity * item.unit_cost
            elif trans.type == 'out':
                summary['items_consumed'] += 1
                item_activity[item.id]['quantity_out'] += trans.quantity
                if item.unit_cost:
                    summary['total_value_out'] += trans.quantity * item.unit_cost
        
        # Get most active items
        most_active = sorted(
            item_activity.values(),
            key=lambda x: x['transactions'],
            reverse=True
        )[:5]
        
        summary['most_active_items'] = most_active
        summary['total_value_in'] = round(summary['total_value_in'], 2)
        summary['total_value_out'] = round(summary['total_value_out'], 2)
        
        return summary
    
    @staticmethod
    def bulk_restock(item_ids: List[int], quantity: float, reference: str = 'Bulk restock', 
                    user_id: Optional[int] = None) -> Tuple[List[StockItem], List[str]]:
        """Perform bulk restock operation"""
        updated_items = []
        errors = []
        
        try:
            for item_id in item_ids:
                item = StockItem.query.get(item_id)
                if not item:
                    errors.append(f"Item with ID {item_id} not found")
                    continue
                
                try:
                    old_quantity = item.quantity
                    transaction = item.add_stock(quantity, reference, user_id=user_id)
                    updated_items.append(item)
                    
                    # Log individual item restock
                    ActivityLog.create(
                        category='stock',
                        action='bulk_restock',
                        description=f'Bulk restocked {quantity} {item.unit} of "{item.name}"',
                        event_data={
                            'item_id': item.id,
                            'quantity_added': quantity,
                            'old_quantity': old_quantity,
                            'new_quantity': item.quantity
                        }
                    )
                    
                except Exception as e:
                    errors.append(f"Error restocking {item.name}: {str(e)}")
            
            if updated_items and not errors:
                db.session.commit()
            elif updated_items:
                # Partial success - still commit but report errors
                db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            errors.append(f"Bulk operation failed: {str(e)}")
        
        return updated_items, errors
    
    @staticmethod
    def bulk_location_update(item_ids: List[int], location_name: str) -> Tuple[List[StockItem], List[str]]:
        """Update location for multiple items"""
        updated_items = []
        errors = []
        
        try:
            # Get or create location
            location = StockLocation.query.filter_by(name=location_name).first()
            if not location:
                location = StockLocation(name=location_name, area='General')
                db.session.add(location)
                db.session.flush()
            
            for item_id in item_ids:
                item = StockItem.query.get(item_id)
                if not item:
                    errors.append(f"Item with ID {item_id} not found")
                    continue
                
                old_location = item.location.name if item.location else 'None'
                item.location_id = location.id
                updated_items.append(item)
                
                ActivityLog.create(
                    category='stock',
                    action='location_updated',
                    description=f'Location updated for "{item.name}": {old_location} → {location_name}',
                    event_data={
                        'item_id': item.id,
                        'old_location': old_location,
                        'new_location': location_name
                    }
                )
            
            if updated_items:
                db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            errors.append(f"Bulk location update failed: {str(e)}")
        
        return updated_items, errors
    
    @staticmethod
    def generate_reorder_suggestions() -> List[Dict]:
        """Generate intelligent reorder suggestions"""
        suggestions = []
        low_items = StockService.get_low_stock_items()
        
        for item in low_items:
            # Calculate suggested order quantity based on usage patterns
            recent_transactions = StockTransaction.query.filter(
                and_(
                    StockTransaction.item_id == item.id,
                    StockTransaction.type == 'out',
                    StockTransaction.created_at >= datetime.now() - timedelta(days=30)
                )
            ).all()
            
            # Calculate average monthly usage
            total_consumed = sum(t.quantity for t in recent_transactions)
            monthly_usage = total_consumed if recent_transactions else item.reorder_point or 5
            
            # Suggest 2 months worth of stock or 2x reorder point, whichever is higher
            suggested_quantity = max(
                monthly_usage * 2,
                (item.reorder_point or 5) * 2
            )
            
            suggestions.append({
                'item_id': item.id,
                'name': item.name,
                'current_quantity': item.quantity,
                'reorder_point': item.reorder_point,
                'suggested_quantity': round(suggested_quantity),
                'unit': item.unit,
                'supplier': item.supplier,
                'estimated_cost': round(suggested_quantity * (item.unit_cost or 0), 2) if item.unit_cost else None,
                'monthly_usage': round(monthly_usage, 1),
                'days_of_stock': round(item.quantity / (monthly_usage / 30), 1) if monthly_usage > 0 else float('inf'),
                'priority': 'high' if item.quantity <= 0 else 'medium'
            })
        
        return sorted(suggestions, key=lambda x: (x['priority'] == 'high', x['days_of_stock']))
    
    @staticmethod
    def create_order_from_suggestions(suggestions: List[Dict], supplier: str, 
                                    user_id: Optional[int] = None) -> Dict:
        """Create an order from reorder suggestions"""
        if not suggestions:
            return {'success': False, 'error': 'No suggestions provided'}
        
        order_data = {
            'id': int(datetime.now().timestamp()),
            'supplier': supplier,
            'items': [],
            'total_cost': 0.0,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'created_by': user_id
        }
        
        for suggestion in suggestions:
            item_data = {
                'item_id': suggestion['item_id'],
                'name': suggestion['name'],
                'quantity': suggestion['suggested_quantity'],
                'unit': suggestion['unit'],
                'unit_cost': suggestion.get('estimated_cost', 0) / suggestion['suggested_quantity'] if suggestion.get('estimated_cost') else None
            }
            order_data['items'].append(item_data)
            order_data['total_cost'] += suggestion.get('estimated_cost', 0)
        
        order_data['total_cost'] = round(order_data['total_cost'], 2)
        
        # Log order creation
        ActivityLog.create(
            category='stock',
            action='order_created',
            description=f'Order created for {len(suggestions)} items with {supplier}',
            event_data={
                'order_id': order_data['id'],
                'supplier': supplier,
                'item_count': len(suggestions),
                'total_cost': order_data['total_cost']
            }
        )
        
        return {'success': True, 'order': order_data}
    
    @staticmethod
    def get_stock_report(start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> Dict:
        """Generate comprehensive stock report"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Get basic stats
        total_items = StockItem.query.count()
        low_stock_count = len(StockService.get_low_stock_items())
        critical_stock_count = len(StockService.get_critical_stock_items())
        
        # Get value information
        value_info = StockService.calculate_stock_value()
        
        # Get movement summary
        movement_summary = StockService.get_stock_movement_summary(
            days=(end_date - start_date).days
        )
        
        # Get location breakdown
        locations = StockLocation.query.all()
        location_breakdown = []
        for location in locations:
            item_count = len(location.items)
            location_value = sum(item.get_total_value() for item in location.items)
            location_breakdown.append({
                'name': location.name,
                'area': location.area,
                'item_count': item_count,
                'total_value': round(location_value, 2)
            })
        
        # Get category breakdown
        categories = StockCategory.query.all()
        category_breakdown = []
        for category in categories:
            item_count = len(category.items)
            category_value = sum(item.get_total_value() for item in category.items)
            category_breakdown.append({
                'name': category.name,
                'item_count': item_count,
                'total_value': round(category_value, 2)
            })
        
        return {
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_items': total_items,
                'low_stock_items': low_stock_count,
                'critical_stock_items': critical_stock_count,
                'total_value': value_info['total_value'],
                'total_locations': len(locations),
                'total_categories': len(categories)
            },
            'movement': movement_summary,
            'value_breakdown': value_info,
            'location_breakdown': location_breakdown,
            'category_breakdown': category_breakdown,
            'reorder_suggestions': StockService.generate_reorder_suggestions()
        }