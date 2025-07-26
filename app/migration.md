# Migration Guide: Refactoring to New Structure

This guide will help you migrate your existing Flask project to the new organized structure.

## 📋 Pre-Migration Checklist

- [ ] Backup your current project
- [ ] Ensure all dependencies are documented
- [ ] Test current functionality works
- [ ] Stop any running instances

## 🗂️ Step 1: Create New Directory Structure

Create the following directory structure:

```bash
mkdir -p app/{models,auth,api,utils,static}
mkdir -p scripts tests
touch app/__init__.py
touch app/models/__init__.py
touch app/auth/__init__.py
touch app/api/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
```

## 📁 Step 2: Move Files to New Locations

### Move and Rename Files

1. **Configuration**
   ```bash
   mv config.py app/config.py
   ```

2. **Models**
   ```bash
   # Split models.py into separate files
   # Copy relevant parts to:
   # - app/models/database.py
   # - app/models/user.py  
   # - app/models/subscription.py
   # - app/models/package.py
   # - app/models/geography.py
   ```

3. **Authentication**
   ```bash
   mv auth.py app/auth/decorators.py
   ```

4. **Scripts**
   ```bash
   mv setup_admin.py scripts/
   mv setup_fake_data.py scripts/
   ```

5. **Application Entry**
   ```bash
   # Keep run.py in root, but update its content
   ```

## 🔧 Step 3: Update Import Statements

### 1. Update `app/__init__.py`
Create the application factory pattern (see artifacts above).

### 2. Update `run.py`
Update to use the new application factory:

```python
from app import create_app
from app.config import config
import os

config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[config_name])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 3. Update Model Imports
In each model file, update imports:

```python
# OLD
from models import Database, User

# NEW  
from app.models import Database, User
# OR within models package
from .database import Database
from .user import User
```

### 4. Update API Route Imports
In API files, update imports:

```python
# OLD
from models import User, Subscription
from auth import admin_required

# NEW
from app.models import User, Subscription  
from app.auth import admin_required
```

## 🔄 Step 4: Split Large Files

### Split `app.py` into Blueprints

1. **Extract Auth Routes** → `app/api/auth.py`
2. **Extract Subscription Routes** → `app/api/subscriptions.py`
3. **Extract Package Routes** → `app/api/packages.py`
4. **Extract Geographic Routes** → `app/api/geography.py`
5. **Extract Report Routes** → `app/api/reports.py`
6. **Extract Public Routes** → `app/api/public.py`

### Split `models.py`

1. **Database Class** → `app/models/database.py`
2. **User Class** → `app/models/user.py`
3. **Subscription Class** → `app/models/subscription.py`
4. **Package Class** → `app/models/package.py`
5. **Geographic Functions** → `app/models/geography.py`

## ⚙️ Step 5: Update Configuration

### 1. Create Environment Template
```bash
cp .env .env.example
# Remove sensitive values from .env.example
```

### 2. Update Configuration Classes
Enhance `app/config.py` with multiple environment configs.

### 3. Update Flask App Creation
Implement application factory pattern in `app/__init__.py`.

## 🧪 Step 6: Test the Migration

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export FLASK_ENV=development
```

### 3. Initialize Database
```bash
python scripts/setup_admin.py
```

### 4. Start Application
```bash
python run.py
```

### 5. Test Endpoints
```bash
# Test health check
curl http://localhost:5000/api/health

# Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test public endpoints
curl http://localhost:5000/api/public/packages
```

## 🔍 Step 7: Verify Functionality

### Checklist of Features to Test

- [ ] User authentication (login/logout)
- [ ] User registration (admin only)
- [ ] JWT token refresh
- [ ] Subscription creation
- [ ] Subscription retrieval with filters
- [ ] Subscription updates
- [ ] Package management
- [ ] Geographic data endpoints
- [ ] Analytics and reports
- [ ] Public endpoints
- [ ] Error handling

## 🚨 Common Issues and Solutions

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'models'`

**Solution**: Update imports to use the new structure:
```python
# Change this
from models import User

# To this  
from app.models import User
```

### Circular Import Errors

**Problem**: Circular imports between modules

**Solution**: 
1. Use late imports inside functions
2. Restructure code to avoid circular dependencies
3. Use `current_app` context for accessing shared resources

### Blueprint Registration Errors

**Problem**: Blueprint routes not found

**Solution**: Ensure all blueprints are registered in `app/__init__.py`:
```python
from app.api.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')
```

### Database Connection Issues

**Problem**: Database not connecting after migration

**Solution**: 
1. Check if database initialization moved to application factory
2. Verify MongoDB URI in environment variables
3. Ensure database models use `current_app.db`

## 📋 Post-Migration Tasks

1. **Update Documentation**
   - Update README.md
   - Update API documentation
   - Update deployment guides

2. **Update CI/CD**
   - Update build scripts
   - Update test commands
   - Update deployment scripts

3. **Review and Optimize**
   - Review code for improvements
   - Add missing error handling
   - Optimize database queries
   - Add logging where needed

4. **Security Review**
   - Review authentication flow
   - Check for exposed secrets
   - Validate input sanitization
   - Test authorization rules

## ✅ Migration Completion Checklist

- [ ] All files moved to new structure
- [ ] All imports updated
- [ ] Application starts without errors
- [ ] All endpoints functional
- [ ] Database operations working
- [ ] Authentication working
- [ ] Tests passing (if any)
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Git repository updated

## 🆘 Rollback Plan

If issues arise during migration:

1. **Stop the new application**
2. **Restore from backup**
3. **Identify the specific issue**
4. **Fix incrementally**
5. **Test each fix**

Keep the old structure available until you're confident the new structure works perfectly.

---

**Note**: This migration should be done incrementally. Test each step before proceeding to the next one.