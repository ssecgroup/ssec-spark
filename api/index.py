# api/index.py - Vercel serverless entry point
from flask import Flask
import sys
import os

# Add the parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the app from backend
try:
    from backend.app import app
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback minimal app
    app = Flask(__name__)
    
    @app.route('/api/health')
    def health():
        return {'status': 'SSEC-SPARK running'}

# This is what Vercel needs
handler = app