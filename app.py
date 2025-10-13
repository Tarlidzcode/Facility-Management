# app.py - main Flask application
import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///office.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devsecret')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwtsecret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, supports_credentials=True)

    # register blueprints
    from auth import auth_bp
    from api import api_bp
    from ai import ai_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/ai')

    @app.route('/')
    def index():
        # simple server-rendered login page to test quickly
        return app.send_static_file('index.html')

    # Serve dedicated pages for sidebar items (static HTML files under static/pages/)
    @app.route('/employees')
    def employees_page():
        return app.send_static_file('pages/employees.html')

    @app.route('/coffee')
    def coffee_page():
        return app.send_static_file('pages/coffee.html')

    @app.route('/temperature')
    def temperature_page():
        return app.send_static_file('pages/temperature.html')

    @app.route('/stock')
    def stock_page():
        return app.send_static_file('pages/stock.html')

    @app.route('/presence')
    def presence_page():
        return app.send_static_file('pages/presence.html')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
