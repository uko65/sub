from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models import Subscription
from app.auth.decorators import admin_required
from datetime import datetime

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('', methods=['POST'])
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
    
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.create_subscription(data)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 201

@subscriptions_bp.route('', methods=['GET'])
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
    
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.get_all_subscriptions(filters, page, per_page)
    return jsonify(result), 200

@subscriptions_bp.route('/<subscription_id>', methods=['GET'])
@jwt_required()
def get_subscription(subscription_id):
    """Get subscription by ID"""
    subscription_model = Subscription(current_app.db.db)
    subscription = subscription_model.get_subscription_by_id(subscription_id)
    
    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404
    
    return jsonify({'subscription': subscription}), 200

@subscriptions_bp.route('/<subscription_id>', methods=['PUT'])
@jwt_required()
def update_subscription(subscription_id):
    """Update subscription"""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.update_subscription(subscription_id, data)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 200

@subscriptions_bp.route('/<subscription_id>', methods=['DELETE'])
@admin_required
def delete_subscription(subscription_id):
    """Delete subscription (soft delete)"""
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.delete_subscription(subscription_id)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 200

@subscriptions_bp.route('/bulk-update', methods=['PUT'])
@admin_required
def bulk_update_subscriptions():
    """Bulk update multiple subscriptions"""
    data = request.get_json()
    
    if not data or 'subscription_ids' not in data or 'update_data' not in data:
        return jsonify({'message': 'Missing subscription_ids or update_data'}), 400
    
    subscription_ids = data['subscription_ids']
    update_data = data['update_data']
    
    if not isinstance(subscription_ids, list) or not subscription_ids:
        return jsonify({'message': 'subscription_ids must be a non-empty list'}), 400
    
    subscription_model = Subscription(current_app.db.db)
    results = []
    
    for subscription_id in subscription_ids:
        result = subscription_model.update_subscription(subscription_id, update_data)
        results.append({
            'subscription_id': subscription_id,
            'result': result
        })
    
    return jsonify({
        'message': f'Bulk update completed for {len(subscription_ids)} subscriptions',
        'results': results
    }), 200

@subscriptions_bp.route('/search', methods=['GET'])
@jwt_required()
def search_subscriptions():
    """Search subscriptions by various criteria"""
    query_param = request.args.get('q', '').strip()
    
    if not query_param:
        return jsonify({'message': 'Search query parameter "q" is required'}), 400
    
    subscription_model = Subscription(current_app.db.db)
    
    # Search in multiple fields
    search_filters = {
        'is_active': True,
        '$or': [
            {'phone_number': {'$regex': query_param, '$options': 'i'}},
            {'email': {'$regex': query_param, '$options': 'i'}},
            {'child_name': {'$regex': query_param, '$options': 'i'}},
            {'parent_name': {'$regex': query_param, '$options': 'i'}},
            {'area': {'$regex': query_param, '$options': 'i'}},
            {'location': {'$regex': query_param, '$options': 'i'}}
        ]
    }
    
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    
    result = subscription_model.get_all_subscriptions(search_filters, page, per_page)
    return jsonify(result), 200