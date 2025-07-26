from flask import Blueprint, jsonify, request, send_from_directory, session, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.package import Package
from app.models.geography import get_kigali_districts, get_sectors_by_district, get_cells_by_sector
from app.models.subscription import Subscription
from app.models.database import Database
from app.models.user import User
from app.auth import admin_required, create_tokens
from datetime import datetime, timedelta
bp = Blueprint('private_api', __name__)

# Example: Add one private route
@bp.route('/api/packages', methods=['GET'])
@jwt_required()
def get_packages():
    db = Database()
    package_model = Package(db.db)
    packages = package_model.get_all_packages()
    return jsonify({'packages': packages}), 200

# Continue moving other private routes here...
# Private API endpoints (authentication required)
