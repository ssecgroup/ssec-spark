# api/index.py - Simplified for Vercel
from flask import Flask, jsonify, request
from flask_cors import CORS
import feedparser
import requests
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DONATION = "0x8242f0f25c5445F7822e80d3C9615e57586c6639"

NEWS_SOURCES = [
    {'name': 'BBC', 'url': 'http://feeds.bbci.co.uk/news/rss.xml'},
    {'name': 'Reuters', 'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'},
    {'name': 'Guardian', 'url': 'https://www.theguardian.com/world/rss'},
    {'name': 'CNN', 'url': 'http://rss.cnn.com/rss/edition.rss'}
]

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'SSEC-SPARK running on Vercel',
        'donation': DONATION
    })

@app.route('/api/trends')
def get_trends():
    # Get news (works in serverless)
    news = []
    for source in NEWS_SOURCES:
        try:
            feed = feedparser.parse(source['url'])
            for entry in feed.entries[:2]:
                news.append({
                    'title': entry.get('title', '')[:90],
                    'source': source['name'],
                    'url': entry.get('link', '#')
                })
        except:
            continue
    
    # Mock data for everything else (Vercel-friendly)
    return jsonify({
        'success': True,
        'location': request.args.get('lat', 'Global'),
        'trending': ['#AI', '#Tech', '#Python', '#Coding', '#WebDev', '#Blockchain', '#Cloud', '#DevOps'],
        'news': news[:8],
        'reddit': [
            {'title': 'AI Breakthrough: New Model Released', 'subreddit': 'technology', 'score': 15234, 'url': '#'},
            {'title': 'Python 3.13 Features Announced', 'subreddit': 'programming', 'score': 12345, 'url': '#'},
            {'title': 'Open Source Projects Going Viral', 'subreddit': 'opensource', 'score': 9876, 'url': '#'},
            {'title': 'Tech Industry Updates', 'subreddit': 'tech', 'score': 8765, 'url': '#'},
            {'title': 'Cybersecurity News', 'subreddit': 'cybersecurity', 'score': 7654, 'url': '#'}
        ],
        'market': {
            'sp500': {'price': '$4,521', 'change': '+25', 'change_pct': '+0.56%', 'trend': 'up'},
            'bitcoin': {'price': '$65,432', 'change': '+1,200', 'change_pct': '+1.88%', 'trend': 'up'},
            'sentiment': 'Bullish',
            'prediction': 'Markets trending up'
        },
        'velocity': 78,
        'donation': DONATION
    })

# This is what Vercel needs
handler = app