from flask import Flask, jsonify, request
from flask_cors import CORS
import feedparser
import requests
import yfinance as yf
from datetime import datetime
import random
from collections import Counter
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

DONATION = "0x8242f0f25c5445F7822e80d3C9615e57586c6639"

# News sources
NEWS_SOURCES = [
    {'name': 'BBC', 'url': 'http://feeds.bbci.co.uk/news/rss.xml'},
    {'name': 'Reuters', 'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'},
    {'name': 'Guardian', 'url': 'https://www.theguardian.com/world/rss'},
    {'name': 'CNN', 'url': 'http://rss.cnn.com/rss/edition.rss'}
]

class RedditCollector:
    def get_trends(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            url = "https://www.reddit.com/r/all/hot.json?limit=25"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                posts = response.json()['data']['children']
                trends = []
                hashtags = []
                
                for post in posts[:10]:
                    title = post['data']['title']
                    trends.append({
                        'title': title[:100],
                        'subreddit': post['data']['subreddit'],
                        'score': post['data']['score'],
                        'url': f"https://reddit.com{post['data']['permalink']}"
                    })
                    
                    words = title.split()
                    for word in words[:4]:
                        clean = word.strip('.,!?').lower()
                        if len(clean) > 3 and clean[0].isalpha():
                            hashtags.append(f"#{clean}")
                
                return {
                    'posts': trends[:5],
                    'hashtags': list(dict.fromkeys(hashtags))[:8]
                }
        except:
            pass
        
        # Fallback data
        return {
            'posts': [
                {'title': 'AI Breakthrough: New Model Released', 'subreddit': 'technology', 'score': 15234, 'url': 'https://reddit.com'},
                {'title': 'Python 3.13 Features Announced', 'subreddit': 'programming', 'score': 12345, 'url': 'https://reddit.com'},
                {'title': 'Open Source Projects Going Viral', 'subreddit': 'opensource', 'score': 9876, 'url': 'https://reddit.com'},
                {'title': 'Tech Industry Updates', 'subreddit': 'tech', 'score': 8765, 'url': 'https://reddit.com'},
                {'title': 'Cybersecurity News', 'subreddit': 'cybersecurity', 'score': 7654, 'url': 'https://reddit.com'}
            ],
            'hashtags': ['#AI', '#Python', '#OpenSource', '#Tech', '#Coding']
        }

class GoogleTrendsCollector:
    def get_trends(self):
        try:
            url = "https://trends.google.com/trends/trendingsearches/daily/rss"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                trends = []
                for item in root.findall('.//item')[:5]:
                    title = item.find('title')
                    if title is not None:
                        trends.append(f"#{title.text.replace(' ', '')}")
                return trends
        except:
            pass
        return ['#AI', '#Tech', '#Python', '#Coding', '#WebDev']

class NewsCollector:
    def get_headlines(self):
        all_news = []
        for source in NEWS_SOURCES:
            try:
                feed = feedparser.parse(source['url'])
                for entry in feed.entries[:2]:
                    all_news.append({
                        'title': entry.get('title', '')[:90],
                        'source': source['name'],
                        'url': entry.get('link', '#')
                    })
            except:
                continue
        return all_news[:8]

class MarketCollector:
    def get_data(self):
        try:
            sp500 = yf.Ticker('^GSPC')
            sp_hist = sp500.history(period='2d')
            
            if not sp_hist.empty:
                sp_price = round(sp_hist['Close'].iloc[-1], 2)
                sp_open = round(sp_hist['Open'].iloc[-1], 2)
                sp_change = round(sp_price - sp_open, 2)
                sp_change_pct = round((sp_change / sp_open) * 100, 2)
            else:
                sp_price, sp_change, sp_change_pct = 4500, 25, 0.56
            
            btc = yf.Ticker('BTC-USD')
            btc_hist = btc.history(period='2d')
            
            if not btc_hist.empty:
                btc_price = round(btc_hist['Close'].iloc[-1], 2)
                btc_open = round(btc_hist['Open'].iloc[-1], 2)
                btc_change = round(btc_price - btc_open, 2)
                btc_change_pct = round((btc_change / btc_open) * 100, 2)
            else:
                btc_price, btc_change, btc_change_pct = 65000, 1200, 1.88
            
            sentiment = "Bullish" if sp_change_pct > 0.5 else "Bearish" if sp_change_pct < -0.5 else "Neutral"
            prediction = "Markets trending up" if sp_change_pct > 0 else "Markets cooling"
            
            return {
                'sp500': {
                    'price': f"${sp_price:,.0f}",
                    'change': f"{'+' if sp_change > 0 else ''}{sp_change:.0f}",
                    'change_pct': f"{'+' if sp_change_pct > 0 else ''}{sp_change_pct:.2f}%",
                    'trend': 'up' if sp_change > 0 else 'down'
                },
                'bitcoin': {
                    'price': f"${btc_price:,.0f}",
                    'change': f"{'+' if btc_change > 0 else ''}{btc_change:.0f}",
                    'change_pct': f"{'+' if btc_change_pct > 0 else ''}{btc_change_pct:.2f}%",
                    'trend': 'up' if btc_change > 0 else 'down'
                },
                'sentiment': sentiment,
                'prediction': prediction
            }
        except:
            return {
                'sp500': {'price': '$4,521', 'change': '+25', 'change_pct': '+0.56%', 'trend': 'up'},
                'bitcoin': {'price': '$65,432', 'change': '+1,200', 'change_pct': '+1.88%', 'trend': 'up'},
                'sentiment': 'Bullish',
                'prediction': 'Markets trending up'
            }

class LocationCollector:
    def get_city(self, lat, lon):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            headers = {'User-Agent': 'SSEC-SPARK/1.0'}
            response = requests.get(url, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                return address.get('city', address.get('town', address.get('village', 'Unknown')))
        except:
            pass
        return f"{float(lat):.2f}, {float(lon):.2f}"

@app.route('/api/trends')
def get_trends():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    location = "Global"
    if lat and lon:
        location = LocationCollector().get_city(lat, lon)
    
    reddit = RedditCollector().get_trends()
    google = GoogleTrendsCollector().get_trends()
    news = NewsCollector().get_headlines()
    market = MarketCollector().get_data()
    
    # Combine hashtags
    all_tags = []
    all_tags.extend(reddit['hashtags'])
    all_tags.extend(google)
    
    for item in news:
        words = item['title'].split()
        for word in words[:3]:
            clean = word.strip('.,!?').lower()
            if len(clean) > 4:
                all_tags.append(f"#{clean}")
    
    # Count and sort
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    top_tags = [tag for tag, count in sorted_tags[:10]]
    
    return jsonify({
        'success': True,
        'location': location,
        'trending': top_tags,
        'news': news,
        'reddit': reddit['posts'],
        'market': market,
        'velocity': min(len(top_tags) * 8, 80),
        'donation': DONATION
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'SSEC-SPARK running', 'donation': DONATION})

if __name__ == '__main__':
    print("=" * 50)
    print("🔥 SSEC-SPARK STARTING")
    print("=" * 50)
    print(f"📍 Donation: {DONATION}")
    print("📍 Features: Hashtags, News, Market, Map, Reddit")
    print("=" * 50)
    app.run(port=5000, debug=True)