from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models import Package
from app.auth.decorators import admin_required

packages_bp = Blueprint('packages', __name__)

@packages_bp.route('', methods=['POST'])
@admin_required
def create_package():
    """Create new package"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'price')):
        return jsonify({'message': 'Missing required fields (name, price)'}), 400
    
    package_model = Package(current_app.db.db)
    result = package_model.create_package(data)
    return jsonify(result), 201

@packages_bp.route('', methods=['GET'])
@jwt_required()
def get_packages():
    """Get all packages"""
    package_model = Package(current_app.db.db)
    packages = package_model.get_all_packages()
    return jsonify({'packages': packages}), 200

@packages_bp.route('/<package_id>', methods=['GET'])
@jwt_required()
def get_package(package_id):
    """Get package by ID"""
    package_model = Package(current_app.db.db)
    package = package_model.get_package_by_id(package_id)
    
    if not package:
        return jsonify({'message': 'Package not found'}), 404
    
    return jsonify({'package': package}), 200

@packages_bp.route('/<package_id>', methods=['PUT'])
@admin_required
def update_package(package_id):
    """Update package"""
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    package_model = Package(current_app.db.db)
    result = package_model.update_package(package_id, data)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 200

@packages_bp.route('/<package_id>', methods=['DELETE'])
@admin_required
def delete_package(package_id):
    """Delete package (soft delete)"""
    package_model = Package(current_app.db.db)
    result = package_model.delete_package(package_id)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 200

@packages_bp.route('/active', methods=['GET'])
def get_active_packages():
    """Get all active packages (public endpoint)"""
    package_model = Package(current_app.db.db)
    packages = package_model.get_all_packages()
    return jsonify({'packages': packages}), 200