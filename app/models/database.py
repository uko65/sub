from pymongo import MongoClient

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
        
        # Packages collection indexes
        self.db.packages.create_index("name")
        self.db.packages.create_index("is_active")
    
    def get_collection(self, name):
        """Get a collection by name"""
        return self.db[name]
    
    def close_connection(self):
        """Close database connection"""
        self.client.close()