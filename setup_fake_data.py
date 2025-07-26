
"""
Script to populate the database with fake users, packages, and subscriptions for development/testing.
Run: python setup_fake_data.py
"""
import random
from datetime import datetime, timedelta
from app.models.database import Database
from app.models.user import User
from app.models.package import Package
from app.models.subscription import Subscription

MONGO_URI = 'mongodb://localhost:27017/'

def seed_users(db):
    user_model = User(db)
    users = [
        {"username": "admin", "email": "admin@example.com", "password": "adminpass", "role": "admin"},
        {"username": "user1", "email": "user1@example.com", "password": "userpass1", "role": "user"},
        {"username": "user2", "email": "user2@example.com", "password": "userpass2", "role": "user"},
    ]
    for u in users:
        res = user_model.create_user(u['username'], u['email'], u['password'], u['role'])
        print(f"User: {u['username']} => {res}")

def seed_packages(db):
    package_model = Package(db)
    packages = [
        {"name": "Basic", "description": "Basic package", "price": 10.0, "duration_days": 30},
        {"name": "Standard", "description": "Standard package", "price": 20.0, "duration_days": 30},
        {"name": "Premium", "description": "Premium package", "price": 30.0, "duration_days": 30},
    ]
    for p in packages:
        res = package_model.create_package(p)
        print(f"Package: {p['name']} => {res}")

def seed_subscriptions(db):
    subscription_model = Subscription(db)
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    parents = ["ParentA", "ParentB", "ParentC", "ParentD"]
    packages = ["Basic", "Standard", "Premium"]
    districts = ["Gasabo", "Kicukiro", "Nyarugenge"]
    sectors = ["Remera", "Kimironko", "Kacyiru", "Gikondo", "Kagarama", "Nyamirambo"]
    cells = ["Cell1", "Cell2", "Cell3", "Cell4"]
    for i in range(20):
        child = random.choice(names)
        parent = random.choice(parents)
        package = random.choice(packages)
        area = random.choice(districts)
        location = random.choice(sectors)
        cell = random.choice(cells)
        agreed = random.choice(["Agreed", "Refused"])
        payment_status = random.choice(["Pending", "Paid", "Failed"])
        date_of_subscription = (datetime.utcnow() - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d')
        data = {
            "phone_number": f"+2507{random.randint(10000000, 99999999)}",
            "email": f"{child.lower()}{i}@example.com",
            "child_name": child,
            "parent_name": parent,
            "agreed_refused": agreed,
            "package": package,
            "date_of_subscription": date_of_subscription,
            "area": area,
            "location": location,
            "cell": cell,
            "payment_status": payment_status
        }
        res = subscription_model.create_subscription(data)
        print(f"Subscription: {child} => {res}")

if __name__ == "__main__":
    db = Database(MONGO_URI).db
    print("Seeding users...")
    seed_users(db)
    print("Seeding packages...")
    seed_packages(db)
    print("Seeding subscriptions...")
    seed_subscriptions(db)
    print("Done.")
