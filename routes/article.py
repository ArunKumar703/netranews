from fastapi import APIRouter, HTTPException, Query
from services.article_service import get_article_content
from utils.helpers import validate_url, is_safe_domain

router = APIRouter()

@router.get("/article-content")
async def fetch_article(url: str = Query(..., description="URL of the news article"), 
                        lang: str = Query("en", description="Language code (en, hi, te)")):
    """
    Endpoint to get full article content.
    """
    if not validate_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Optional security check
    # if not is_safe_domain(url):
    #    raise HTTPException(status_code=403, detail="Domain not allowed")

    content = get_article_content(url, language=lang)
    
    if not content:
        raise HTTPException(status_code=404, detail="No content found or failed to parse article")
    
    return content
