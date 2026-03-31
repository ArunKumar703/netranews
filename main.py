from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import news, article

app = FastAPI(
    title="Global News API",
    description="A multi-language (Telugu, Hindi, English, etc.) production-level News API.",
    version="1.1.0"
)

# CORS Middleware (Allow all for production-ready API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(news.router, tags=["News"])
app.include_router(article.router, tags=["Article Content"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Multi-Language News API!",
        "docs": "/docs",
        "supported_languages": "en, hi, te, ta, kn, ml, mr, bn, gu, pa",
        "example_endpoints": {
            "categories": "/categories?lang=te",
            "category_news": "/news/topnews?lang=te",
            "article_content": "/article-content?url={url}&lang=te"
        }
    }

@app.get("/test-fetch")
async def test_fetch():
    import feedparser
    import requests
    target = "https://zeenews.india.com/rss/india-national-news.xml"
    try:
        r = requests.get(target, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        feed = feedparser.parse(target)
        return {
            "status": r.status_code,
            "feed_title": feed.feed.get('title'),
            "entries_count": len(feed.entries)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
