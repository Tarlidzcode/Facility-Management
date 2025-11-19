#!/usr/bin/env python
"""
Verify temperature API: seed an office if missing, list offices, and fetch /api/temperature/comparison
"""
import json
import sys
import time

from app import create_app
from models import Office
import requests

app = create_app()
with app.app_context():
    o = Office.query.filter_by(name='Seeded OpenMeteo Office').first()
    if o:
        print('Seed exists:', o.id, o.location)
    else:
        o = Office(name='Seeded OpenMeteo Office', location='51.5074,-0.1278')
        from app import db as _db
        _db.session.add(o)
        _db.session.commit()
        print('Created seed office id', o.id)

    offices = Office.query.all()
    print('Found', len(offices), 'offices')
    for o in offices:
        print('-', o.id, o.name, getattr(o, 'location', None))

# Try the API with retries
url = 'http://127.0.0.1:5000/api/temperature/comparison'
for i in range(12):
    try:
        r = requests.get(url, timeout=5)
        print('\nHTTP', r.status_code)
        try:
            js = r.json()
            if isinstance(js, list) and len(js) > 0:
                print(json.dumps(js[0], indent=2)[:2000])
            else:
                print(json.dumps(js, indent=2)[:2000])
        except Exception:
            print('Non-JSON response:', r.text[:1000])
        sys.exit(0)
    except Exception as e:
        print(f'Attempt {i+1}/12 failed: {e}')
        time.sleep(1)

print('All attempts failed')
sys.exit(1)
