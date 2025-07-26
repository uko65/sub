from flask import Blueprint, request, jsonify, current_app
from app.models import Subscription, Package
from app.models.geography import get_kigali_districts, get_sectors_by_district, get_cells_by_sector
from datetime import datetime

public_bp = Blueprint('public', __name__)

# Package routes
@public_bp.route('/packages', methods=['GET'])
def get_public_packages():
    """Get all packages (public, no authentication)"""
    package_model = Package(current_app.db.db)
    packages = package_model.get_all_packages()
    return jsonify({'packages': packages}), 200

# Geographic data routes
@public_bp.route('/districts', methods=['GET'])
def get_public_districts():
    """Get list of Kigali districts for dropdown (public)"""
    districts = get_kigali_districts()
    return jsonify({'districts': districts}), 200

@public_bp.route('/sectors/<district>', methods=['GET'])
def get_public_sectors(district):
    """Get sectors for a specific district (public)"""
    sectors = get_sectors_by_district(district)
    if not sectors:
        return jsonify({'message': 'Invalid district'}), 400
    return jsonify({'district': district, 'sectors': sectors}), 200

@public_bp.route('/cells/<district>/<sector>', methods=['GET'])
def get_public_cells(district, sector):
    """Get cells for a specific district and sector (public)"""
    cells = get_cells_by_sector(district, sector)
    if not cells:
        return jsonify({'message': 'Invalid district or sector'}), 400
    return jsonify({'district': district, 'sector': sector, 'cells': cells}), 200

# Subscription routes
@public_bp.route('/subscriptions', methods=['POST'])
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
    
    # Validate date format
    try:
        datetime.strptime(data['date_of_subscription'], '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate agreed_refused field
    if data['agreed_refused'] not in ['Agreed', 'Refused']:
        return jsonify({'message': 'agreed_refused must be "Agreed" or "Refused"'}), 400
    
    # Validate package exists
    package_model = Package(current_app.db.db)
    if not package_model.validate_package_exists(data['package']):
        return jsonify({'message': 'Invalid package name'}), 400
    
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.create_subscription(data)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 201

@public_bp.route('/subscriptions', methods=['GET'])
def get_public_subscriptions():
    """Get all subscriptions (public, no authentication)"""
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)
    
    filters = {'is_active': True}
    
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.get_all_subscriptions(filters, page, per_page)
    return jsonify(result), 200

@public_bp.route('/subscriptions/stats', methods=['GET'])
def get_public_subscription_stats():
    """Get basic subscription statistics (public)"""
    subscription_model = Subscription(current_app.db.db)
    
    total_subscriptions = subscription_model.collection.count_documents({"is_active": True})
    total_agreed = subscription_model.collection.count_documents({
        "is_active": True, 
        "agreed_refused": "Agreed"
    })
    
    return jsonify({
        'total_subscriptions': total_subscriptions,
        'total_agreed': total_agreed,
        'success_rate': round((total_agreed / total_subscriptions * 100), 2) if total_subscriptions > 0 else 0
    }), 200