import sqlite3

conn = sqlite3.connect(r'C:\Users\EATHON~1.GRO\AppData\Local\Temp\office_eathon.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("📋 Tables in database:", tables)

# Check stock items
if 'stock_items' in tables:
    cursor.execute("SELECT COUNT(*) FROM stock_items")
    count = cursor.fetchone()[0]
    print(f"\n📦 Total stock items: {count}")
    
    cursor.execute("SELECT name, current_quantity, reorder_point FROM stock_items WHERE current_quantity <= reorder_point LIMIT 5")
    low_stock = cursor.fetchall()
    if low_stock:
        print("\n⚠️  Low stock items:")
        for item in low_stock:
            print(f"  • {item[0]}: {item[1]} (reorder at {item[2]})")
    else:
        print("\n✅ No low stock items - need to add some test data!")
        cursor.execute("SELECT name, current_quantity, reorder_point FROM stock_items LIMIT 5")
        all_stock = cursor.fetchall()
        if all_stock:
            print("\n📦 Sample stock items:")
            for item in all_stock:
                print(f"  • {item[0]}: {item[1]} (reorder at {item[2]})")
else:
    print("\n❌ stock_items table doesn't exist - need to seed database!")

conn.close()
