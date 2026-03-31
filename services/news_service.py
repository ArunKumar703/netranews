import newspaper
import feedparser
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from utils.helpers import clean_text
from deep_translator import GoogleTranslator
from functools import lru_cache

@lru_cache(maxsize=100)
def translate_text(text: str, target_lang: str) -> str:
    """Translates a small piece of text to target language."""
    if not text or target_lang == "en":
        return text
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except:
        return text

# Map category IDs to Google News RSS search keywords (in English, usually works across regions)
CATEGORY_KEYWORDS = {
    "topnews": "top stories",
    "entertainment": "entertainment",
    "cricket": "cricket",
    "buzz": "trending",
    "international": "world",
    "impact_shorts": "news",
    "instantloan": "finance loan",
    "national": "India",
    "business": "business",
    "lifestyle": "lifestyle",
    "tech": "technology",
    "educationandcareer": "education career",
    "explainers": "explainers news",
    "opinion": "opinion",
    "politics": "politics"
}

# Updated to match the IDs in user screenshot
CATEGORY_SOURCES = {
    "topnews": ["https://zeenews.india.com/rss/india-national-news.xml", "https://www.ndtv.com/latest"],
    "entertainment": ["https://zeenews.india.com/rss/entertainment-news.xml", "https://www.ndtv.com/entertainment"],
    "cricket": ["https://zeenews.india.com/rss/sports-news.xml", "https://www.ndtv.com/cricket"],
    "buzz": ["https://zeenews.india.com/rss/technology-news.xml", "https://www.ndtv.com/offbeat"],
    "international": ["https://zeenews.india.com/rss/world-news.xml", "https://www.bbc.com/news/world"],
    "impact_shorts": ["https://zeenews.india.com/rss/india-national-news.xml"],
    "instantloan": ["https://economictimes.indiatimes.com/wealth/borrow"],
    "national": ["https://zeenews.india.com/rss/india-national-news.xml", "https://www.ndtv.com/india-news"],
    "business": ["https://zeenews.india.com/rss/business-news.xml", "https://www.ndtv.com/business"],
    "lifestyle": ["https://zeenews.india.com/rss/health-news.xml", "https://www.ndtv.com/lifestyle"],
    "tech": ["https://zeenews.india.com/rss/technology-news.xml", "https://www.ndtv.com/tech"],
    "educationandcareer": ["https://zeenews.india.com/rss/india-national-news.xml"],
    "explainers": ["https://www.ndtv.com/explainers", "https://www.bbc.com/news/explainers"],
    "opinion": ["https://zeenews.india.com/rss/india-national-news.xml"],
    "politics": ["https://zeenews.india.com/rss/india-national-news.xml", "https://www.ndtv.com/india-news"]
}

def process_one_article(article_obj: newspaper.Article, source_name: str) -> Dict:
    """Download and parse a single article with precision and 'all exact full' text guarantee."""
    try:
        config = newspaper.Config()
        # Use more comprehensive headers for better access
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        config.request_timeout = 15
        
        try:
            article_obj.config = config
            article_obj.download()
            article_obj.parse()
            # Run NLP for summary/keywords which are better fallbacks than meta-description
            try:
                import nltk
                article_obj.nlp()
            except:
                pass
        except Exception as lang_err:
            url = article_obj.url
            article_obj = newspaper.Article(url, language='en', config=config)
            article_obj.download()
            article_obj.parse()
        
        # Exact extraction strategy
        raw_text = article_obj.text
        # Fallback to Summary (NLP) if text is very short (<200 chars)
        if len(raw_text) < 200 and hasattr(article_obj, 'summary') and article_obj.summary:
            raw_text = article_obj.summary
            
        cleaned_text = clean_text(raw_text)
        
        # Remove common "read more" noise
        garbage_patterns = [
            r'Read More:.*', r'Original Article:.*', r'Follow us on.*', 
            r'Advertisement', r'©.*', r'All rights reserved.*',
            r'Story continues.*', r'WATCH:.*', r'ALSO READ:.*'
        ]
        import re
        for pattern in garbage_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        if not cleaned_text or len(cleaned_text) < 100:
            return None

        return {
            "title": article_obj.title or "Recent News Highlight",
            "text": cleaned_text.strip(),
            "source": source_name.upper(),
            "top_image": article_obj.top_image,
            "publish_date": str(article_obj.publish_date) if article_obj.publish_date else "N/A"
        }
    except Exception as e:
        print(f"Error processing article: {str(e)}")
        return None

def fetch_source_articles(source_url: str, limit: int = 5, lang: str = 'en') -> List[Dict]:
    """Uses newspaper to discover and process articles with native RSS and XML support."""
    try:
        config = newspaper.Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        config.request_timeout = 15
        
        # 0. Handle RSS/XML Directly
        if source_url.endswith('.xml') or 'rss' in source_url.lower():
            import feedparser
            feed = feedparser.parse(source_url)
            articles = []
            for entry in feed.entries[:limit]:
                article_obj = newspaper.Article(entry.link, language=lang, config=config)
                processed = process_one_article(article_obj, "RSS Feed")
                if processed:
                    articles.append(processed)
            return articles

        # Follow redirect if it's a Google News link or similar
        import requests
        try:
            r = requests.head(source_url, allow_redirects=True, timeout=5, headers={'User-Agent': config.browser_user_agent})
            final_url = r.url
        except:
            final_url = source_url

        # Check if source_url is a single article
        if "/article/" in final_url or ".html" in final_url or final_url.count("/") > 3:
            article_obj = newspaper.Article(final_url, language=lang, config=config)
            processed = process_one_article(article_obj, "News Source")
            return [processed] if processed else []

        source_name = final_url.split('/')[2].replace('www.', '').split('.')[0]
        paper = newspaper.build(final_url, memoize_articles=False, language=lang, config=config)
        
        articles = []
        for article_obj in paper.articles:
            if len(articles) >= limit:
                break
            processed = process_one_article(article_obj, source_name)
            if processed:
                articles.append(processed)
        
        return articles
    except Exception as e:
        print(f"Error fetching from {source_url}: {str(e)}")
        return []

def get_news_by_category(category: str, limit: int = 5, lang: str = "en") -> List[Dict]:
    """Fetches news and merges results with better error handling."""
    category_id = category.lower()
    all_articles = []
    
    # Language switch: non-English uses Google News search
    if lang != "en":
        keyword = CATEGORY_KEYWORDS.get(category_id, category_id)
        from urllib.parse import quote
        keyword_encoded = quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={keyword_encoded}&hl={lang}&gl=IN&ceid=IN:{lang}"
        feed = feedparser.parse(rss_url)
        # Higher limit for fetching to compensate for filtered results
        urls = [entry.link for entry in feed.entries[:limit*2]]
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # We fetch 1 article per URL from the RSS feed
            results = list(executor.map(lambda u: fetch_source_articles(u, limit=1, lang=lang), urls))
            for res_list in results:
                if res_list:
                    all_articles.extend(res_list)
    else:
        urls = CATEGORY_SOURCES.get(category_id, [])
        if not urls:
            return []
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda u: fetch_source_articles(u, limit=limit, lang='en'), urls))
            for res_list in results:
                all_articles.extend(res_list)
    
    # Filtering and Deduplication
    seen = set()
    deduped = []
    for item in all_articles:
        if not item or not item.get("title") or not item.get("text"):
            continue
        # Avoid the "Google News" fake entry
        if "Google News" in item["title"] and len(item["text"]) < 150:
            continue
            
        title_norm = item["title"].lower().strip()
        if title_norm not in seen:
            seen.add(title_norm)
            deduped.append(item)
            
    return deduped[:limit*2] # Return a bit more for the category view if available

def get_available_categories(lang: str = "en"):
    """Returns the list of mapping categories, translated if needed."""
    base_categories = [
        {"id": "topnews", "title": "HOME"},
        {"id": "entertainment", "title": "ENTERTAINMENT"},
        {"id": "cricket", "title": "CRICKET"},
        {"id": "buzz", "title": "TRENDING"},
        {"id": "international", "title": "WORLD"},
        {"id": "impact_shorts", "title": "IMPACT SHORTS"},
        {"id": "instantloan", "title": "LOANS @ 10%"},
        {"id": "national", "title": "NATIONAL"},
        {"id": "business", "title": "BUSINESS"},
        {"id": "lifestyle", "title": "LIFESTYLE"},
        {"id": "tech", "title": "TECH"},
        {"id": "educationandcareer", "title": "EDUCATION AND CAREER"},
        {"id": "explainers", "title": "EXPLAINERS"},
        {"id": "opinion", "title": "OPINION"},
        {"id": "politics", "title": "POLITICS"}
    ]
    
    if lang == "en":
        return base_categories
        
    for cat in base_categories:
        cat["title"] = translate_text(cat["title"], lang)
        
    return base_categories


