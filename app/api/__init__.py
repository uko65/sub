from flask import Flask
from flask_jwt_extended import JWTManager
from flask_session import Session
from flasgger import Swagger
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
    
    # Initialize Swagger documentation
    from app.utils.swagger import init_swagger
    init_swagger(app)
    
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
    
    # Health check route with Swagger documentation
    @app.route('/api/health')
    def health_check():
        """
        API health check
        ---
        tags:
          - System
        summary: Check API health status
        description: |
          Performs a comprehensive health check of the API and its dependencies.
          This endpoint verifies:
          - API server responsiveness
          - Database connectivity
          - Redis connectivity
          - System timestamp
        responses:
          200:
            description: System is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [healthy]
                  description: Overall system health status
                timestamp:
                  type: string
                  format: date-time
                  description: Current server timestamp
                database:
                  type: string
                  enum: [connected]
                  description: Database connection status
                redis:
                  type: string
                  enum: [connected]
                  description: Redis connection status
                version:
                  type: string
                  description: API version
            examples:
              application/json:
                status: "healthy"
                timestamp: "2024-01-15T10:30:00.000Z"
                database: "connected"
                redis: "connected"
                version: "1.0.0"
          500:
            description: System is unhealthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [unhealthy]
                timestamp:
                  type: string
                  format: date-time
                database:
                  type: string
                  enum: [connected, disconnected]
                redis:
                  type: string
                  enum: [connected, disconnected]
                error:
                  type: string
                  description: Error details
        """
        from datetime import datetime
        from flask import jsonify
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }
        
        try:
            # Test database connection
            app.db.client.admin.command('ping')
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['database'] = 'disconnected'
            health_status['database_error'] = str(e)
        
        try:
            # Test Redis connection
            redis_client.ping()
            health_status['redis'] = 'connected'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['redis'] = 'disconnected'
            health_status['redis_error'] = str(e)
        
        status_code = 200 if health_status['status'] == 'healthy' else 500
        return jsonify(health_status), status_code
    
    # API documentation index route
    @app.route('/api')
    def api_index():
        """
        API Documentation Index
        ---
        tags:
          - System
        summary: API documentation and endpoints overview
        description: |
          Welcome to the Subscription Management API documentation.
          This API provides comprehensive subscription management capabilities including:
          
          **Core Features:**
          - User authentication and authorization
          - Subscription lifecycle management
          - Package management
          - Geographic data for Rwanda/Kigali
          - Analytics and reporting
          - Public endpoints for integration
          
          **Quick Start:**
          1. Register/Login to get JWT token
          2. Include token in Authorization header: `Bearer <token>`
          3. Start making API calls
          
          **Base URL:** `/api`
          **Documentation:** `/api/docs/`
          **Health Check:** `/api/health`
        responses:
          200:
            description: API information
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: API name
                version:
                  type: string
                  description: API version
                description:
                  type: string
                  description: API description
                documentation:
                  type: string
                  description: Documentation URL
                endpoints:
                  type: object
                  description: Available endpoint categories
        """
        from flask import jsonify
        
        return jsonify({
            'name': 'Subscription Management API',
            'version': '1.0.0',
            'description': 'A comprehensive REST API for managing subscription services',
            'documentation': '/api/docs/',
            'health_check': '/api/health',
            'endpoints': {
                'authentication': '/api/auth/',
                'subscriptions': '/api/subscriptions/',
                'packages': '/api/packages/',
                'geography': '/api/geographic/',
                'reports': '/api/reports/',
                'public': '/api/public/'
            },
            'features': [
                'JWT Authentication',
                'Role-based Access Control',
                'Geographic Data Management',
                'Comprehensive Analytics',
                'Public API Endpoints',
                'Data Export Capabilities'
            ]
        }), 200
    
    # Static files route
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        from flask import send_from_directory
        return send_from_directory('static', filename)
    
    return app

def register_error_handlers(app):
    """Register comprehensive error handlers with Swagger documentation"""
    from flask import jsonify
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request contains invalid or missing parameters',
            'status_code': 400
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication credentials are missing or invalid',
            'status_code': 401
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'Insufficient permissions to access this resource',
            'status_code': 403
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The HTTP method is not allowed for this endpoint',
            'status_code': 405
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors"""
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': 'The request data could not be processed',
            'status_code': 422
        }), 422

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests errors"""
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later',
            'status_code': 429
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later',
            'status_code': 500
        }), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors"""
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The service is temporarily unavailable',
            'status_code': 503
        }), 503

def register_jwt_handlers(jwt):
    """Register JWT handlers with detailed error messages"""
    from flask import jsonify
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token Expired',
            'message': 'The JWT token has expired. Please login again',
            'status_code': 401
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid Token',
            'message': 'The JWT token is invalid or malformed',
            'status_code': 401
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Missing Token',
            'message': 'Authorization token is required. Include Bearer token in Authorization header',
            'status_code': 401
        }), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Fresh Token Required',
            'message': 'This operation requires a fresh token. Please login again',
            'status_code': 401
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token Revoked',
            'message': 'The JWT token has been revoked',
            'status_code': 401
        }), 401