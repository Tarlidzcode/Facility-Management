"""
Quick script to update employee emails from @mri.com to @mrisoftware.com
"""
import os
import tempfile
import sqlite3

# Get database path
temp_dir = tempfile.gettempdir()
db_path = os.path.join(temp_dir, "office_eathon.db")

print(f"📁 Updating database: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First, check what tables exist
print("\n📋 Available tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# Check columns in employees table
print("\n📋 Checking 'employees' table structure:")
cursor.execute("PRAGMA table_info(employees)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Update all @mri.com emails to @mrisoftware.com
print("\n🔄 Updating Employee emails...")
cursor.execute("UPDATE employees SET email = REPLACE(email, '@mri.com', '@mrisoftware.com') WHERE email LIKE '%@mri.com'")
employee_updated = cursor.rowcount
print(f"✅ Updated {employee_updated} Employee records")

print("\n🔄 Updating User emails...")
cursor.execute("UPDATE users SET email = REPLACE(email, '@mri.com', '@mrisoftware.com') WHERE email LIKE '%@mri.com'")
user_updated = cursor.rowcount
print(f"✅ Updated {user_updated} User records")

# Commit changes
conn.commit()

# Verify updates
print("\n📊 Verifying Employee emails:")
cursor.execute("SELECT first_name, last_name, email FROM employees ORDER BY first_name")
employees = cursor.fetchall()
for fname, lname, email in employees:
    print(f"  {fname} {lname}: {email}")

print("\n📊 Verifying User emails:")
cursor.execute("SELECT name, email FROM users ORDER BY name")
users = cursor.fetchall()
for name, email in users:
    print(f"  {name}: {email}")

conn.close()
print("\n✅ Database update complete!")
print("🔄 Try logging in again with @mrisoftware.com emails")
