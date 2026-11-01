import re
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.search import get_autocomplete_suggestions, search_site

def sanitize_input(val: str, max_len: int = 100) -> str:
    """Sanitize and length-limit search API queries."""
    if not val:
        return ""
    # Strip potential control characters and truncate
    clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', val)
    return clean[:max_len].strip()

async def api_search_suggestions(request: Request):
    """Provides fast autocomplete search suggestions."""
    q = sanitize_input(request.query_params.get("q", ""))
    if len(q) < 2:
        return JSONResponse([])
    suggestions = get_autocomplete_suggestions(q, limit=8)
    return JSONResponse(suggestions)

async def api_search_full(request: Request):
    """Returns full JSON search results for headless or dynamic consumption."""
    q = sanitize_input(request.query_params.get("q", ""))
    results = search_site(q, limit=20)
    return JSONResponse(results)
