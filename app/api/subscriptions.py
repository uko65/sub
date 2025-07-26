from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from app.models import Subscription
from app.auth.decorators import admin_required
from app.docs.swagger_specs import (
    subscription_create_spec, subscription_list_spec, subscription_search_spec
)
from datetime import datetime

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('', methods=['POST'])
@swag_from(subscription_create_spec)
@jwt_required()
def create_subscription():
    """
    Create new subscription
    ---
    This endpoint creates a new subscription with comprehensive validation
    for geographic data, package existence, and data integrity.
    """
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
@swag_from(subscription_list_spec)
@jwt_required()
def get_subscriptions():
    """
    Get all subscriptions with optional filters
    ---
    Retrieve paginated subscriptions with comprehensive filtering options
    for efficient data management and reporting.
    """
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
@swag_from({
    "tags": ["Subscriptions"],
    "summary": "Get subscription by ID",
    "description": "Retrieve a specific subscription by its unique identifier.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "subscription_id",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Unique subscription identifier"
        }
    ],
    "responses": {
        "200": {
            "description": "Subscription retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "subscription": {"$ref": "#/definitions/Subscription"}
                }
            }
        },
        "404": {
            "description": "Subscription not found",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "401": {
            "description": "Unauthorized - Invalid token",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
@jwt_required()
def get_subscription(subscription_id):
    """Get subscription by ID"""
    subscription_model = Subscription(current_app.db.db)
    subscription = subscription_model.get_subscription_by_id(subscription_id)
    
    if not subscription:
        return jsonify({'message': 'Subscription not found'}), 404
    
    return jsonify({'subscription': subscription}), 200

@subscriptions_bp.route('/<subscription_id>', methods=['PUT'])
@swag_from({
    "tags": ["Subscriptions"],
    "summary": "Update subscription",
    "description": "Update an existing subscription with validation for all fields including geographic data.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "subscription_id",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Unique subscription identifier"
        },
        {
            "name": "update_data",
            "in": "body",
            "required": True,
            "description": "Fields to update",
            "schema": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "pattern": "^\\+250[0-9]{9}$",
                        "description": "Phone number in Rwanda format"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Parent's email address"
                    },
                    "child_name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Name of the child"
                    },
                    "parent_name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Name of the parent/guardian"
                    },
                    "agreed_refused": {
                        "type": "string",
                        "enum": ["Agreed", "Refused"],
                        "description": "Subscription agreement status"
                    },
                    "package": {
                        "type": "string",
                        "description": "Name of the subscription package"
                    },
                    "payment_status": {
                        "type": "string",
                        "enum": ["Pending", "Paid", "Failed"],
                        "description": "Payment status"
                    },
                    "area": {
                        "type": "string",
                        "enum": ["Gasabo", "Kicukiro", "Nyarugenge"],
                        "description": "Kigali district"
                    },
                    "location": {
                        "type": "string",
                        "description": "Sector within the district"
                    },
                    "cell": {
                        "type": "string",
                        "description": "Cell within the sector"
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Subscription updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "modified": {"type": "integer"}
                }
            }
        },
        "400": {
            "description": "Bad request - Validation error",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "404": {
            "description": "Subscription not found",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
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
@swag_from({
    "tags": ["Subscriptions"],
    "summary": "Delete subscription (Admin only)",
    "description": "Soft delete a subscription (marks as inactive). Only administrators can perform this action.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "subscription_id",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Unique subscription identifier"
        }
    ],
    "responses": {
        "200": {
            "description": "Subscription deleted successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "modified": {"type": "integer"}
                }
            }
        },
        "400": {
            "description": "Bad request",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "403": {
            "description": "Forbidden - Admin access required",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "404": {
            "description": "Subscription not found",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
@admin_required
def delete_subscription(subscription_id):
    """Delete subscription (soft delete)"""
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.delete_subscription(subscription_id)
    
    if 'error' in result:
        return jsonify({'message': result['error']}), 400
    
    return jsonify(result), 200

@subscriptions_bp.route('/bulk-update', methods=['PUT'])
@swag_from({
    "tags": ["Subscriptions"],
    "summary": "Bulk update subscriptions (Admin only)",
    "description": "Update multiple subscriptions at once. Useful for batch operations like payment status updates.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "bulk_data",
            "in": "body",
            "required": True,
            "description": "Bulk update information",
            "schema": {
                "type": "object",
                "required": ["subscription_ids", "update_data"],
                "properties": {
                    "subscription_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "description": "List of subscription IDs to update"
                    },
                    "update_data": {
                        "type": "object",
                        "description": "Fields to update for all subscriptions",
                        "properties": {
                            "payment_status": {
                                "type": "string",
                                "enum": ["Pending", "Paid", "Failed"]
                            },
                            "agreed_refused": {
                                "type": "string",
                                "enum": ["Agreed", "Refused"]
                            }
                        }
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Bulk update completed",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "subscription_id": {"type": "string"},
                                "result": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "modified": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "400": {
            "description": "Bad request - Invalid data",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "403": {
            "description": "Forbidden - Admin access required",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
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
@swag_from(subscription_search_spec)
@jwt_required()
def search_subscriptions():
    """
    Search subscriptions by various criteria
    ---
    Perform full-text search across multiple subscription fields including
    phone numbers, emails, names, and location data.
    """
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

@subscriptions_bp.route('/export', methods=['GET'])
@swag_from({
    "tags": ["Subscriptions"],
    "summary": "Export subscriptions data (Admin only)",
    "description": "Export subscriptions data in CSV format with optional filtering.",
    "security": [{"Bearer": []}],
    "parameters": [
        {
            "name": "format",
            "in": "query",
            "type": "string",
            "enum": ["csv", "json"],
            "default": "csv",
            "description": "Export format"
        },
        {
            "name": "agreed_refused",
            "in": "query",
            "type": "string",
            "enum": ["Agreed", "Refused"],
            "description": "Filter by agreement status"
        },
        {
            "name": "payment_status",
            "in": "query",
            "type": "string",
            "enum": ["Pending", "Paid", "Failed"],
            "description": "Filter by payment status"
        },
        {
            "name": "area",
            "in": "query",
            "type": "string",
            "enum": ["Gasabo", "Kicukiro", "Nyarugenge"],
            "description": "Filter by district"
        },
        {
            "name": "start_date",
            "in": "query",
            "type": "string",
            "format": "date",
            "description": "Start date for date range filter (YYYY-MM-DD)"
        },
        {
            "name": "end_date",
            "in": "query",
            "type": "string",
            "format": "date",
            "description": "End date for date range filter (YYYY-MM-DD)"
        }
    ],
    "responses": {
        "200": {
            "description": "Export file generated successfully",
            "headers": {
                "Content-Disposition": {
                    "type": "string",
                    "description": "attachment; filename=subscriptions.csv"
                }
            }
        },
        "400": {
            "description": "Bad request - Invalid parameters",
            "schema": {"$ref": "#/definitions/Error"}
        },
        "403": {
            "description": "Forbidden - Admin access required",
            "schema": {"$ref": "#/definitions/Error"}
        }
    }
})
@admin_required
def export_subscriptions():
    """Export subscriptions data"""
    from flask import make_response
    import csv
    from io import StringIO
    from datetime import datetime
    
    # Build filters
    filters = {'is_active': True}
    
    if request.args.get('agreed_refused'):
        filters['agreed_refused'] = request.args.get('agreed_refused')
    if request.args.get('payment_status'):
        filters['payment_status'] = request.args.get('payment_status')
    if request.args.get('area'):
        filters['area'] = request.args.get('area')
    
    # Date range filter
    if request.args.get('start_date') or request.args.get('end_date'):
        date_filter = {}
        if request.args.get('start_date'):
            try:
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
                date_filter['$gte'] = start_date
            except ValueError:
                return jsonify({'message': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
        
        if request.args.get('end_date'):
            try:
                end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
                date_filter['$lte'] = end_date
            except ValueError:
                return jsonify({'message': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
        
        if date_filter:
            filters['date_of_subscription'] = date_filter
    
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.get_all_subscriptions(filters, page=1, per_page=10000)  # Large limit for export
    
    export_format = request.args.get('format', 'csv').lower()
    
    if export_format == 'csv':
        # Generate CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        header = [
            'ID', 'Phone Number', 'Email', 'Child Name', 'Parent Name',
            'Agreement Status', 'Package', 'Subscription Date', 'Renewal Date',
            'Payment Status', 'District', 'Sector', 'Cell', 'Created At'
        ]
        writer.writerow(header)
        
        # Write data
        for sub in result['subscriptions']:
            writer.writerow([
                sub['_id'],
                sub['phone_number'],
                sub['email'],
                sub['child_name'],
                sub['parent_name'],
                sub['agreed_refused'],
                sub['package'],
                sub['date_of_subscription'],
                sub['renew_subscription_by'],
                sub['payment_status'],
                sub['area'],
                sub['location'],
                sub.get('cell', ''),
                sub['created_at']
            ])
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=subscriptions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return response
    
    elif export_format == 'json':
        response = make_response(jsonify(result))
        response.headers['Content-Disposition'] = f'attachment; filename=subscriptions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        return response
    
    else:
        return jsonify({'message': 'Invalid format. Use csv or json'}), 400