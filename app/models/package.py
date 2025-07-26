from datetime import datetime
from bson import ObjectId

class Package:
    def __init__(self, db):
        self.collection = db.packages
    
    def create_package(self, data):
        """Create a new package"""
        # Check if package name already exists
        existing = self.collection.find_one({"name": data['name'], "is_active": True})
        if existing:
            return {"error": "Package with this name already exists"}
        
        package = {
            "name": data['name'],
            "description": data.get('description', ''),
            "price": float(data['price']),
            "duration_days": data.get('duration_days', 30),
            "features": data.get('features', []),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.collection.insert_one(package)
        return {"success": True, "package_id": str(result.inserted_id)}
    
    def get_all_packages(self, include_inactive=False):
        """Get all packages"""
        query = {} if include_inactive else {"is_active": True}
        packages = list(self.collection.find(query).sort("name", 1))
        for package in packages:
            package['_id'] = str(package['_id'])
            if 'created_at' in package and hasattr(package['created_at'], 'isoformat'):
                package['created_at'] = package['created_at'].isoformat()
            if 'updated_at' in package and hasattr(package['updated_at'], 'isoformat'):
                package['updated_at'] = package['updated_at'].isoformat()
        return packages
    
    def get_package_by_id(self, package_id):
        """Get package by ID"""
        try:
            package = self.collection.find_one({"_id": ObjectId(package_id)})
            if package:
                package['_id'] = str(package['_id'])
                package['created_at'] = package['created_at'].isoformat()
                package['updated_at'] = package['updated_at'].isoformat()
                return package
            return None
        except:
            return None
    
    def get_package_by_name(self, name):
        """Get package by name"""
        package = self.collection.find_one({"name": name, "is_active": True})
        if package:
            package['_id'] = str(package['_id'])
            package['created_at'] = package['created_at'].isoformat()
            package['updated_at'] = package['updated_at'].isoformat()
            return package
        return None
    
    def update_package(self, package_id, data):
        """Update package"""
        try:
            update_data = data.copy()
            
            # Check if new name conflicts with existing packages
            if 'name' in update_data:
                existing = self.collection.find_one({
                    "name": update_data['name'],
                    "is_active": True,
                    "_id": {"$ne": ObjectId(package_id)}
                })
                if existing:
                    return {"error": "Package with this name already exists"}
            
            # Convert price to float if provided
            if 'price' in update_data:
                update_data['price'] = float(update_data['price'])
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(package_id)},
                {"$set": update_data}
            )
            
            return {"success": True, "modified": result.modified_count}
        except Exception as e:
            return {"error": str(e)}
    
    def delete_package(self, package_id):
        """Soft delete package"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(package_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return {"success": True, "modified": result.modified_count}
        except Exception as e:
            return {"error": str(e)}
    
    def get_package_analytics(self):
        """Get package usage analytics"""
        from app.models.subscription import Subscription
        
        # This would typically be injected or accessed differently
        # For now, we'll create a separate method to be called from analytics
        pass
    
    def validate_package_exists(self, package_name):
        """Validate that a package exists and is active"""
        package = self.get_package_by_name(package_name)
        return package is not None