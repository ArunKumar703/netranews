# 📰 News API - Complete Setup Guide

## What You Got

A FastAPI news server that gives you **all news from multiple categories** with full article content through simple API endpoints.

---

## 🚀 QUICK START (3 STEPS)

### Step 1: Get FREE API Key
1. Go to: https://newsapi.org
2. Click **Sign Up** (top right)
3. Create account with your email
4. Check your email for API key
5. Copy the API key

### Step 2: Add API Key to Code
1. Open file: `news_api.py`
2. Find line 19: `NEWS_API_KEY = "demo"`
3. Replace `"demo"` with your API key
4. Save file (Ctrl+S)

### Step 3: Run the Server
**EASY WAY:**
- Double-click `run.bat` file

**OR MANUAL WAY:**
- Open terminal in this folder
- Run command: `python news_api.py`

---

## ✅ How to Use the API

Once server is running, open your browser and go to:

### 📍 Main endpoints:

1. **Get ALL News (All Categories)**
   ```
   http://localhost:8000/news
   ```

2. **Get News by Category**
   ```
   http://localhost:8000/news/category/business
   http://localhost:8000/news/category/sports
   http://localhost:8000/news/category/technology
   http://localhost:8000/news/category/health
   http://localhost:8000/news/category/entertainment
   http://localhost:8000/news/category/science
   http://localhost:8000/news/category/general
   ```

3. **Search News**
   ```
   http://localhost:8000/news/search?q=python
   http://localhost:8000/news/search?q=artificial intelligence
   ```

4. **See All Available Categories**
   ```
   http://localhost:8000/categories
   ```

5. **Interactive API Documentation** (BEST WAY TO TEST)
   ```
   http://localhost:8000/docs
   ```

---

## 📊 What You Get from Each Article

Each article includes:
- ✅ **Title** - News headline
- ✅ **Description** - Short summary
- ✅ **Content** - Full article text
- ✅ **URL** - Link to full article
- ✅ **Image** - Article image
- ✅ **Source** - News source name
- ✅ **Published At** - When published
- ✅ **Author** - Who wrote it

---

## 💻 Files Explained

| File | Purpose |
|------|---------|
| `news_api.py` | Main API server code |
| `requirements.txt` | List of packages to install |
| `run.bat` | Easy startup script (Windows) |
| `README.md` | This file |

---

## 🎯 Example API Response

```json
{
  "status": "success",
  "totalResults": 38,
  "articles": [
    {
      "title": "Latest Breaking News",
      "description": "Full description of the news",
      "content": "Complete full article content...",
      "url": "https://example.com/article",
      "image": "https://example.com/image.jpg",
      "source": "BBC News",
      "published_at": "2026-03-30T10:30:00Z",
      "author": "John Smith"
    }
  ],
  "count": 20
}
```

---

## ⚙️ Need Help?

### Problem: "API limit reached" error
- **Solution**: Make sure you replaced `"demo"` with your real API key on line 19

### Problem: Can't install packages
- **Solution**: Open terminal and run: `pip install fastapi uvicorn requests`

### Problem: Port 8000 already in use
- **Solution**: Open `news_api.py`, find last line, change `port=8000` to `port=8001`

---

## 🌍 What's Powered By

- **FastAPI** - Super fast modern API framework
- **NewsAPI.org** - Real-time news data from 150,000+ sources

---

## 📝 License

Free to use and modify for personal projects.

---

**Enjoy your News API! 🎉**
