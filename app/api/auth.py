from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flasgger import swag_from
from app.models import User
from app.auth.decorators import admin_required, create_tokens
from app.docs.swagger_specs import (
    auth_login_spec, auth_register_spec
)
import redis

auth_bp = Blueprint('auth', __name__)

def get_redis_client():
    return current_app.config['SESSION_REDIS']

@auth_bp.route('/login', methods=['POST'])
@swag_from(auth_login_spec)
def login():
    """
    User login endpoint
    ---
    This endpoint authenticates users and returns JWT tokens for API access.
    The access token should be included in the Authorization header for authenticated requests.
    """
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

@auth_bp.route('/register', methods=['POST'])
@swag_from(auth_register_spec)
@admin_required
def register():
    """
    Register new user (admin only)
    ---
    This endpoint allows administrators to create new user accounts.
    Requires admin authentication and validates user data before creation.
    """
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    user_model = User(current_app.db.db)
    result = user_model.create_user(
        data['username'], 
        data['email'], 
        data['password'],
        data.get('role', 'user')
    )
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify({'message': 'User created successfully', 'user_id': result['user_id']}), 201

@auth_bp.route('/refresh', methods=['POST'])
@swag_from({
    "tags": ["Authentication"],
    "summary": "Refresh access token",
    "description": "Generate a new access token using a valid refresh token.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "required": True,
            "type": "string",
            "description": "Refresh token in Bearer format"
        }
    ],
    "responses": {
        "200": {
            "description": "Token refreshed successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "description": "New JWT access token"
                    }
                }
            }
        },
        "401": {
            "description": "Invalid or expired refresh token",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
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
@swag_from({
    "tags": ["Authentication"],
    "summary": "User logout",
    "description": "Logout user by invalidating the current session token.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Logged out successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            }
        },
        "401": {
            "description": "Unauthorized - Invalid token",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
@jwt_required()
def logout():
    """User logout - remove token from Redis"""
    current_user_id = get_jwt_identity()
    
    # Remove token from Redis
    redis_client = get_redis_client()
    redis_client.delete(f"user_token:{current_user_id}")
    
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile', methods=['GET'])
@swag_from({
    "tags": ["Authentication"],
    "summary": "Get current user profile",
    "description": "Retrieve the profile information of the currently authenticated user.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Profile retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "user": {"$ref": "#/definitions/User"}
                }
            }
        },
        "404": {
            "description": "User not found",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "401": {
            "description": "Unauthorized - Invalid token",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
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
@swag_from({
    "tags": ["Authentication"],
    "summary": "Update current user profile",
    "description": "Update the profile information of the currently authenticated user. Role cannot be changed via this endpoint.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "profile_data",
            "in": "body",
            "required": True,
            "description": "Profile update data",
            "schema": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 50,
                        "description": "New username (must be unique)"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "New email address (must be unique)"
                    },
                    "password": {
                        "type": "string",
                        "minLength": 6,
                        "description": "New password"
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Profile updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            }
        },
        "400": {
            "description": "Bad request - Validation error",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "401": {
            "description": "Unauthorized - Invalid token",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
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

# Debug routes (remove in production)
@auth_bp.route('/debug/users', methods=['GET'])
@swag_from({
    "tags": ["Authentication"],
    "summary": "Debug: List all users (Admin only)",
    "description": "Development endpoint to list all users. Should be removed in production.",
    "security": [{"Bearer": []}],
    "responses": {
        "200": {
            "description": "Users listed successfully",
            "schema": {
                "allOf": [
                    {"$ref": "#/definitions/PaginatedResponse"},
                    {
                        "type": "object",
                        "properties": {
                            "users": {
                                "type": "array",
                                "items": {"$ref": "#/definitions/User"}
                            }
                        }
                    }
                ]
            }
        },
        "403": {
            "description": "Forbidden - Admin access required",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
@admin_required
def list_users():
    """Debug: List all users"""
    user_model = User(current_app.db.db)
    users = user_model.get_all_users()
    return jsonify(users), 200

@auth_bp.route('/debug/redis-token/<user_id>', methods=['GET'])
@swag_from({
    "tags": ["Authentication"],
    "summary": "Debug: Check Redis token for user (Admin only)",
    "description": "Development endpoint to check stored tokens. Should be removed in production.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "User ID to check token for"
        }
    ],
    "responses": {
        "200": {
            "description": "Token found",
            "schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "token": {"type": "string"}
                }
            }
        },
        "404": {
            "description": "Token not found",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "403": {
            "description": "Forbidden - Admin access required",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
@admin_required
def debug_redis_token(user_id):
    """Debug: Check Redis token for user"""
    redis_client = get_redis_client()
    token = redis_client.get(f"user_token:{user_id}")
    if token:
        return jsonify({'user_id': user_id, 'token': token.decode('utf-8')}), 200
    else:
        return jsonify({'message': f'No token found for user {user_id}'}), 404