from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.models import User
from app.auth.decorators import admin_required, create_tokens
import redis

auth_bp = Blueprint('auth', __name__)

# Get Redis client (initialized in app factory)
def get_redis_client():
    return current_app.config['SESSION_REDIS']

@auth_bp.route('/register', methods=['POST'])
@admin_required
def register():
    """Register new user (admin only)"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user_model = User(current_app.db.db)
    result = user_model.update_user(current_user_id, data)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify({'message': 'Profile updated successfully'}), 200

# Debug routes (remove in production)
@auth_bp.route('/debug/users', methods=['GET'])
@admin_required
def list_users():
    """Debug: List all users"""
    user_model = User(current_app.db.db)
    users = user_model.get_all_users()
    return jsonify(users), 200

@auth_bp.route('/debug/redis-token/<user_id>', methods=['GET'])
@admin_required
def debug_redis_token(user_id):
    """Debug: Check Redis token for user"""
    redis_client = get_redis_client()
    token = redis_client.get(f"user_token:{user_id}")
    if token:
        return jsonify({'user_id': user_id, 'token': token.decode('utf-8')}), 200
    else:
        return jsonify({'message': f'No token found for user {user_id}'}), 404
    result = user_model.create_user(
        data['username'], 
        data['email'], 
        data['password'],
        data.get('role', 'user')
    )
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify({'message': 'User created successfully', 'user_id': result['user_id']}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Username and password required'}), 400
    
    user_model = User(current_app.db.db)
    user = user_model.authenticate(data['username'], data['password'])
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    
    access_token, refresh_token = create_tokens(user['user_id'])
    
    # Store token in Redis with user_id as key
    redis_client = get_redis_client()
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

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    # Update token in Redis
    redis_client = get_redis_client()
    redis_client.set(f"user_token:{current_user_id}", access_token, ex=86400)
    
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout - remove token from Redis"""
    current_user_id = get_jwt_identity()
    
    # Remove token from Redis
    redis_client = get_redis_client()
    redis_client.delete(f"user_token:{current_user_id}")
    
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user_model = User(current_app.db.db)
    user = user_model.get_user_by_id(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'user': user}), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    # Remove sensitive fields that shouldn't be updated via profile
    data.pop('role', None)
    data.pop('user_id', None)
    data.pop('_id', None)
    
    user_model = User(current_app.db.db)
    result = user_model.update_user(current_user_id, data)
    if 'error' in result:
        return jsonify({'message': result['error']}), 400

    return jsonify({'message': 'Profile updated successfully'}), 200