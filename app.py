import os
import requests
from flask import Flask, request, jsonify, render_template
from functools import wraps
import ssl
import json

app = Flask(__name__)

# Environment variables for secure connection
KALI_API_URL = os.environ.get('KALI_API_URL', 'https://your-kali-ip-or-domain/api')
API_KEY = os.environ.get('API_KEY', 'your-secret-api-key')
VERIFY_SSL = os.environ.get('VERIFY_SSL', 'True').lower() == 'true'

# Custom SSL context (if using self-signed certificates on Kali)
ssl_context = ssl.create_default_context()
if not VERIFY_SSL:
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "missing bearer token"}), 401
        token = auth.split(" ", 1)[1]
        if token != API_KEY:
            return jsonify({"error": "invalid token"}), 403
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
@require_token
def get_data():
    """Retrieve data from Kali Linux API"""
    try:
        # Make request to Kali API
        headers = {
            'User-Agent': 'Flask-App/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"{KALI_API_URL}/data",
            headers=headers,
            verify=VERIFY_SSL,
            timeout=30
        )
        
        if response.status_code == 200:
            return jsonify({
                "status": "success",
                "data": response.json()
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Kali API returned status {response.status_code}",
                "response": response.text
            }), response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": f"Connection error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "flask-data-retriever",
        "version": "1.0"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, ssl_context='adhoc' if os.environ.get('FLASK_ENV') == 'development' else None)
