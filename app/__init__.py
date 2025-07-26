from flask import Flask
from flask_jwt_extended import JWTManager
from flask_session import Session
import redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(config_class=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        from app.config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    jwt = JWTManager(app)
    
    # Initialize Redis for sessions
    redis_client = redis.StrictRedis(
        host=app.config.get('REDIS_HOST', 'localhost'),
        port=app.config.get('REDIS_PORT', 6379),
        db=app.config.get('REDIS_DB', 0)
    )
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_client
    Session(app)
    
    # Initialize database
    from app.models.database import Database
    app.db = Database(app.config['MONGO_URI'])
    
    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.subscriptions import subscriptions_bp
    from app.api.packages import packages_bp
    from app.api.geography import geography_bp
    from app.api.reports import reports_bp
    from app.api.public import public_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(packages_bp, url_prefix='/api/packages')
    app.register_blueprint(geography_bp, url_prefix='/api/geographic')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(public_bp, url_prefix='/api/public')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register JWT handlers
    register_jwt_handlers(jwt)
    
    # Health check route
    @app.route('/api/health')
    def health_check():
        """API health check"""
        from datetime import datetime
        from flask import jsonify
        
        try:
            app.db.client.admin.command('ping')
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'connected'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'disconnected',
                'error': str(e)
            }), 500
    
    # Static files route
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        from flask import send_from_directory
        return send_from_directory('static', filename)
    
    return app

def register_error_handlers(app):
    """Register error handlers"""
    from flask import jsonify
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'message': 'Unauthorized access'}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'message': 'Forbidden access'}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500

def register_jwt_handlers(jwt):
    """Register JWT handlers"""
    from flask import jsonify
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'message': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Authorization token required'}), 401