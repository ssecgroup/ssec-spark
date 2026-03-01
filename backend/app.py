"""
SSEC-SPARK - Complete Trend Engine
All features: Hashtags, News, Market, Map, Location, Reddit, Prediction, Donation
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import feedparser
import requests
from pytrends.request import TrendReq
import yfinance as yf
from datetime import datetime
import random
from collections import Counter

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION ====================
DONATION_ADDRESS = "0x8242f0f25c5445F7822e80d3C9615e57586c6639"

# News sources (RSS - no API keys)
NEWS_SOURCES = [
    {'name': 'BBC', 'url': 'http://feeds.bbci.co.uk/news/rss.xml'},
    {'name': 'Reuters', 'url': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best'},
    {'name': 'Guardian', 'url': 'https://www.theguardian.com/world/rss'},
    {'name': 'CNN', 'url': 'http://rss.cnn.com/rss/edition.rss'}
]

# ==================== DATA COLLECTORS ====================

class RedditCollector:
    """Get trending posts and hashtags from Reddit (free)"""
    
    def get_trends(self):
        try:
            headers = {'User-Agent': 'SSEC-SPARK/2.0'}
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
                        'url': post['data']['url']
                    })
                    
                    # Extract hashtags from title
                    words = title.split()
                    for word in words[:4]:
                        clean = word.strip('.,!?').lower()
                        if len(clean) > 3 and clean[0].isalpha():
                            hashtags.append(f"#{clean}")
                
                return {
                    'posts': trends,
                    'hashtags': list(dict.fromkeys(hashtags))[:8]
                }
        except Exception as e:
            print(f"Reddit error: {e}")
        
        return {'posts': [], 'hashtags': ['#trending', '#viral', '#news']}


class GoogleTrendsCollector:
    """Get Google Trends data (completely free)"""
    
    def __init__(self):
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360)
        except:
            self.pytrends = None
    
    def get_trends(self):
        try:
            if not self.pytrends:
                return []
            
            # Get trending searches
            trending = self.pytrends.trending_searches(pn='united_states')
            if not trending.empty:
                trends = trending[0].tolist()[:5]
                return [f"#{t.replace(' ', '')}" for t in trends]
        except:
            pass
        return []


class NewsCollector:
    """Get news from RSS feeds (free)"""
    
    def get_headlines(self):
        all_news = []
        
        for source in NEWS_SOURCES:
            try:
                feed = feedparser.parse(source['url'])
                for entry in feed.entries[:2]:  # Top 2 from each source
                    all_news.append({
                        'title': entry.get('title', '')[:90],
                        'source': source['name'],
                        'url': entry.get('link', '#'),
                        'time': entry.get('published', datetime.now().isoformat())
                    })
            except:
                continue
        
        return all_news[:8]  # Return top 8


class MarketCollector:
    """Get market data and predictions"""
    
    def get_data(self):
        try:
            # S&P 500
            sp500 = yf.Ticker('^GSPC')
            sp_hist = sp500.history(period='2d')
            
            if not sp_hist.empty:
                sp_price = round(sp_hist['Close'].iloc[-1], 2)
                sp_open = round(sp_hist['Open'].iloc[-1], 2)
                sp_change = round(sp_price - sp_open, 2)
                sp_change_pct = round((sp_change / sp_open) * 100, 2)
            else:
                sp_price = 4500
                sp_change = 25
                sp_change_pct = 0.56
            
            # Bitcoin
            btc = yf.Ticker('BTC-USD')
            btc_hist = btc.history(period='2d')
            
            if not btc_hist.empty:
                btc_price = round(btc_hist['Close'].iloc[-1], 2)
                btc_open = round(btc_hist['Open'].iloc[-1], 2)
                btc_change = round(btc_price - btc_open, 2)
                btc_change_pct = round((btc_change / btc_open) * 100, 2)
            else:
                btc_price = 65000
                btc_change = 1200
                btc_change_pct = 1.88
            
            # Determine sentiment
            if sp_change_pct > 0.5:
                sentiment = "Bullish"
                prediction = "Markets trending up"
            elif sp_change_pct < -0.5:
                sentiment = "Bearish"
                prediction = "Markets cooling down"
            else:
                sentiment = "Neutral"
                prediction = "Markets stable"
            
            return {
                'sp500': {
                    'price': f"${sp_price:,.0f}",
                    'change': f"{'+' if sp_change > 0 else ''}{sp_change:.0f}",
                    'change_pct': f"{'+' if sp_change_pct > 0 else ''}{sp_change_pct}%",
                    'trend': 'up' if sp_change > 0 else 'down'
                },
                'bitcoin': {
                    'price': f"${btc_price:,.0f}",
                    'change': f"{'+' if btc_change > 0 else ''}{btc_change:.0f}",
                    'change_pct': f"{'+' if btc_change_pct > 0 else ''}{btc_change_pct}%",
                    'trend': 'up' if btc_change > 0 else 'down'
                },
                'sentiment': sentiment,
                'prediction': prediction
            }
            
        except Exception as e:
            print(f"Market error: {e}")
            return {
                'sp500': {'price': '$4,521', 'change': '+25', 'change_pct': '+0.56%', 'trend': 'up'},
                'bitcoin': {'price': '$65,432', 'change': '+1,200', 'change_pct': '+1.88%', 'trend': 'up'},
                'sentiment': 'Bullish',
                'prediction': 'Markets trending up'
            }


class LocationCollector:
    """Get location from coordinates (free)"""
    
    def get_city(self, lat, lon):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            headers = {'User-Agent': 'SSEC-SPARK/2.0'}
            response = requests.get(url, headers=headers, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                return address.get('city', address.get('town', address.get('village', 'Unknown')))
        except:
            pass
        return f"{float(lat):.2f}, {float(lon):.2f}"


def calculate_velocity(hashtags_count, prev_count=0):
    """Calculate trend velocity (0-100)"""
    if prev_count == 0:
        return min(hashtags_count * 8, 80)
    
    growth = ((hashtags_count - prev_count) / prev_count) * 100
    return min(max(int(growth), 0), 100)


# ==================== MAIN ENDPOINT ====================

@app.route('/api/trends')
def get_trends():
    """Get ALL trends data - every feature included"""
    
    # Get location
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    location = "Global"
    if lat and lon:
        location = LocationCollector().get_city(lat, lon)
    
    # Collect data from ALL sources
    reddit = RedditCollector().get_trends()
    google = GoogleTrendsCollector().get_trends()
    news = NewsCollector().get_headlines()
    market = MarketCollector().get_data()
    
    # Combine all hashtags
    all_hashtags = []
    
    # From Reddit
    all_hashtags.extend(reddit['hashtags'])
    
    # From Google
    all_hashtags.extend(google)
    
    # From news titles
    for item in news:
        words = item['title'].split()
        for word in words[:3]:
            clean = word.strip('.,!?').lower()
            if len(clean) > 4 and clean[0].isalpha():
                all_hashtags.append(f"#{clean}")
    
    # Count frequencies and get top 10
    hashtag_counts = Counter(all_hashtags)
    top_hashtags = [tag for tag, count in hashtag_counts.most_common(10)]
    
    # Calculate velocity
    velocity = calculate_velocity(len(top_hashtags))
    
    return jsonify({
        'success': True,
        'location': location,
        'trending': top_hashtags,
        'news': news,
        'reddit': reddit['posts'][:5],
        'market': market,
        'velocity': velocity,
        'donation': DONATION_ADDRESS,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/health')
def health():
    return jsonify({
        'status': 'SSEC-SPARK running',
        'features': ['hashtags', 'news', 'market', 'map', 'location', 'reddit', 'prediction', 'donation'],
        'donation': DONATION_ADDRESS
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🔥 SSEC-SPARK - COMPLETE EDITION")
    print("=" * 60)
    print("\n✅ ALL FEATURES ENABLED:")
    print("   • Hashtags (Reddit + Google + News)")
    print("   • News (BBC, Reuters, Guardian, CNN)")
    print("   • Market (S&P 500, Bitcoin)")
    print("   • Predictions (sentiment + trend)")
    print("   • Map + Location")
    print("   • Reddit Trending")
    print("   • Trend Velocity")
    print(f"\n💰 Donation: {DONATION_ADDRESS}")
    print("\n🚀 Server starting on http://localhost:5000")
    print("=" * 60)
    
    app.run(port=5000, debug=True)
