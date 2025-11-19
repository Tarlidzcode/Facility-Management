#!/usr/bin/env python3
"""Seed an Office row directly into the SQLite DB used by the Flask app.
This avoids SQLAlchemy import/app-context issues when seeding from an external script.
"""
import sqlite3
import os

# Adjust path to the instance DB used by the app
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'office.db')
DB_PATH = os.path.abspath(DB_PATH)

if not os.path.exists(DB_PATH):
    print('DB not found at', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    # Find a table that looks like Office
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    rows = cur.fetchall()
    tables = [r[0] for r in rows]
    print('Tables in DB:', tables)

    # Try common office table names
    candidates = [t for t in tables if 'office' in t.lower()]
    if not candidates:
        print('No office-like table found. Aborting.')
        raise SystemExit(1)

    table = candidates[0]
    print('Using table:', table)

    name = 'Seeded OpenMeteo Office'
    # Check if seed exists
    cur.execute(f"SELECT id, name, location FROM {table} WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        print('Seed already exists:', row)
    else:
        try:
            # Try inserting with name, location and created_at if columns exist
            # We'll inspect columns
            cur.execute(f"PRAGMA table_info({table})")
            cols = [c[1] for c in cur.fetchall()]
            print('Columns for', table, cols)
            if 'location' in cols and 'name' in cols:
                if 'created_at' in cols:
                    cur.execute(f"INSERT INTO {table} (name, location, created_at) VALUES (?, ?, datetime('now'))", (name, '51.5074,-0.1278'))
                else:
                    cur.execute(f"INSERT INTO {table} (name, location) VALUES (?, ?)", (name, '51.5074,-0.1278'))
                conn.commit()
                print('Inserted seed id', cur.lastrowid)
            else:
                print('Required columns (name, location) not found on table. Aborting.')
        except Exception as e:
            print('Insert failed:', e)
finally:
    conn.close()
