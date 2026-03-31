import newspaper
from newspaper import Article
import nltk
from typing import Dict, Optional
from utils.helpers import clean_text

# Ensure NLTK data is downloaded for NLP features (one-time check)
# Ensure NLTK data is downloaded for NLP features (one-time check)
try:
    # Modern NLTK uses punkt_tab occasionally
    for pkg in ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'stopwords']:
        try:
            nltk.download(pkg, quiet=True)
        except:
            pass
except LookupError:
    pass

def get_article_content(url: str, language: str = 'en') -> Optional[Dict]:
    """Downloads and parses a full article with multi-level fallback and 'Landing Page' detection."""
    try:
        config = newspaper.Config()
        config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        config.request_timeout = 10

        # Step 1: Attempt standard parsing
        try:
            article = Article(url, language=language, config=config, memoize_articles=False)
            article.download()
            article.parse()
        except:
            article = Article(url, language='en', config=config, memoize_articles=False)
            article.download()
            article.parse()
            
        # Step 2: 'Landing Page' Check (Articles usually have body text > 300 chars)
        # If it's a directory page (like /latest or /news), it won't have a main body
        if len(article.text) < 300:
            # Try to build a newspaper source to get the first real article
            paper = newspaper.build(url, memoize_articles=False, language='en')
            if paper.articles:
                # Recursively try to get the first article's content
                first_article_url = paper.articles[0].url
                # Avoid infinite loops by checking it's a different URL
                if first_article_url != url:
                    return get_article_content(first_article_url, language=language)

        # Selection and Exact extraction strategy
        raw_text = article.text
        # Fallback to Summary (NLP) if text is very short (<200 chars)
        if len(raw_text) < 200 and hasattr(article, 'summary') and article.summary:
            raw_text = article.summary

        cleaned_text = clean_text(raw_text)
        
        # Remove common "read more" noise
        import re
        garbage_patterns = [
            r'Read More:.*', r'Original Article:.*', r'Follow us on.*', 
            r'Advertisement', r'©.*', r'All rights reserved.*',
            r'Story continues.*', r'WATCH:.*', r'ALSO READ:.*'
        ]
        for pattern in garbage_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)

        if not cleaned_text or len(cleaned_text) < 100:
            if article.title:
                cleaned_text = f"The full content for '{article.title}' is protected or inaccessible. Please visit the original source for the full story."
            else:
                return None
            
        return {
            "title": article.title or "Recent News Highlight",
            "text": cleaned_text.strip(),
            "top_image": article.top_image,
            "publish_date": str(article.publish_date) if article.publish_date else "N/A"
        }
    except Exception as e:
        print(f"Extraction Error: {str(e)}")
        return {
            "title": "Article Content",
            "text": "Failed to parse content from this link. It might be protected or not a supported article format.",
            "top_image": None,
            "publish_date": "N/A"
        }

