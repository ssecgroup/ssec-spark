# api/index.py - Vercel serverless entry point
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add the parent directory to path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the actual app from backend
try:
    from backend.app import app as flask_app
except ImportError:
    # If import fails, create a minimal app
    flask_app = Flask(__name__)
    CORS(flask_app)
    
    @flask_app.route('/api/trends')
    def get_trends():
        return jsonify({
            'success': True,
            'location': 'Global',
            'trending': ['#AI', '#Tech', '#Python', '#Coding', '#WebDev'],
            'news': [
                {'title': 'AI Breakthrough', 'source': 'BBC', 'url': '#'},
                {'title': 'Markets Rally', 'source': 'Reuters', 'url': '#'}
            ],
            'market': {
                'sp500': {'price': '$4,521', 'change': '+25', 'trend': 'up'},
                'bitcoin': {'price': '$65,432', 'change': '+1,200', 'trend': 'up'},
                'sentiment': 'Bullish',
                'prediction': 'Markets up'
            },
            'reddit': [
                {'title': 'New AI Model', 'subreddit': 'technology', 'score': 15000, 'url': '#'}
            ],
            'velocity': 78,
            'donation': '0x8242f0f25c5445F7822e80d3C9615e57586c6639'
        })
    
    @flask_app.route('/api/health')
    def health():
        return jsonify({'status': 'SSEC-SPARK running'})

# This is what Vercel needs
app = flask_app

# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)