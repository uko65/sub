
Subscription Management System

A Flask-based REST API for managing subscription services with user authentication, geographic data management, and comprehensive reporting features.

🏗️ Project Structure

subscription_management/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   ├── database.py          # Database connection
│   │   ├── user.py              # User model
│   │   ├── subscription.py      # Subscription model
│   │   ├── package.py           # Package model
│   │   └── geography.py         # Geographic data
│   ├── auth/                    # Authentication
│   │   ├── __init__.py
│   │   └── decorators.py        # Auth decorators
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── subscriptions.py     # Subscription routes
│   │   ├── packages.py          # Package routes
│   │   ├── geography.py         # Geographic routes
│   │   ├── reports.py           # Analytics routes
│   │   └── public.py            # Public routes
│   └── static/                  # Static files
├── scripts/
│   ├── setup_admin.py           # Database setup script
│   └── setup_fake_data.py       # Test data generator
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── run.py                       # Application entry point
└── README.md                    # This file