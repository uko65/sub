import os
from app import create_app
from app.config import config

def main():
    """Main application entry point"""
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask application
    app = create_app(config[config_name])
    
    # Get port and debug settings
    port = int(os.environ.get('PORT', 5000))
    debug = config_name == 'development'
    
    print(f"🚀 Starting Flask application in {config_name} mode")
    print(f"📡 Server running on http://0.0.0.0:{port}")
    print(f"🔧 Debug mode: {debug}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

if __name__ == '__main__':
    main()