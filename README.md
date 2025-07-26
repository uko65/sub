
# Books on Wheels Subscription System

Welcome! This project is a full-featured subscription management system for Books on Wheels, built with Flask, MongoDB, and Redis. It includes a RESTful API, Testing static HTML forms for non CLI users, and production-ready deployment scripts. Follow the steps below to get started, test, and deploy your own instance.

## Overview
A Flask-based backend with testing static HTML forms for managing and viewing book subscription data. Includes JSON export for browser-based form data.

## Features
- RESTful API for subscriptions
- Testing static HTML forms for subscription entry and listing
- JSON export from browser
- Dynamic dropdowns for location fields
- Session management with Redis
- MongoDB for data storage

## Setup
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd sub
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure environment variables as needed (see `.env.example`).
   - Copy `.env.example` to `.env` and update values for your environment.
4. Start Redis and MongoDB services.

## Running and Testing
1. (Optional) Set up an admin user for testing:
   ```bash
   python app/setup_admin.py
   ```
2. (Optional) Populate the database with fake data for testing:
   ```bash
   python setup_fake_data.py
   ```
3. Run the app for development:
   ```bash
   python run.py
   ```

## Deploying to Ubuntu Server
1. Use the provided deploy script for production setup:
   ```bash
   bash deploy.sh
   ```
2. For systemd and Nginx integration, see the Deployment section below.

## Testing Static Files
- `app/static/public_subscription.html`: Public subscription form
- `app/static/subscription_list.html`: Subscription list view
- `app/static/subscription.html`: Standalone form with JSON export


## Deployment
- Use `deploy.sh` to install dependencies and launch the backend with Gunicorn for production.

### Production with systemd and Nginx (recommended)
1. Copy `gunicorn.service` to your systemd directory:
   ```bash
   sudo cp gunicorn.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable gunicorn
   sudo systemctl start gunicorn
   sudo systemctl status gunicorn
   ```
2. Copy `nginx.conf` to your Nginx sites-available directory and enable it:
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/books-on-wheels
   sudo ln -s /etc/nginx/sites-available/books-on-wheels /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```
3. The app will now run as a background service, with Nginx serving static files and proxying API requests to Gunicorn.
- All Python, cache, and environment files are ignored via `.gitignore`.
- Use `requirements.txt` to manage dependencies.

## Author
- **Names:** Jean Felix
- **Email:** [nijeanfelix@gmail.com](mailto:nijeanfelix@gmail.com)
- **LinkedIn:** [https://linkedin.com/in/free-felix/](https://linkedin.com/in/free-felix/)
- **GitHub:** [https://github.com/FreeFelix](https://github.com/FreeFelix)

## License
MIT
