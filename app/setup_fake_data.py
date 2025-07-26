from app.models.database import Database
from app.models.user import User
from app.models.subscription import Subscription
from app.models.package import Package
from datetime import datetime

DB_URI = 'mongodb://localhost:27017/subscription_db'
db = Database(DB_URI)
user_model = User(db.db)
subscription_model = Subscription(db.db)
package_model = Package(db.db)

def add_packages():
    packages = [
        {"name": "Basic", "description": "Basic package", "price": 50, "duration_days": 30, "features": ["FeatureA", "FeatureB"]},
        {"name": "Premium", "description": "Premium package", "price": 100, "duration_days": 60, "features": ["FeatureA", "FeatureB", "FeatureC"]}
    ]
    for pkg in packages:
        package_model.create_package(pkg)

def add_users():
    users = [
        {"username": "admin1", "email": "admin1@example.com", "password": "adminpass", "role": "admin"},
        {"username": "user1", "email": "user1@example.com", "password": "userpass", "role": "user"}
    ]
    for u in users:
        user_model.create_user(u["username"], u["email"], u["password"], u["role"])

def add_subscriptions():
    subs = [
        {"phone_number": "0781111111", "email": "parent1@example.com", "child_name": "Child One", "parent_name": "Parent One", "agreed_refused": "Agreed", "package": "Basic", "date_of_subscription": datetime.utcnow().strftime('%Y-%m-%d'), "area": "Nyarugenge", "location": "Gitega"},
        {"phone_number": "0782222222", "email": "parent2@example.com", "child_name": "Child Two", "parent_name": "Parent Two", "agreed_refused": "Refused", "package": "Premium", "date_of_subscription": datetime.utcnow().strftime('%Y-%m-%d'), "area": "Gasabo", "location": "Gisozi"}
    ]
    for s in subs:
        subscription_model.create_subscription(s)

if __name__ == "__main__":
    add_packages()
    add_users()
    add_subscriptions()
    print("Fake data inserted.")
