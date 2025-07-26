from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models import Subscription
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/subscription-summary', methods=['GET'])
@jwt_required()
def subscription_analytics():
    """Get subscription analytics"""
    subscription_model = Subscription(current_app.db.db)
    analytics = subscription_model.get_analytics()
    return jsonify(analytics), 200

@reports_bp.route('/upcoming-renewals', methods=['GET'])
@jwt_required()
def upcoming_renewals():
    """Get subscriptions due for renewal in next 7 days"""
    from flask import request
    
    days_ahead = int(request.args.get('days', 7))
    subscription_model = Subscription(current_app.db.db)
    result = subscription_model.get_upcoming_renewals(days_ahead)
    
    return jsonify({
        'upcoming_renewals': result['subscriptions'],
        'total_renewals': result['total'],
        'days_ahead': days_ahead
    }), 200

@reports_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def dashboard_stats():
    """Get dashboard statistics"""
    subscription_model = Subscription(current_app.db.db)
    
    # Basic counts
    total_active = subscription_model.collection.count_documents({"is_active": True})
    total_agreed = subscription_model.collection.count_documents({
        "is_active": True, 
        "agreed_refused": "Agreed"
    })
    total_refused = subscription_model.collection.count_documents({
        "is_active": True, 
        "agreed_refused": "Refused"
    })
    
    # This month's subscriptions
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = subscription_model.collection.count_documents({
        "is_active": True,
        "date_of_subscription": {"$gte": start_of_month}
    })
    
    # Upcoming renewals (next 7 days)
    upcoming_renewals = subscription_model.collection.count_documents({
        "is_active": True,
        "renew_subscription_by": {
            "$lte": datetime.utcnow() + timedelta(days=7)
        },
        "agreed_refused": "Agreed"
    })
    
    # Payment status breakdown
    paid_count = subscription_model.collection.count_documents({
        "is_active": True,
        "payment_status": "Paid"
    })
    pending_count = subscription_model.collection.count_documents({
        "is_active": True,
        "payment_status": "Pending"
    })
    failed_count = subscription_model.collection.count_documents({
        "is_active": True,
        "payment_status": "Failed"
    })
    
    return jsonify({
        'total_subscriptions': total_active,
        'total_agreed': total_agreed,
        'total_refused': total_refused,
        'success_rate': round((total_agreed / total_active * 100), 2) if total_active > 0 else 0,
        'this_month_subscriptions': this_month,
        'upcoming_renewals': upcoming_renewals,
        'payment_breakdown': {
            'paid': paid_count,
            'pending': pending_count,
            'failed': failed_count
        }
    }), 200

@reports_bp.route('/monthly-trends', methods=['GET'])
@jwt_required()
def monthly_trends():
    """Get monthly subscription trends"""
    from flask import request
    
    months_back = int(request.args.get('months', 12))
    subscription_model = Subscription(current_app.db.db)
    
    pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {
            "_id": {
                "year": {"$year": "$date_of_subscription"},
                "month": {"$month": "$date_of_subscription"}
            },
            "total": {"$sum": 1},
            "agreed": {
                "$sum": {"$cond": [{"$eq": ["$agreed_refused", "Agreed"]}, 1, 0]}
            }
        }},
        {"$sort": {"_id.year": -1, "_id.month": -1}},
        {"$limit": months_back}
    ]
    
    trends = list(subscription_model.collection.aggregate(pipeline))
    
    # Format the response
    formatted_trends = []
    for trend in trends:
        formatted_trends.append({
            'year': trend['_id']['year'],
            'month': trend['_id']['month'],
            'month_name': datetime(trend['_id']['year'], trend['_id']['month'], 1).strftime('%B'),
            'total_subscriptions': trend['total'],
            'agreed_subscriptions': trend['agreed'],
            'success_rate': round((trend['agreed'] / trend['total'] * 100), 2) if trend['total'] > 0 else 0
        })
    
    return jsonify({
        'monthly_trends': formatted_trends,
        'months_requested': months_back
    }), 200

@reports_bp.route('/area-distribution', methods=['GET'])
@jwt_required()
def area_distribution():
    """Get subscription distribution by area"""
    subscription_model = Subscription(current_app.db.db)
    
    pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {
            "_id": "$area",
            "total": {"$sum": 1},
            "agreed": {
                "$sum": {"$cond": [{"$eq": ["$agreed_refused", "Agreed"]}, 1, 0]}
            }
        }},
        {"$sort": {"total": -1}}
    ]
    
    distribution = list(subscription_model.collection.aggregate(pipeline))
    
    # Format the response
    formatted_distribution = []
    for item in distribution:
        formatted_distribution.append({
            'area': item['_id'],
            'total_subscriptions': item['total'],
            'agreed_subscriptions': item['agreed'],
            'success_rate': round((item['agreed'] / item['total'] * 100), 2) if item['total'] > 0 else 0
        })
    
    return jsonify({
        'area_distribution': formatted_distribution
    }), 200

@reports_bp.route('/package-popularity', methods=['GET'])
@jwt_required()
def package_popularity():
    """Get package popularity statistics"""
    subscription_model = Subscription(current_app.db.db)
    
    pipeline = [
        {"$match": {"is_active": True, "agreed_refused": "Agreed"}},
        {"$group": {
            "_id": "$package",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    
    popularity = list(subscription_model.collection.aggregate(pipeline))
    
    return jsonify({
        'package_popularity': [
            {'package': item['_id'], 'subscription_count': item['count']}
            for item in popularity
        ]
    }), 200