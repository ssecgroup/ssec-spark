from http.server import BaseHTTPRequestHandler
import json
import feedparser
import urllib.request
from urllib.parse import parse_qs

DONATION = "0x8242f0f25c5445F7822e80d3C9615e57586c6639"

NEWS_SOURCES = [
    {'name': 'BBC', 'url': 'http://feeds.bbci.co.uk/news/rss.xml'},
    {'name': 'Reuters', 'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'},
    {'name': 'Guardian', 'url': 'https://www.theguardian.com/world/rss'},
    {'name': 'CNN', 'url': 'http://rss.cnn.com/rss/edition.rss'}
]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Handle different paths
        if self.path == '/api/health':
            response = {
                'status': 'SSEC-SPARK running',
                'donation': DONATION
            }
            
        elif self.path.startswith('/api/trends'):
            # Get location from query params
            query = {}
            if '?' in self.path:
                query_string = self.path.split('?')[1]
                query = parse_qs(query_string)
            
            lat = query.get('lat', [None])[0]
            lon = query.get('lon', [None])[0]
            
            location = "Global"
            if lat and lon:
                location = f"{lat}, {lon}"
            
            # Get news
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
            
            response = {
                'success': True,
                'location': location,
                'trending': ['#AI', '#Tech', '#Python', '#Coding', '#WebDev', '#Blockchain', '#Cloud', '#DevOps'],
                'news': news[:8],
                'reddit': [
                    {'title': 'AI Breakthrough', 'subreddit': 'technology', 'score': 15234, 'url': '#'},
                    {'title': 'Python 3.13 Features', 'subreddit': 'programming', 'score': 12345, 'url': '#'},
                    {'title': 'Open Source Viral', 'subreddit': 'opensource', 'score': 9876, 'url': '#'},
                    {'title': 'Tech Updates', 'subreddit': 'tech', 'score': 8765, 'url': '#'},
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
            }
        else:
            response = {
                'status': 'SSEC-SPARK API',
                'endpoints': ['/api/health', '/api/trends'],
                'donation': DONATION
            }
        
        self.wfile.write(json.dumps(response).encode())
        return