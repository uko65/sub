from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from app.models.user import User
from app.models.subscription import Subscription
from app.models.package import Package
from app.models.database import Database
from app.models.geography import get_kigali_districts, get_sectors_by_district, get_cells_by_sector

class Database:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client.subscription_db
        self.create_indexes()
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        # Users collection indexes
        self.db.users.create_index("username", unique=True)
        self.db.users.create_index("email", unique=True)
        
        # Subscriptions collection indexes
        self.db.subscriptions.create_index("phone_number")
        self.db.subscriptions.create_index("email")
        self.db.subscriptions.create_index("date_of_subscription")
        self.db.subscriptions.create_index("renew_subscription_by")

class User:
    def __init__(self, db):
        self.collection = db.users
    
    def create_user(self, username, email, password, role='user'):
        """Create a new user with hashed password"""
        if self.collection.find_one({"username": username}):
            return {"error": "Username already exists"}
        
        if self.collection.find_one({"email": email}):
            return {"error": "Email already exists"}
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = self.collection.insert_one(user)
        return {"success": True, "user_id": str(result.inserted_id)}
    
    def authenticate(self, username, password):
        """Authenticate user with username and password"""
        user = self.collection.find_one({"username": username, "is_active": True})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return {
                "user_id": str(user['_id']),
                "username": user['username'],
                "email": user['email'],
                "role": user['role']
            }
        return None

class Subscription:
    def __init__(self, db):
        self.collection = db.subscriptions
    
    def create_subscription(self, data):
        """Create a new subscription record"""
        # Validate area (district)
        if data['area'] not in get_kigali_districts():
            return {"error": f"Invalid area. Must be one of: {get_kigali_districts()}"}
        
        # Validate location (sector)
        valid_sectors = get_sectors_by_district(data['area'])
        if data['location'] not in valid_sectors:
            return {"error": f"Invalid location for {data['area']}. Must be one of: {valid_sectors}"}
        
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
            # Handle date updates
            update_data = data.copy()
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
        
        return {
            "total_subscriptions": self.collection.count_documents({"is_active": True}),
            "agreement_breakdown": agreement_stats,
            "payment_status": payment_stats,
            "popular_packages": package_stats,
            "area_distribution": area_stats,
            "upcoming_renewals": self.collection.count_documents({
                "is_active": True,
                "renew_subscription_by": {
                    "$lte": datetime.utcnow() + timedelta(days=7)
                }
            })
        }

class Package:
    def __init__(self, db):
        self.collection = db.packages
    
    def create_package(self, data):
        """Create a new package"""
        package = {
            "name": data['name'],
            "description": data.get('description', ''),
            "price": data['price'],
            "duration_days": data.get('duration_days', 30),
            "features": data.get('features', []),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        result = self.collection.insert_one(package)
        return {"success": True, "package_id": str(result.inserted_id)}
    
    def get_all_packages(self):
        """Get all active packages"""
        packages = list(self.collection.find({"is_active": True}))
        for package in packages:
            package['_id'] = str(package['_id'])
            package['created_at'] = package['created_at'].isoformat()
        
        return packages