import os
from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Run the application in debug mode for development
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port) 