from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from functools import wraps
from flask import jsonify, request
from bson import ObjectId

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from app import db, User
        current_user_id = get_jwt_identity()
        user_model = User(db.db)
        user = user_model.collection.find_one({"_id": ObjectId(current_user_id)})
        
        if not user or user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def create_tokens(user_id):
    """Create access and refresh tokens"""
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return access_token, refresh_token
