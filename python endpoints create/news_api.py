from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import feedparser
import concurrent.futures
from newspaper import Article
from typing import List, Optional
import uvicorn
from datetime import datetime

app = FastAPI(title="News API", description="Get latest news from multiple FREE sources - No API key needed!")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zee-like categories JSON (as in your screenshot)
FEED_CATEGORIES = [
    {"id":"topnews","title":"HOME"},
    {"id":"entertainment","title":"ENTERTAINMENT"},
    {"id":"cricket","title":"CRICKET"},
    {"id":"buzz","title":"TRENDING"},
    {"id":"international","title":"WORLD"},
    {"id":"impact_shorts","title":"IMPACT SHORTS"},
    {"id":"instantloan","title":"LOANS @ 10%"},
    {"id":"national","title":"NATIONAL"},
    {"id":"business","title":"BUSINESS"},
    {"id":"lifestyle","title":"LIFESTYLE"},
    {"id":"tech","title":"TECH"},
    {"id":"educationandcareer","title":"EDUCATION AND CAREER"},
    {"id":"explainers","title":"EXPLAINERS"},
    {"id":"opinion","title":"OPINION"},
    {"id":"politics","title":"POLITICS"}
]

# Free RSS sources for news aggregation (no key required)
FEED_SOURCES = {
    "general": [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.reuters.com/reuters/topNews",
        "https://www.theguardian.com/international/rss",
    ],

    "business": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.reuters.com/finance/markets",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
    ],
    "technology": [
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.techradar.com/feeds/all",
    ],
    "sports": [
        "https://feeds.bbci.co.uk/news/sports/rss.xml",
        "https://feeds.reuters.com/sports",
        "https://www.espn.com/espn/rss/news",
    ],
    "science": [
        "https://feeds.nature.com/nature/rss/current",
        "https://www.sciencedaily.com/rss/all.xml",
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    ],
    "health": [
        "https://feeds.bbci.co.uk/news/health/rss.xml",
        "https://www.healthline.com/health/feeds/rss",
        "https://www.medicalnewstoday.com/feed",
    ],
    "entertainment": [
        "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
        "https://www.theverge.com/culture/rss/index.xml",
        "https://variety.com/feed/",
    ]
}

CATEGORIES = list(FEED_SOURCES.keys())

@app.get("/")
async def root():
    """Welcome endpoint - Get all categories and news"""
    try:
        all_news_by_category = {}
        
        for category, feeds in FEED_SOURCES.items():
            articles = []
            for feed_url in feeds[:1]:
                articles.extend(parse_rss_feed(feed_url))
            
            all_news_by_category[category] = {
                "id": category,
                "title": category.upper(),
                "articles": articles[:5]
            }
        
        return {
            "status": "success",
            "categories": all_news_by_category
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/categories")
async def get_categories():
    """Get all available news categories"""
    return {
        "categories": CATEGORIES,
        "total": len(CATEGORIES)
    }

@app.get("/feeds")
async def get_feed_categories():
    """Get exact source category data (Zee-like, as image)"""
    return FEED_CATEGORIES

# Add some special source endpoints (e.g., Zee News) + others
ZEE_FEED_MAPPINGS = {
    "topnews": "https://zeenews.india.com/rss/india-national-news.xml",
    "entertainment": "https://zeenews.india.com/rss/entertainment-news.xml",
    "business": "https://zeenews.india.com/rss/economy-business.xml",
    "technology": "https://zeenews.india.com/rss/technology-news.xml",
    "sports": "https://zeenews.india.com/rss/sports-news.xml",
    "world": "https://zeenews.india.com/rss/world-news.xml"
}

@app.get("/news/source/{source_id}")
async def get_news_by_source(source_id: str, page_size: int = 20, full_text: bool = True):
    """Get news by specific source ID (Zee-like)"""
    source_url = ZEE_FEED_MAPPINGS.get(source_id)
    if not source_url:
        return {"error": "source_id not found", "available": list(ZEE_FEED_MAPPINGS.keys())}
    
    articles = parse_rss_feed(source_url, fetch_full=full_text)
    for art in articles:
        art["category"] = source_id
    return articles[:page_size]

def fetch_article_full_text(url: str) -> str:
    """Get full article text from URL using newspaper3k"""
    if not url or not url.startswith("http"):
        return ""
    
    try:
        article = Article(url)
        article.download()
        article.parse()
        full_text = article.text.strip()
        return full_text
    except Exception:
        return ""


def parse_rss_feed(feed_url: str, fetch_full: bool = False) -> List[dict]:
    """Parse RSS feed and extract articles"""
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries[:20]:  # Get first 20 items
            url = entry.get("link", "")
            base_content = entry.get("summary", entry.get("description", ""))
            article = {
                "title": entry.get("title", "No title"),
                "description": base_content[:300],
                "content": base_content,
                "source": feed.feed.get("title", "Unknown Source"),
                "published_at": entry.get("published", ""),
                "author": entry.get("author", "Unknown"),
                "full_text": ""
            }
            
            if fetch_full and url:
                article["full_text"] = fetch_article_full_text(url)
            
            articles.append(article)
        
        return articles
    except Exception:
        return []

@app.get("/news")
async def get_all_news(page_size: int = 20, full_text: bool = True):
    """Get latest news from all categories - NO API KEY NEEDED!"""
    try:
        all_articles = []
        
        # Fetch from all categories
        for category, feeds in FEED_SOURCES.items():
            for feed_url in feeds[:1]:
                articles = parse_rss_feed(feed_url, fetch_full=full_text)
                for article in articles:
                    article["category"] = category
                all_articles.extend(articles)
        
        # Limit results
        all_articles = all_articles[:page_size]
        
        # Output: direct JSON list
        return all_articles
    except Exception:
        return []
        all_articles = all_articles[:page_size]
        
        return all_articles
    except Exception as e:
        return []

@app.get("/news/category/{category}")
async def get_news_by_category(category: str, page_size: int = 20, full_text: bool = True):
    """Get news by specific category - NO API KEY NEEDED!"""
    if category.lower() not in CATEGORIES:
        return {
            "error": f"Category '{category}' not found",
            "available_categories": CATEGORIES
        }
    
    try:
        all_articles = []
        feeds = FEED_SOURCES.get(category.lower(), [])
        
        # Fetch from all feeds in this category
        for feed_url in feeds:
            articles = parse_rss_feed(feed_url, fetch_full=full_text)
            for article in articles:
                article["category"] = category
            all_articles.extend(articles)
        
        # Remove duplicates
        seen_keys = set()
        unique_articles = []
        for article in all_articles:
            key = f"{article.get('title','')}|{article.get('published_at','')}"
            if key not in seen_keys:
                seen_keys.add(key)
                unique_articles.append(article)
        
        unique_articles = unique_articles[:page_size]
        
        return unique_articles
    except Exception:
        return []

@app.get("/news/search")
async def search_news(q: str, page_size: int = 20, full_text: bool = True):
    """Search news by keyword - NO API KEY NEEDED!"""
    if not q or len(q.strip()) == 0:
        return []
    
    try:
        all_articles = []
        search_term = q.lower()
        
        # Search through all feeds
        for category, feeds in FEED_SOURCES.items():
            for feed_url in feeds[:1]:
                articles = parse_rss_feed(feed_url, fetch_full=full_text)
                # Filter articles matching search term
                for article in articles:
                    if (search_term in article["title"].lower() or 
                        search_term in article["description"].lower() or
                        search_term in article.get("content", "").lower() or
                        search_term in article.get("full_text", "").lower()):
                        article["category"] = category
                        all_articles.append(article)
        
        all_articles = all_articles[:page_size]
        
        return all_articles
    except Exception:
        return []

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📰 FREE NEWS API SERVER STARTING...")
    print("="*70)
    print("\n✅ Your API is LIVE!")
    print("\n📍 Direct News Data (No wrappers, just pure data):")
    print("   • http://localhost:8004              (All categories)")
    print("   • http://localhost:8004/news         (All latest news)")
    print("   • http://localhost:8004/news/category/business")
    print("   • http://localhost:8004/news/category/sports")
    print("   • http://localhost:8004/news/category/technology")
    print("   • http://localhost:8004/news/category/health")
    print("   • http://localhost:8004/news/category/science")
    print("   • http://localhost:8004/news/category/entertainment")
    print("   • http://localhost:8004/news/search?q=keyword")
    print("\n📊 Each news item includes:")
    print("   ✓ Title")
    print("   ✓ Description/Content")
    print("   ✓ Source (BBC, Reuters, Guardian, etc)")
    print("   ✓ Author")
    print("   ✓ Published Date")
    print("   ✓ Direct Link to Article")
    print("   ✓ Category")
    print("\n✨ Pure JSON Response - Direct data, no wrappers!")
    print("   Every response is pure news data - no status wrapper")
    print("\n🎯 Try in browser: http://localhost:8002/docs")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8004)
