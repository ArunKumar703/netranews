from fastapi import APIRouter, HTTPException, Query
from services.news_service import get_news_by_category, get_available_categories

router = APIRouter()

@router.get("/categories")
async def fetch_categories(lang: str = Query("en")):
    """
    Returns the list of mapping categories, optionally translated.
    """
    return get_available_categories(lang=lang)

@router.get("/news/{category}")
async def fetch_news(category: str, lang: str = Query("en"), limit: int = Query(10, ge=1, le=50)):
    """
    Endpoint to get news by category in a specific language.
    """
    articles = get_news_by_category(category, limit=limit, lang=lang)
    if not articles:
        raise HTTPException(status_code=404, detail=f"No articles found for category: {category} in language: {lang}")
    
    return {
        "category": category,
        "language": lang,
        "articles": articles
    }
