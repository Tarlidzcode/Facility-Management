from flask import Blueprint, request, jsonify, current_app
from app import create_app
import json
import os
from html.parser import HTMLParser
from datetime import datetime


ai_bp = Blueprint('ai', __name__)


# Knowledge base about the site: pages, important API endpoints and model summaries.
SITE_KB = {
    'pages': [
        'Dashboard (/) - metrics, charts, recent activity',
        'Employees (/employees) - manage employees',
        'Coffee (/coffee) - coffee machine status and usage',
        'Temperature (/temperature) - control and monitor temperature',
        'Stock (/stock) - inventory and low-stock alerts',
        'Presence (/presence) - presence tracking and reports',
    ],
    'api_endpoints': [
        '/api/dashboard (GET) - returns metrics and chart data for the dashboard',
        '/api/employees (GET/POST) - list or create employees (JWT protected)',
        '/api/offices (GET/POST) - list or create offices (JWT protected)',
        '/api/assets (GET/POST) - asset management (JWT protected)',
        '/api/bookings (GET/POST) - booking resources (JWT protected)',
        '/api/maintenances (GET/POST) - maintenance records (JWT protected)',
        '/api/me (GET) - current user details (JWT protected)',
        '/api/ai (POST) - server-side AI endpoint used by the frontend (optional OpenAI integration)',
    ],
    'models': {
        'User': 'id, email, name, is_admin, created_at',
        'Office': 'id, name, address, description, created_at',
        'Employee': 'id, first_name, last_name, email, phone, role, office_id',
        'Asset': 'id, name, serial, status, office_id',
        'Booking': 'id, resource, user_id, start_time, end_time, notes',
        'Maintenance': 'id, asset_id, description, status',
    }
}


def scan_static_nav(static_html_path):
    """Parse the static/index.html file to extract nav item texts and return as list.
    Uses Python's built-in HTMLParser to avoid external dependencies.
    """
    class NavParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_aside = False
            self.in_nav = False
            self.in_a = False
            self.current = []
            self.pages = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'aside' and 'class' in attrs and 'sidebar' in attrs['class']:
                self.in_aside = True
            if self.in_aside and tag == 'nav' and 'class' in attrs and 'nav' in attrs['class']:
                self.in_nav = True
            if self.in_nav and tag == 'a':
                self.in_a = True
                self.current = []

        def handle_endtag(self, tag):
            if tag == 'aside' and self.in_aside:
                self.in_aside = False
            if tag == 'nav' and self.in_nav:
                self.in_nav = False
            if tag == 'a' and self.in_a:
                self.in_a = False
                text = ''.join(self.current).strip()
                if text:
                    # normalize whitespace
                    text = ' '.join(text.split())
                    self.pages.append(text + ' (static)')

        def handle_data(self, data):
            if self.in_a:
                self.current.append(data)

    pages = []
    try:
        with open(static_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            parser = NavParser()
            parser.feed(content)
            pages = parser.pages
    except Exception:
        pages = []
    return pages


def refresh_site_kb(workspace_root=None):
    """Refresh SITE_KB['pages'] by scanning static HTML. Persist a JSON copy and log the change."""
    static_path = os.path.join(workspace_root or os.getcwd(), 'static', 'index.html')
    pages = scan_static_nav(static_path)
    if pages:
        SITE_KB['pages'] = pages
    # persist
    try:
        out = os.path.join(workspace_root or os.getcwd(), 'site_kb.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(SITE_KB, f, indent=2)
        # append change log
        logp = os.path.join(workspace_root or os.getcwd(), 'ai_changes.log')
        with open(logp, 'a', encoding='utf-8') as lf:
            lf.write(f"{datetime.utcnow().isoformat()}Z - refreshed SITE_KB from {static_path}\n")
    except Exception:
        pass
    return SITE_KB['pages']


def get_live_dashboard():
    """Create an app context and call the internal /api/dashboard endpoint
    using the Flask test client so we can return current demo metrics.
    This avoids making external HTTP requests and works in-process.
    """
    try:
        app = create_app()
        client = app.test_client()
        res = client.get('/api/dashboard')
        if res.status_code == 200:
            return res.get_json()
    except Exception:
        pass
    return None


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Richer assistant that knows about the site and can return live dashboard
    data when asked. Accepts JSON { message: '...'} and returns { reply: '...' }.
    """
    data = request.get_json(force=True, silent=True) or {}
    msg = (data.get('message') or '').strip()
    low = msg.lower()

    if not msg:
        return jsonify({'reply': "Hi — ask me about the dashboard, coffee, temperature, stock, or pages on this site."}), 200

    # Help and knowledge queries
    if any(p in low for p in ('help', 'what can you do', 'commands')):
        pages = '\n'.join(f"- {p}" for p in SITE_KB['pages'])
        reply = f"I can answer questions about this Office Manager demo. Known pages:\n{pages}\nYou can also ask for live metrics (e.g. 'how many employees are in') or 'coffee status'."
        return jsonify({'reply': reply}), 200

    if any(p in low for p in ('pages', 'site', 'what pages', 'navigation')):
        reply = 'This site includes these pages:\n' + '\n'.join(SITE_KB['pages'])
        return jsonify({'reply': reply}), 200

    # live dashboard metrics
    if any(p in low for p in ('how many', 'employees', 'in office', 'coffee today', 'temperature', 'low stock')):
        live = get_live_dashboard()
        if live and isinstance(live, dict):
            m = live.get('metrics', {})
            if 'employees' in low or 'how many' in low or 'in office' in low:
                reply = f"There are {m.get('employees_in', 'unknown')} people in the office out of {m.get('employees_total','unknown')}."
                return jsonify({'reply': reply}), 200
            if 'coffee' in low:
                reply = f"Coffee used today: {m.get('coffee_today','unknown')} cups. Beans level appears low (approx {m.get('coffee_level',12)}%)."
                return jsonify({'reply': reply}), 200
            if 'temperature' in low or 'temp' in low:
                reply = f"Current office temperature: {m.get('temperature','unknown')}°C."
                return jsonify({'reply': reply}), 200
            if 'stock' in low or 'low stock' in low:
                reply = f"There are {m.get('low_stock','unknown')} low-stock items."
                return jsonify({'reply': reply}), 200

    # API / model facts
    if any(p in low for p in ('api', 'endpoints', 'models', 'schema')):
        apis = '\n'.join(SITE_KB['api_endpoints'])
        models = '\n'.join(f"{k}: {v}" for k, v in SITE_KB['models'].items())
        reply = f"Important API endpoints:\n{apis}\n\nModels and key fields:\n{models}"
        return jsonify({'reply': reply}), 200

    # fallback to canned replies
    if 'coffee' in low:
        return jsonify({'reply': "Coffee machine beans are low (approx 12%). Water level is 68% and milk 45%."}), 200
    if 'temperature' in low or 'temp' in low:
        return jsonify({'reply': "The current office temperature is 22°C."}), 200

    # default echo-like fallback
    return jsonify({'reply': f"You said: {msg}. I can answer about pages, metrics, stock, coffee, and temperature."}), 200


@ai_bp.route('/refresh-kb', methods=['POST'])
def refresh_kb():
    """Trigger a refresh of the SITE_KB by scanning the static HTML nav.
    POST body may include { workspace_root: '/abs/path' } to point to the repo root.
    """
    data = request.get_json(silent=True) or {}
    root = data.get('workspace_root')
    pages = refresh_site_kb(workspace_root=root)
    return jsonify({'updated_pages': pages}), 200


if __name__ == '__main__':
    # simple CLI mode to refresh the kb when running the file directly
    root = os.getcwd()
    refreshed = refresh_site_kb(workspace_root=root)
    print('Refreshed SITE_KB pages:')
    for p in refreshed:
        print(' -', p)
