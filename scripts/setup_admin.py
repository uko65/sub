#!/usr/bin/env python3
"""
Database initialization script for the subscription management system.
Creates admin user and sample packages.
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User, Package
from app.config import config

def setup_database():
    """Initialize database with admin user and sample data"""
    print("🚀 Initializing subscription management database...")
    
    # Create Flask application
    app = create_app(config['development'])
    
    with app.app_context():
        # Initialize models
        user_model = User(app.db.db)
        package_model = Package(app.db.db)
        
        # Create admin user
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
            print("   Email: admin@example.com")
        else:
            print(f"ℹ️  Admin user: {admin_result.get('error', 'Already exists')}")
        
        # Create regular user for testing
        print("\n👤 Creating test user...")
        user_result = user_model.create_user(
            username="testuser",
            email="test@example.com",
            password="test123",
            role="user"
        )
        
        if 'success' in user_result:
            print("✅ Test user created successfully")
            print("   Username: testuser")
            print("   Password: test123")
            print("   Email: test@example.com")
        else:
            print(f"ℹ️  Test user: {user_result.get('error', 'Already exists')}")
        
        # Create sample packages
        print("\n📦 Creating sample packages...")
        sample_packages = [
            {
                "name": "Basic Plan",
                "description": "Basic subscription package for early childhood development",
                "price": 5000,  # RWF
                "duration_days": 30,
                "features": [
                    "Weekly developmental activities",
                    "Basic progress tracking",
                    "Email support"
                ]
            },
            {
                "name": "Premium Plan", 
                "description": "Premium subscription package with enhanced features",
                "price": 8000,  # RWF
                "duration_days": 30,
                "features": [
                    "Daily developmental activities",
                    "Advanced progress tracking",
                    "Video tutorials",
                    "Phone support",
                    "Milestone assessments"
                ]
            },
            {
                "name": "Family Plan",
                "description": "Family subscription package for multiple children",
                "price": 12000,  # RWF
                "duration_days": 30,
                "features": [
                    "All Premium features",
                    "Support for up to 3 children",
                    "Family dashboard",
                    "Sibling comparison reports",
                    "Priority support"
                ]
            },
            {
                "name": "Annual Basic",
                "description": "Annual basic plan with discount",
                "price": 50000,  # RWF (save 10,000)
                "duration_days": 365,
                "features": [
                    "All Basic Plan features",
                    "Annual discount",
                    "Yearly progress reports"
                ]
            }
        ]
        
        created_packages = 0
        for package_data in sample_packages:
            # Check if package already exists
            existing = package_model.get_package_by_name(package_data["name"])
            if not existing:
                result = package_model.create_package(package_data)
                if 'success' in result:
                    print(f"✅ Created package: {package_data['name']} (RWF {package_data['price']:,})")
                    created_packages += 1
                else:
                    print(f"❌ Failed to create package: {package_data['name']} - {result.get('error')}")
            else:
                print(f"ℹ️  Package already exists: {package_data['name']}")
        
        print(f"\n📊 Database initialization summary:")
        print(f"   - Admin user: {'Created' if 'success' in admin_result else 'Already exists'}")
        print(f"   - Test user: {'Created' if 'success' in user_result else 'Already exists'}")
        print(f"   - Packages created: {created_packages}")
        
        print("\n🎉 Database initialization complete!")
        print("\n📝 Next steps:")
        print("1. Start the Flask application: python run.py")
        print("2. Access the API at http://localhost:5000")
        print("3. Login with admin credentials:")
        print("   POST /api/auth/login")
        print("   {\"username\": \"admin\", \"password\": \"admin123\"}")
        print("4. Test public endpoints:")
        print("   GET /api/public/packages")
        print("   GET /api/public/districts")
        
def create_sample_subscriptions():
    """Create sample subscription data for testing"""
    print("\n📝 Creating sample subscriptions...")
    
    from app.models import Subscription
    from datetime import datetime, timedelta
    import random
    
    app = create_app(config['development'])
    
    with app.app_context():
        subscription_model = Subscription(app.db.db)
        package_model = Package(app.db.db)
        
        # Get available packages
        packages = package_model.get_all_packages()
        if not packages:
            print("❌ No packages found. Please run setup_database() first.")
            return
        
        package_names = [pkg['name'] for pkg in packages]
        
        # Sample data
        districts = ["Gasabo", "Kicukiro", "Nyarugenge"]
        sectors = {
            "Gasabo": ["Remera", "Kacyiru", "Kimihurura", "Gisozi"],
            "Kicukiro": ["Gahanga", "Gatenga", "Kagarama"],
            "Nyarugenge": ["Nyarugenge", "Muhima", "Nyamirambo"]
        }
        
        sample_subscriptions = []
        for i in range(50):  # Create 50 sample subscriptions
            district = random.choice(districts)
            sector = random.choice(sectors[district])
            
            # Random date in the last 3 months
            days_ago = random.randint(1, 90)
            sub_date = datetime.now() - timedelta(days=days_ago)
            
            sample_data = {
                "phone_number": f"+25078{random.randint(1000000, 9999999)}",
                "email": f"user{i+1}@example.com",
                "child_name": f"Child {i+1}",
                "parent_name": f"Parent {i+1}",
                "agreed_refused": random.choice(["Agreed"] * 7 + ["Refused"] * 3),  # 70% agreed
                "package": random.choice(package_names),
                "date_of_subscription": sub_date.strftime('%Y-%m-%d'),
                "area": district,
                "location": sector,
                "payment_status": random.choice(["Paid"] * 6 + ["Pending"] * 3 + ["Failed"] * 1)
            }
            
            result = subscription_model.create_subscription(sample_data)
            if 'success' in result:
                sample_subscriptions.append(result['subscription_id'])
        
        print(f"✅ Created {len(sample_subscriptions)} sample subscriptions")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup subscription management database')
    parser.add_argument('--with-samples', action='store_true', 
                       help='Create sample subscription data')
    
    args = parser.parse_args()
    
    # Always run basic setup
    setup_database()
    
    # Optionally create sample data
    if args.with_samples:
        create_sample_subscriptions()
    
    print("\n✨ Setup complete! You can now start the application with: python run.py")