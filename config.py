import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'JHbrx0GvNulhV6uKP+UWXE/FNZbHASAQgy1E1Cs60SE='
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/subscription_db'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'JHbrx0GvNulhV6uKP+UWXE/FNZbHASAQgy1E1Cs60SE='
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # Remove unexpected indent. If this return is needed, place it inside a function.