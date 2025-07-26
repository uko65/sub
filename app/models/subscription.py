from datetime import datetime, timedelta
from bson import ObjectId
from .geography import get_kigali_districts, get_sectors_by_district, validate_location

class Subscription:
    def __init__(self, db):
        self.collection = db.subscriptions
    
    def create_subscription(self, data):
        """Create a new subscription record"""
        # Validate location
        is_valid, message = validate_location(data['area'], data['location'], data.get('cell'))
        if not is_valid:
            return {"error": message}
        
        # Calculate renewal date (30 days from subscription date)
        subscription_date = datetime.strptime(data['date_of_subscription'], '%Y-%m-%d')
        renewal_date = subscription_date + timedelta(days=30)
        
        subscription = {
            "phone_number": data['phone_number'],
            "email": data['email'],
            "child_name": data['child_name'],
            "parent_name": data['parent_name'],
            "agreed_refused": data['agreed_refused'],  # "Agreed" or "Refused"
            "package": data['package'],
            "date_of_subscription": subscription_date,
            "renew_subscription_by": renewal_date,
            "payment_status": data.get('payment_status', 'Pending'),  # Pending, Paid, Failed
            "area": data['area'],  # Kigali district
            "location": data['location'],  # Sector within district
            "cell": data.get('cell', ''),  # Optional: specific cell within sector
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = self.collection.insert_one(subscription)
        return {"success": True, "subscription_id": str(result.inserted_id)}
    
    def get_all_subscriptions(self, filters=None, page=1, per_page=20):
        """Get all subscriptions with optional filters"""
        query = filters or {}
        skip = (page - 1) * per_page
        
        subscriptions = list(self.collection.find(query)
                           .sort("created_at", -1)
                           .skip(skip)
                           .limit(per_page))
        
        # Convert ObjectId to string and format dates
        for sub in subscriptions:
            sub['_id'] = str(sub['_id'])
            sub['date_of_subscription'] = sub['date_of_subscription'].strftime('%Y-%m-%d')
            sub['renew_subscription_by'] = sub['renew_subscription_by'].strftime('%Y-%m-%d')
            sub['created_at'] = sub['created_at'].isoformat()
            sub['updated_at'] = sub['updated_at'].isoformat()
        
        total = self.collection.count_documents(query)
        
        return {
            "subscriptions": subscriptions,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    def get_subscription_by_id(self, subscription_id):
        """Get subscription by ID"""
        try:
            subscription = self.collection.find_one({"_id": ObjectId(subscription_id)})
            if subscription:
                subscription['_id'] = str(subscription['_id'])
                subscription['date_of_subscription'] = subscription['date_of_subscription'].strftime('%Y-%m-%d')
                subscription['renew_subscription_by'] = subscription['renew_subscription_by'].strftime('%Y-%m-%d')
                subscription['created_at'] = subscription['created_at'].isoformat()
                subscription['updated_at'] = subscription['updated_at'].isoformat()
                return subscription
            return None
        except:
            return None
    
    def update_subscription(self, subscription_id, data):
        """Update subscription record"""
        try:
            update_data = data.copy()
            
            # Validate location if area or location is being updated
            if 'area' in update_data or 'location' in update_data:
                # Get current subscription to merge with update data
                current_sub = self.get_subscription_by_id(subscription_id)
                if not current_sub:
                    return {"error": "Subscription not found"}
                
                area = update_data.get('area', current_sub['area'])
                location = update_data.get('location', current_sub['location'])
                cell = update_data.get('cell', current_sub.get('cell'))
                
                is_valid, message = validate_location(area, location, cell)
                if not is_valid:
                    return {"error": message}
            
            # Handle date updates
            if 'date_of_subscription' in update_data:
                update_data['date_of_subscription'] = datetime.strptime(
                    update_data['date_of_subscription'], '%Y-%m-%d'
                )
                # Recalculate renewal date
                update_data['renew_subscription_by'] = update_data['date_of_subscription'] + timedelta(days=30)
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(subscription_id)},
                {"$set": update_data}
            )
            
            return {"success": True, "modified": result.modified_count}
        except Exception as e:
            return {"error": str(e)}
    
    def delete_subscription(self, subscription_id):
        """Soft delete subscription"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(subscription_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return {"success": True, "modified": result.modified_count}
        except Exception as e:
            return {"error": str(e)}
    
    def get_analytics(self):
        """Get subscription analytics"""
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": "$agreed_refused",
                "count": {"$sum": 1}
            }}
        ]
        
        agreement_stats = list(self.collection.aggregate(pipeline))
        
        # Payment status analytics
        payment_pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": "$payment_status",
                "count": {"$sum": 1}
            }}
        ]
        
        payment_stats = list(self.collection.aggregate(payment_pipeline))
        
        # Package popularity
        package_pipeline = [
            {"$match": {"is_active": True, "agreed_refused": "Agreed"}},
            {"$group": {
                "_id": "$package",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        package_stats = list(self.collection.aggregate(package_pipeline))
        
        # Area distribution
        area_pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": "$area",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        area_stats = list(self.collection.aggregate(area_pipeline))
        
        # Monthly subscription trends
        monthly_pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": {
                    "year": {"$year": "$date_of_subscription"},
                    "month": {"$month": "$date_of_subscription"}
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": -1, "_id.month": -1}},
            {"$limit": 12}
        ]
        
        monthly_stats = list(self.collection.aggregate(monthly_pipeline))
        
        return {
            "total_subscriptions": self.collection.count_documents({"is_active": True}),
            "total_agreed": self.collection.count_documents({"is_active": True, "agreed_refused": "Agreed"}),
            "total_refused": self.collection.count_documents({"is_active": True, "agreed_refused": "Refused"}),
            "agreement_breakdown": agreement_stats,
            "payment_status": payment_stats,
            "popular_packages": package_stats,
            "area_distribution": area_stats,
            "monthly_trends": monthly_stats,
            "upcoming_renewals": self.collection.count_documents({
                "is_active": True,
                "renew_subscription_by": {
                    "$lte": datetime.utcnow() + timedelta(days=7)
                }
            })
        }
    
    def get_upcoming_renewals(self, days_ahead=7):
        """Get subscriptions due for renewal"""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        filters = {
            'is_active': True,
            'renew_subscription_by': {'$lte': end_date},
            'agreed_refused': 'Agreed'
        }
        
        return self.get_all_subscriptions(filters)