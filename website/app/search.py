import re
from typing import List, Dict, Any
from app.database import get_db

def clean_query(q: str) -> str:
    """Sanitizes user search query to letters, numbers, and basic spaces."""
    if not q:
        return ""
    q = re.sub(r'[^a-zA-Z0-9\s\$\-\&]', ' ', q)
    return " ".join(q.split())[:80].strip()

def search_site(query: str, limit: int = 25) -> Dict[str, Any]:
    """
    Searches published articles and verified menu items for the query.
    Returns categorized, ranked results with highlighted snippets.
    """
    clean_q = clean_query(query)
    if not clean_q or len(clean_q) < 2:
        return {"query": query, "articles": [], "menu_items": [], "total": 0}

    terms = clean_q.lower().split()
    results_articles = []
    results_menu = []

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Search Published Articles
        cursor.execute("""
            SELECT a.id, a.title, a.slug, a.summary, a.content, a.is_cornerstone, 
                   c.name as category_name, c.slug as category_slug
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE a.status = 'published'
        """)
        articles = cursor.fetchall()

        for art in articles:
            score = 0
            title_lower = art["title"].lower()
            summary_lower = (art["summary"] or "").lower()
            content_lower = art["content"].lower()
            cat_lower = (art["category_name"] or "").lower()

            for term in terms:
                if term in title_lower:
                    score += 15
                if term in cat_lower:
                    score += 8
                if term in summary_lower:
                    score += 5
                if term in content_lower:
                    score += 2

            if score > 0:
                # Generate snippet
                snippet = art["summary"]
                if not snippet:
                    snippet = art["content"][:160] + "..."
                elif len(snippet) > 160:
                    snippet = snippet[:160] + "..."

                results_articles.append({
                    "type": "article",
                    "title": art["title"],
                    "url": f"/articles/{art['slug']}",
                    "category": art["category_name"] or "General Guide",
                    "snippet": snippet,
                    "is_cornerstone": bool(art["is_cornerstone"]),
                    "score": score
                })

        # 2. Search Menu Items
        cursor.execute("""
            SELECT m.id, m.name, m.slug, m.description, m.sizes_available, 
                   m.price_formatted, m.calories, m.verification_status,
                   c.name as category_name, c.slug as category_slug
            FROM menu_items m
            LEFT JOIN categories c ON m.category_id = c.id
            WHERE m.is_active = 1
        """)
        menu_items = cursor.fetchall()

        for item in menu_items:
            score = 0
            name_lower = item["name"].lower()
            desc_lower = (item["description"] or "").lower()
            cat_lower = (item["category_name"] or "").lower()

            for term in terms:
                if term in name_lower:
                    score += 20
                if term in cat_lower:
                    score += 10
                if term in desc_lower:
                    score += 4
                if term in ["price", "prices", "cost"] and item["price_formatted"]:
                    score += 12
                if term in ["calorie", "calories", "nutrition"] and item["calories"]:
                    score += 12

            if score > 0:
                # Determine URL based on category
                target_url = "/menu"
                cat_slug = item["category_slug"]
                if cat_slug == "blizzards":
                    target_url = "/blizzards"
                elif cat_slug == "cakes":
                    target_url = "/cakes"
                elif cat_slug in ("burgers", "food"):
                    target_url = "/food"
                elif cat_slug == "breakfast":
                    target_url = "/breakfast"
                elif cat_slug == "treats":
                    target_url = "/treats-desserts"

                results_menu.append({
                    "type": "menu_item",
                    "name": item["name"],
                    "category": item["category_name"],
                    "price": item["price_formatted"] or "Prices vary",
                    "calories": item["calories"] or "Varies by size",
                    "sizes": item["sizes_available"] or "",
                    "description": item["description"] or "",
                    "url": target_url,
                    "verification": item["verification_status"],
                    "score": score
                })

    # Sort by relevance score
    results_articles.sort(key=lambda x: x["score"], reverse=True)
    results_menu.sort(key=lambda x: x["score"], reverse=True)

    combined_total = len(results_articles) + len(results_menu)
    return {
        "query": clean_q,
        "articles": results_articles[:limit],
        "menu_items": results_menu[:limit],
        "total": combined_total
    }

def get_autocomplete_suggestions(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """Returns fast, lightweight autocomplete suggestions for search input."""
    clean_q = clean_query(query)
    if not clean_q or len(clean_q) < 2:
        return []

    q_lower = clean_q.lower()
    suggestions = []

    # Popular curated guide shortcuts
    shortcuts = [
        {"title": "Dairy Queen Menu with Prices", "url": "/menu", "category": "Master Guide"},
        {"title": "Blizzard Flavors & Complete Menu", "url": "/blizzards", "category": "Blizzards"},
        {"title": "Blizzard Prices & Size Comparison", "url": "/blizzards/prices-sizes", "category": "Pricing"},
        {"title": "Current & Seasonal Blizzard Flavors", "url": "/blizzards/seasonal", "category": "Seasonal"},
        {"title": "Blizzard Calories & Nutrition Chart", "url": "/blizzards/nutrition", "category": "Nutrition"},
        {"title": "Ice Cream Cakes & Cake Prices", "url": "/cakes/prices-sizes", "category": "Cakes"},
        {"title": "Grill & Chill Food Menu & Combos", "url": "/food", "category": "Food Menu"},
        {"title": "Signature Stackburgers & FlameThrower", "url": "/food/burgers", "category": "Burgers"},
        {"title": "Breakfast Menu & Operating Hours", "url": "/breakfast", "category": "Breakfast"},
        {"title": "DQ Deals, $7 Meal Deal & Coupons", "url": "/deals-coupons", "category": "Deals"},
        {"title": "Online Ordering, DoorDash & Delivery", "url": "/ordering-delivery", "category": "Delivery"},
        {"title": "Allergen & Gluten-Free Guide", "url": "/nutrition-allergens", "category": "Allergens"}
    ]

    for sc in shortcuts:
        if q_lower in sc["title"].lower() or any(term in sc["title"].lower() for term in q_lower.split()):
            suggestions.append(sc)

    # Database matching for menu items
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, price_formatted, category_id 
            FROM menu_items 
            WHERE lower(name) LIKE ? AND is_active = 1
            LIMIT 5
        """, (f"%{q_lower}%",))
        rows = cursor.fetchall()
        for r in rows:
            suggestions.append({
                "title": f"{r['name']} ({r['price_formatted'] or 'Prices vary'})",
                "url": f"/menu?search={r['name']}",
                "category": "Menu Item"
            })

    return suggestions[:limit]
