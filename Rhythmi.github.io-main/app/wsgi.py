from app import app  # Replace 'app' with the actual name of your Flask app instance
from waitress import serve

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)