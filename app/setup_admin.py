from app.models.database import Database
from app.models.user import User
from app.models.package import Package
from app.config.config import Config
from datetime import datetime

def setup_database():
    print("🚀 Initializing database...")
    db = Database(Config.MONGO_URI)
    user_model = User(db.db)
    package_model = Package(db.db)
    print("👤 Creating admin user...")
    admin_result = user_model.create_user(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role="admin"
    )
    if 'success' in admin_result:
        print("✅ Admin user created successfully")
        print("   Username: admin")
        print("   Password: admin123")
    else:
        print(f"ℹ️  Admin user: {admin_result.get('error', 'Already exists')}")
    print("📦 Creating sample packages...")
    sample_packages = [
        {"name": "Basic Plan", "description": "Basic subscription package", "price": 29.99, "duration_days": 30, "features": ["Feature 1", "Feature 2"]},
        {"name": "Premium Plan", "description": "Premium subscription package", "price": 59.99, "duration_days": 30, "features": ["All Basic Features", "Premium Feature 1", "Premium Feature 2"]},
        {"name": "Family Plan", "description": "Family subscription package", "price": 89.99, "duration_days": 30, "features": ["All Premium Features", "Multiple Children", "Family Dashboard"]}
    ]
    for package_data in sample_packages:
        existing = package_model.collection.find_one({"name": package_data["name"]})
        if not existing:
            result = package_model.create_package(package_data)
            print(f"✅ Created package: {package_data['name']}")
        else:
            print(f"ℹ️  Package already exists: {package_data['name']}")
    print("\n🎉 Database initialization complete!")
    print("\n📊 Next steps:")
    print("1. Start the Flask application: python app/run.py")
    print("2. Test the API endpoints")
    print("3. Login with admin credentials to access all features")

if __name__ == "__main__":
    setup_database()
