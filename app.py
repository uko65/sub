from flask import Flask, request, jsonify, send_from_directory, session, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from app.views.public import *
from app.views.admin import *
from flask import Flask, request, jsonify, send_from_directory, session, make_response
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from models import Database, User, Subscription, Package, get_kigali_districts, get_sectors_by_district, get_cells_by_sector
from auth import admin_required, create_tokens
from datetime import datetime
import os
from dotenv import load_dotenv
import redis
from flask_session import Session

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize JWT
jwt = JWTManager(app)

# Initialize Database
db = Database(app.config['MONGO_URI'])

# Initialize models
user_model = User(db.db)
subscription_model = Subscription(db.db)
package_model = Package(db.db)

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)  # Removed decode_responses=True for session compatibility
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_client
Session(app)

# ===============================
# Geographic Data Routes
# ===============================

@app.route('/api/public/packages', methods=['GET'])
def get_public_packages():
    """Get all packages (public, no authentication)"""
    packages = package_model.get_all_packages()
    return jsonify({'packages': packages}), 200

@app.route('/api/public/districts', methods=['GET'])
def get_public_districts():
    """Get list of Kigali districts for dropdown (public)"""
    districts = get_kigali_districts()
    return jsonify({'districts': districts}), 200

@app.route('/api/public/sectors/<district>', methods=['GET'])
def get_public_sectors(district):
    """Get sectors for a specific district (public)"""
    sectors = get_sectors_by_district(district)
    if not sectors:
        return jsonify({'message': 'Invalid district'}), 400
    return jsonify({'district': district, 'sectors': sectors}), 200

@app.route('/api/public/cells/<district>/<sector>', methods=['GET'])
def get_public_cells(district, sector):
    """Get cells for a specific district and sector (public)"""
    cells = get_cells_by_sector(district, sector)
    if not cells:
        return jsonify({'message': 'Invalid district or sector'}), 400
    return jsonify({'district': district, 'sector': sector, 'cells': cells}), 200

@app.route('/api/geographic/districts', methods=['GET'])
@jwt_required()
def get_districts():
    """Get list of Kigali districts for dropdown"""
    districts = get_kigali_districts()
    return jsonify({'districts': districts}), 200

@app.route('/api/geographic/sectors/<district>', methods=['GET'])
@jwt_required()
def get_sectors(district):
    """Get sectors for a specific district"""
    sectors = get_sectors_by_district(district)
    if not sectors:
        return jsonify({'message': 'Invalid district'}), 400
    
    return jsonify({
        'district': district,
        'sectors': sectors
    }), 200

@app.route('/api/geographic/cells/<district>/<sector>', methods=['GET'])
@jwt_required()
def get_cells(district, sector):
    """Get cells for a specific district and sector"""
    cells = get_cells_by_sector(district, sector)
    if not cells:
        return jsonify({'message': 'Invalid district or sector'}), 400
    
    return jsonify({
        'district': district,
        'sector': sector,
        'cells': cells
    }), 200

@app.route('/api/geographic/all', methods=['GET'])
@jwt_required()
def get_all_geographic_data():
    """Get complete geographic hierarchy for frontend dropdowns"""
    from models import KIGALI_DISTRICTS
    return jsonify({
        'kigali_districts': KIGALI_DISTRICTS,
        'districts_list': get_kigali_districts()
    }), 200

# ===============================
# Authentication Routes
# ===============================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user (admin only)"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    result = user_model.create_user(
        data['username'], 
        data['email'], 
        data['password'],
        data.get('role', 'user')
    )
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify({'message': 'User created successfully', 'user_id': result['user_id']}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Username and password required'}), 400
    user = user_model.authenticate(data['username'], data['password'])
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    access_token, refresh_token = create_tokens(user['user_id'])
    # Store token in Redis with user_id as key
    redis_client.set(f"user_token:{user['user_id']}", access_token, ex=86400)  # 1 day expiry
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': access_token}), 200

# ===============================
# Package Routes
# ===============================

@app.route('/api/packages', methods=['POST'])
@admin_required
def create_package():
    """Create new package"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'price')):
        return jsonify({'message': 'Missing required fields (name, price)'}), 400
    
    result = package_model.create_package(data)
    return jsonify(result), 201

@app.route('/api/packages', methods=['GET'])
@jwt_required()
def get_packages():
    """Get all packages"""
    packages = package_model.get_all_packages()
    return jsonify({'packages': packages}), 200

# ===============================
# Subscription Routes
# ===============================

@app.route('/api/subscriptions', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create new subscription"""
    data = request.get_json()
    
    required_fields = [
        'phone_number', 'email', 'child_name', 'parent_name', 
        'agreed_refused', 'package', 'date_of_subscription', 
        'area', 'location'
    ]
    
    if not data or not all(k in data for k in required_fields):
        return jsonify({'message': f'Missing required fields: {required_fields}'}), 400
    
    # Validate date format
    try:
        datetime.strptime(data['date_of_subscription'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate agreed_refused field
    if data['agreed_refused'] not in ['Agreed', 'Refused']:
        return jsonify({'message': 'agreed_refused must be "Agreed" or "Refused"'}), 400
    
    # Validate area and location through the model
    result = subscription_model.create_subscription(data)
    if not result:
        return jsonify({'message': 'Subscription creation failed.'}), 500
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 201

@app.route('/api/public/subscriptions', methods=['GET'])
def get_public_subscriptions():
    """Get all subscriptions (public, no authentication)"""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    filters = {'is_active': True}
    result = subscription_model.get_all_subscriptions(filters, page, per_page)
    return jsonify(result), 200
    
    # Validate area and location through the model
    result = subscription_model.create_subscription(data)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 201

@app.route('/api/public/subscriptions', methods=['POST'])
def public_create_subscription():
    """Create new subscription (public, no authentication)"""
    data = request.get_json()
    required_fields = [
        'phone_number', 'email', 'child_name', 'parent_name',
        'agreed_refused', 'package', 'date_of_subscription',
        'area', 'location'
    ]
    if not data or not all(k in data for k in required_fields):
        return jsonify({'message': f'Missing required fields: {required_fields}'}), 400
    try:
        datetime.strptime(data['date_of_subscription'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    if data['agreed_refused'] not in ['Agreed', 'Refused']:
        return jsonify({'message': 'agreed_refused must be "Agreed" or "Refused"'}), 400
    # Validate area against actual districts
    from app.models.geography import get_kigali_districts
    allowed_areas = get_kigali_districts()
    if data['area'] not in allowed_areas:
        return jsonify({'message': f'Invalid area. Must be one of: {allowed_areas}'}), 400
    result = subscription_model.create_subscription(data)
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    return jsonify(result), 201

@app.route('/api/subscriptions', methods=['GET'])
@jwt_required()
def get_subscriptions():
    """Get all subscriptions with optional filters"""
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    
    # Build filters
    filters = {}
    if request.args.get('agreed_refused'):
        filters['agreed_refused'] = request.args.get('agreed_refused')
    if request.args.get('payment_status'):
        filters['payment_status'] = request.args.get('payment_status')
    if request.args.get('area'):
        filters['area'] = request.args.get('area')
    if request.args.get('package'):
        filters['package'] = request.args.get('package')
    
    filters['is_active'] = True
    
    result = subscription_model.get_all_subscriptions(filters, page, per_page)
    return jsonify(result), 200

@app.route('/api/subscriptions/<subscription_id>', methods=['GET'])
@jwt_required()
def get_subscription(subscription_id):
    """Get subscription by ID"""
    subscription = subscription_model.get_subscription_by_id(subscription_id)
    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404
    
    return jsonify({'subscription': subscription}), 200

@app.route('/api/subscriptions/<subscription_id>', methods=['PUT'])
@jwt_required()
def update_subscription(subscription_id):
    """Update subscription"""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    result = subscription_model.update_subscription(subscription_id, data)
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 200

@app.route('/api/subscriptions/<subscription_id>', methods=['DELETE'])
@admin_required
def delete_subscription(subscription_id):
    """Delete subscription (soft delete)"""
    result = subscription_model.delete_subscription(subscription_id)
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 200

# ===============================
# Analytics Routes
# ===============================

@app.route('/api/reports/subscription-summary', methods=['GET'])
@jwt_required()
def subscription_analytics():
    """Get subscription analytics"""
    analytics = subscription_model.get_analytics()
    return jsonify(analytics), 200

@app.route('/api/reports/upcoming-renewals', methods=['GET'])
@jwt_required()
def upcoming_renewals():
    """Get subscriptions due for renewal in next 7 days"""
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow() + timedelta(days=7)
    filters = {
        'is_active': True,
        'renew_subscription_by': {'$lte': end_date},
        'agreed_refused': 'Agreed'
    }
    
    result = subscription_model.get_all_subscriptions(filters)
    return jsonify({
        'upcoming_renewals': result['subscriptions'],
        'total_renewals': result['total']
    }), 200

# ===============================
# Health Check Route
# ===============================

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    try:
        # Test database connection
        db.client.admin.command('ping')
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

# ===============================
# Static Files Route
# ===============================

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# ===============================
# Error Handlers
# ===============================

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

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'message': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': 'Authorization token required'}), 401

@app.route('/api/debug/users', methods=['GET'])
def list_users():
    users = list(user_model.collection.find())
    for user in users:
        user['_id'] = str(user['_id'])
        user['password'] = str(user['password'])  # Show hashed password for debug
    return jsonify({'users': users}), 200

@app.route('/api/debug/redis-token/<user_id>', methods=['GET'])
def debug_redis_token(user_id):
    token = redis_client.get(f"user_token:{user_id}")
    if token:
        return f"Token for user {user_id}: {token}", 200
    else:
        return f"No token found for user {user_id}", 404

@app.route('/api/debug/session-set', methods=['GET'])
def debug_session_set():
    session['test_key'] = 'test_value'
    return 'Session value set: test_key = test_value', 200

@app.route('/api/debug/session-get', methods=['GET'])
def debug_session_get():
    value = session.get('test_key', None)
    return f"Session value: test_key = {value}", 200

@app.route('/api/debug/set-cookie', methods=['GET'])
def debug_set_cookie():
    resp = make_response('Cookie set: test_cookie=test_value')
    resp.set_cookie('test_cookie', 'test_value', max_age=3600)
    return resp

@app.route('/api/debug/cookies', methods=['GET'])
def debug_cookies():
    """Show cookies set in the browser"""
    test_cookie = request.cookies.get('test_cookie', 'not_set')
    return f"Cookie value: test_cookie = {test_cookie}", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)