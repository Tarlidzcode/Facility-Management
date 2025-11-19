import sqlite3
from datetime import datetime

conn = sqlite3.connect(r'C:\Users\EATHON~1.GRO\AppData\Local\Temp\office_eathon.db')
cursor = conn.cursor()

# Add some test stock items with low stock
test_items = [
    ('Coffee Beans', 'kg', 2, 10, 'Coffee Suppliers Ltd', 15.50),
    ('Milk', 'L', 3, 10, 'Dairy Fresh', 5.00),
    ('Sugar', 'kg', 1, 5, 'Sweet Supplies', 3.50),
    ('Tea Bags', 'boxes', 4, 8, 'Tea World', 12.00),
    ('Paper Cups', 'packs', 15, 20, 'Office Supplies Co', 8.50),
    ('Coffee Filters', 'boxes', 2, 5, 'Coffee Suppliers Ltd', 6.00),
    ('Cleaning Supplies', 'units', 10, 15, 'Clean Pro', 25.00),
    ('Napkins', 'packs', 20, 30, 'Office Supplies Co', 4.50),
]

now = datetime.now().isoformat()

print("Adding test stock items...")
for name, unit, quantity, reorder_point, supplier, cost in test_items:
    cursor.execute('''
        INSERT INTO stock_items 
        (name, unit, quantity, reorder_point, supplier, unit_cost, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, unit, quantity, reorder_point, supplier, cost, now, now))
    print(f"  ✅ Added: {name} - {quantity} {unit} (reorder at {reorder_point})")

conn.commit()

# Check low stock items
cursor.execute("SELECT name, quantity, reorder_point, unit FROM stock_items WHERE quantity <= reorder_point")
low_stock = cursor.fetchall()

print(f"\n⚠️  {len(low_stock)} items are low in stock:")
for item in low_stock:
    print(f"  • {item[0]}: {item[1]} {item[3]} (reorder at {item[2]})")

conn.close()
print("\n✅ Database seeded successfully!")
