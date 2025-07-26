from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.geography import get_kigali_districts, get_sectors_by_district, get_cells_by_sector, KIGALI_DISTRICTS

geography_bp = Blueprint('geography', __name__)

@geography_bp.route('/districts', methods=['GET'])
@jwt_required()
def get_districts():
    """Get list of Kigali districts for dropdown"""
    districts = get_kigali_districts()
    return jsonify({'districts': districts}), 200

@geography_bp.route('/sectors/<district>', methods=['GET'])
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

@geography_bp.route('/cells/<district>/<sector>', methods=['GET'])
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

@geography_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_geographic_data():
    """Get complete geographic hierarchy for frontend dropdowns"""
    return jsonify({
        'kigali_districts': KIGALI_DISTRICTS,
        'districts_list': get_kigali_districts()
    }), 200

@geography_bp.route('/validate', methods=['POST'])
@jwt_required()
def validate_location():
    """Validate a location combination"""
    from flask import request
    from app.models.geography import validate_location as validate_loc
    
    data = request.get_json()
    if not data or 'area' not in data or 'location' not in data:
        return jsonify({'message': 'area and location are required'}), 400
    
    is_valid, message = validate_loc(
        data['area'], 
        data['location'], 
        data.get('cell')
    )
    
    return jsonify({
        'valid': is_valid,
        'message': message
    }), 200