"""
Start the Employee Check-In Portal on port 5002
This is a standalone portal that employees can use to check in/out
"""

import os
import sys

# Add the current directory to the path to import models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from employee_portal import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏢 EMPLOYEE CHECK-IN PORTAL")
    print("="*60)
    print("📍 Starting standalone employee portal...")
    print("🌐 Access at: http://localhost:5002")
    print("📊 This portal will update presence tracking in real-time")
    print("🔄 Shared database ensures main app sees all updates")
    print("="*60)
    print("💡 Test credentials:")
    print("   Email: eathon.groenewald@mrisoftware.com")
    print("   Password: password123")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)
