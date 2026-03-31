import re
import unicodedata
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    """Removes HTML remnants, normalizes spacing, and strips text."""
    if not text:
        return ""
    # Normalize unicode (handles different encodings)
    text = unicodedata.normalize("NFKC", text)
    # Remove excessive whitespaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def validate_url(url: str) -> bool:
    """Validates that the input is a proper URL from supported domains (optional restriction)."""
    try:
        result = urlparse(url)
        # Check for scheme/netloc
        return all([result.scheme, result.netloc])
    except:
        return False

ALLOWED_DOMAINS = ["bbc.com", "cnn.com", "ndtv.com", "thehindu.com", "timesofindia.indiatimes.com"]

def is_safe_domain(url: str) -> bool:
    """Basic security check for specific domains if needed."""
    domain = urlparse(url).netloc.lower()
    return any(d in domain for d in ALLOWED_DOMAINS) or not ALLOWED_DOMAINS # If empty allow all
