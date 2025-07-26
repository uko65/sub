import bcrypt
from datetime import datetime
from bson import ObjectId

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
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id), "is_active": True})
            if user:
                user['_id'] = str(user['_id'])
                # Remove password from response
                user.pop('password', None)
                return user
            return None
        except:
            return None
    
    def update_user(self, user_id, data):
        """Update user data"""
        try:
            update_data = data.copy()
            
            # Hash password if provided
            if 'password' in update_data:
                update_data['password'] = bcrypt.hashpw(
                    update_data['password'].encode('utf-8'), 
                    bcrypt.gensalt()
                )
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return {"success": True, "modified": result.modified_count}
        except Exception as e:
            return {"error": str(e)}
    
    def delete_user(self, user_id):
        """Soft delete user"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return {"success": True, "modified": result.modified_count}
        except Exception as e:
            return {"error": str(e)}
    
    def get_all_users(self, page=1, per_page=20):
        """Get all active users with pagination"""
        skip = (page - 1) * per_page
        
        users = list(self.collection.find({"is_active": True}, {"password": 0})
                    .sort("created_at", -1)
                    .skip(skip)
                    .limit(per_page))
        
        # Convert ObjectId to string
        for user in users:
            user['_id'] = str(user['_id'])
            user['created_at'] = user['created_at'].isoformat()
        
        total = self.collection.count_documents({"is_active": True})
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }