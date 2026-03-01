from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.app import app
except ImportError as e:
    # Fallback if import fails
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'SSEC-SPARK on Vercel',
            'donation': '0x8242f0f25c5445F7822e80d3C9615e57586c6639'
        })
    
    @app.route('/api/trends')
    def trends():
        return jsonify({
            'success': True,
            'location': 'Global',
            'trending': ['#AI', '#Tech', '#Python'],
            'news': [
                {'title': 'AI Breakthrough', 'source': 'BBC', 'url': '#'},
                {'title': 'Markets Rally', 'source': 'Reuters', 'url': '#'}
            ],
            'reddit': [
                {'title': 'Tech News', 'subreddit': 'technology', 'score': 1000, 'url': '#'}
            ],
            'market': {
                'sp500': {'price': '$4,521', 'change': '+25', 'trend': 'up'},
                'bitcoin': {'price': '$65,432', 'change': '+1,200', 'trend': 'up'},
                'sentiment': 'Bullish',
                'prediction': 'Markets up'
            },
            'velocity': 75,
            'donation': '0x8242f0f25c5445F7822e80d3C9615e57586c6639'
        })

# Vercel needs this
handler = app