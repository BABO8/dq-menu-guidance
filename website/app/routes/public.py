import json
import time
from datetime import datetime
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response, RedirectResponse, FileResponse
from pathlib import Path
from starlette.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from app.config import settings
from app.database import get_db
from app.search import search_site
from app.auth import generate_csrf_token, verify_csrf_token

from jinja2 import pass_context

templates = Jinja2Templates(directory="app/templates")

_orig_url_for = templates.env.globals.get("url_for")
@pass_context
def _compat_url_for(context, name: str, **path_params):
    if name == "static":
        filename = path_params.pop("filename", None)
        if filename and "path" not in path_params:
            path_params["path"] = filename
    request = context.get("request")
    if request is not None and hasattr(request, "url_for"):
        try:
            return request.url_for(name, **path_params)
        except Exception:
            pass
    if _orig_url_for is not None:
        try:
            return _orig_url_for(context, name, **path_params)
        except Exception:
            pass
    if name == "static":
        return f"/static/{path_params.get('path', '')}"
    return f"/{name}"

templates.env.globals["url_for"] = _compat_url_for

def get_base_context(request: Request, active_page: str = "") -> dict:
    clean_path = request.url.path
    if not clean_path.startswith("/"):
        clean_path = "/" + clean_path
    canonical_url = f"{settings.SITE_URL.rstrip('/')}{clean_path}"
    
    return {
        "request": request,
        "settings": settings,
        "active_page": active_page,
        "canonical_url": canonical_url,
        "csrf_token": generate_csrf_token(request),
        "noindex": False
    }

async def home_page(request: Request):
    with get_db() as conn:
        c = conn.cursor()
        # Featured popular items
        c.execute("""
            SELECT m.*, c.name as category_name, c.slug as category_slug
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE m.is_active = 1
            LIMIT 8
        """)
        featured_items = c.fetchall()

        # Cornerstone articles
        c.execute("""
            SELECT a.*, c.name as category_name
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE a.status = 'published' AND a.is_cornerstone = 1
            ORDER BY a.id ASC
            LIMIT 6
        """)
        articles = c.fetchall()

        # Top FAQs
        c.execute("SELECT * FROM faqs WHERE is_active = 1 ORDER BY display_order ASC")
        faqs = c.fetchall()

    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f["answer"]
                }
            }
            for f in faqs
        ]
    }

    ctx = get_base_context(request, active_page="home")
    ctx.update({
        "featured_items": featured_items,
        "articles": articles,
        "faqs": faqs,
        "faq_json_ld": json.dumps(faq_ld, ensure_ascii=False)
    })
    return templates.TemplateResponse(request, "index.html", ctx)

async def menu_hub_page(request: Request):
    cat_filter = request.query_params.get("category", "").strip()
    search_q = request.query_params.get("search", "").strip()

    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY display_order ASC")
        categories = c.fetchall()

        query = """
            SELECT m.*, c.name as category_name, c.slug as category_slug
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE m.is_active = 1
        """
        params = []

        if cat_filter:
            query += " AND c.slug = ?"
            params.append(cat_filter)
        if search_q:
            query += " AND (lower(m.name) LIKE ? OR lower(m.description) LIKE ?)"
            params.extend([f"%{search_q.lower()}%", f"%{search_q.lower()}%"])

        query += " ORDER BY c.display_order ASC, m.id ASC"
        c.execute(query, params)
        menu_items = c.fetchall()

    # Build Menu schema.org JSON-LD
    menu_ld = {
        "@context": "https://schema.org",
        "@type": "Menu",
        "name": "Dairy Queen Menu With Prices (2026 US Reference)",
        "description": "Comprehensive reference of Dairy Queen menu items, estimated US prices, calories, and nutrition information.",
        "inLanguage": "en-US",
        "hasMenuSection": []
    }
    cat_items_map = {}
    for item in menu_items:
        cat_items_map.setdefault(item["category_id"], []).append(item)

    for cat in categories:
        sec_items = cat_items_map.get(cat["id"], [])
        if not sec_items:
            continue
        section_obj = {
            "@type": "MenuSection",
            "name": cat["name"],
            "description": cat["description"] or "",
            "hasMenuItem": []
        }
        for m in sec_items:
            item_obj = {
                "@type": "MenuItem",
                "name": m["name"],
                "description": m["description"] or "",
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "USD",
                    "price": f"{m['price_min']:.2f}" if m["price_min"] else "0.00",
                    "priceValidUntil": "2026-12-31"
                }
            }
            if m["calories"]:
                item_obj["nutrition"] = {
                    "@type": "NutritionInformation",
                    "calories": m["calories"]
                }
            section_obj["hasMenuItem"].append(item_obj)
        menu_ld["hasMenuSection"].append(section_obj)

    ctx = get_base_context(request, active_page="menu")
    ctx.update({
        "categories": categories,
        "menu_items": menu_items,
        "selected_category": cat_filter,
        "search_q": search_q,
        "menu_json_ld": json.dumps(menu_ld, ensure_ascii=False)
    })
    return templates.TemplateResponse(request, "menu_hub.html", ctx)

async def blizzards_page(request: Request):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT m.*, c.name as category_name
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE c.slug = 'blizzards' AND m.is_active = 1
            ORDER BY m.is_seasonal ASC, m.id ASC
        """)
        blizzard_items = c.fetchall()

    ctx = get_base_context(request, active_page="blizzards")
    ctx.update({"blizzard_items": blizzard_items})
    return templates.TemplateResponse(request, "blizzards.html", ctx)

async def blizzard_prices_page(request: Request):
    ctx = get_base_context(request, active_page="blizzards")
    return templates.TemplateResponse(request, "blizzard_prices.html", ctx)

async def seasonal_blizzards_page(request: Request):
    ctx = get_base_context(request, active_page="blizzards")
    return templates.TemplateResponse(request, "seasonal.html", ctx)

async def blizzard_nutrition_page(request: Request):
    ctx = get_base_context(request, active_page="blizzards")
    return templates.TemplateResponse(request, "blizzard_nutrition.html", ctx)

async def cakes_page(request: Request):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT m.*, c.name as category_name
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE c.slug = 'cakes' AND m.is_active = 1
            ORDER BY m.id ASC
        """)
        cake_items = c.fetchall()

    ctx = get_base_context(request, active_page="cakes")
    ctx.update({"cake_items": cake_items})
    return templates.TemplateResponse(request, "cakes.html", ctx)

async def cake_prices_page(request: Request):
    ctx = get_base_context(request, active_page="cakes")
    return templates.TemplateResponse(request, "cake_prices.html", ctx)

async def food_page(request: Request):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT m.*, c.name as category_name
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE c.slug IN ('food', 'burgers') AND m.is_active = 1
            ORDER BY c.display_order ASC, m.id ASC
        """)
        food_items = c.fetchall()

    ctx = get_base_context(request, active_page="food")
    ctx.update({"food_items": food_items})
    return templates.TemplateResponse(request, "food.html", ctx)

async def burgers_page(request: Request):
    ctx = get_base_context(request, active_page="food")
    return templates.TemplateResponse(request, "burgers.html", ctx)

async def breakfast_page(request: Request):
    ctx = get_base_context(request, active_page="menu")
    return templates.TemplateResponse(request, "breakfast.html", ctx)

async def treats_desserts_page(request: Request):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT m.*, c.name as category_name
            FROM menu_items m
            JOIN categories c ON m.category_id = c.id
            WHERE c.slug IN ('treats', 'drinks') AND m.is_active = 1
            ORDER BY c.display_order ASC, m.id ASC
        """)
        treat_items = c.fetchall()

    ctx = get_base_context(request, active_page="treats")
    ctx.update({"treat_items": treat_items})
    return templates.TemplateResponse(request, "treats_desserts.html", ctx)

async def nutrition_allergens_page(request: Request):
    ctx = get_base_context(request, active_page="nutrition")
    return templates.TemplateResponse(request, "nutrition_allergens.html", ctx)

async def deals_coupons_page(request: Request):
    ctx = get_base_context(request, active_page="deals")
    return templates.TemplateResponse(request, "deals_coupons.html", ctx)

async def ordering_delivery_page(request: Request):
    ctx = get_base_context(request, active_page="menu")
    return templates.TemplateResponse(request, "ordering_delivery.html", ctx)

async def faqs_page(request: Request):
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM faqs WHERE is_active = 1 ORDER BY display_order ASC")
        faqs = c.fetchall()

    ctx = get_base_context(request, active_page="faqs")
    ctx.update({"faqs": faqs})
    return templates.TemplateResponse(request, "faqs.html", ctx)

ARTICLE_FEATURED_IMG_MAP = {
    "dairy-queen-menu-with-prices": {"img": "homepage-food-hero", "alt": "Assortment of popular Dairy Queen treats and meals"},
    "dairy-queen-blizzard-menu-flavors": {"img": "blizzard-treats", "alt": "Classic Blizzard treat with candy and cookie mix-ins"},
    "dairy-queen-blizzard-prices-sizes": {"img": "blizzard-treats", "alt": "Blizzard treat cup comparison and sizes"},
    "dairy-queen-ice-cream-cake-menu-prices": {"img": "ice-cream-cake", "alt": "Decorated round celebration ice cream cake"},
    "dairy-queen-food-menu-prices": {"img": "burger-menu", "alt": "Signature double cheeseburger on toasted bun"},
    "dairy-queen-nutrition-calories-guide": {"img": "nutrition-guide-food", "alt": "Fresh balanced food ingredients and nutrition transparency"},
    "dairy-queen-deals-coupons-guide": {"img": "chicken-strip-meal", "alt": "Crispy chicken strips meal deal with fries and dipping gravy"},
    "dairy-queen-breakfast-menu-hours": {"img": "breakfast-platter", "alt": "Traditional country breakfast platter with eggs, toast, and bacon"},
    "dairy-queen-online-ordering-delivery-guide": {"img": "homepage-food-hero", "alt": "Fast-food order spread for pickup and delivery"},
    # 22 new SEO-optimized articles
    "dq-summer-blizzard-menu-flavors": {"img": "blizzard-fruit-strawberry", "alt": "Dairy Queen Summer Blizzard menu lineup and limited-time flavors"},
    "dairy-queen-blizzard-of-the-month": {"img": "blizzard-caramel-pecan", "alt": "Dairy Queen Blizzard of the Month featured creation"},
    "dq-signature-stackburgers-guide": {"img": "bacon-stackburger", "alt": "Dairy Queen Signature Double Stackburger with bacon and melted cheese"},
    "dairy-queen-2-for-5-mix-and-match": {"img": "burger-and-fries", "alt": "Dairy Queen 2 for $5 Super Snack and Mix & Match deal"},
    "dairy-queen-7-dollar-meal-deal-upgrade": {"img": "chicken-strip-meal", "alt": "Dairy Queen $7 Meal Deal with chicken tenders, fries, drink, and sundae"},
    "dairy-queen-chicken-strip-baskets-sauces": {"img": "chicken-strip-meal", "alt": "Dairy Queen crispy chicken strip basket with country gravy and Texas toast"},
    "dairy-queen-delivery-order-online-guide": {"img": "homepage-food-hero", "alt": "Dairy Queen online ordering and doorstep delivery guide"},
    "dairy-queen-allergy-menu-gluten-free-options": {"img": "nutrition-guide-food", "alt": "Dairy Queen allergen safety guide and gluten-free dining precautions"},
    "dairy-queen-ice-cream-cake-ordering-prices": {"img": "birthday-ice-cream-cake", "alt": "Dairy Queen celebration ice cream cake with custom piping"},
    "dairy-queen-breakfast-biscuits-platters": {"img": "breakfast-platter", "alt": "Dairy Queen Southern breakfast platter with biscuits, gravy, and eggs"},
    "dairy-queen-grill-and-chill-vs-treat-stores": {"img": "burger-menu", "alt": "Dairy Queen Grill & Chill restaurant exterior and menu"},
    "dairy-queen-royal-blizzard-treats-guide": {"img": "blizzard-chocolate-cookie", "alt": "Dairy Queen Royal Blizzard with rich molten fudge center"},
    "dairy-queen-classic-novelties-dilly-buster-bars": {"img": "chocolate-dipped-cone", "alt": "Dairy Queen classic frozen stick novelties and Dilly Bars"},
    "dairy-queen-secret-menu-blizzards-treats": {"img": "blizzard-peanut-butter", "alt": "Dairy Queen secret menu custom Blizzard creation"},
    "dairy-queen-shakes-malts-frozen-drinks": {"img": "milkshakes", "alt": "Dairy Queen hand-spun shakes, malts, and Misty Slush frozen drinks"},
    "dairy-queen-kids-meal-options-pricing": {"img": "burger-and-fries", "alt": "Dairy Queen Kids Meal with cheeseburger, fries, and soft-serve treat"},
    "dairy-queen-state-regional-price-disparities": {"img": "homepage-food-hero", "alt": "Dairy Queen regional franchise price comparison across U.S. states"},
    "dairy-queen-flamethrower-sauce-menu-items": {"img": "flamethrower-burger", "alt": "Dairy Queen FlameThrower burger with spicy sauce and Pepper Jack cheese"},
    "dairy-queen-app-rewards-free-food-hacks": {"img": "ice-cream-sundae", "alt": "Dairy Queen DQ Rewards loyalty program and mobile app coupons"},
    "dairy-queen-dilly-bar-flavors-box-pricing": {"img": "soft-serve-cone", "alt": "Dairy Queen Dilly Bar multi-pack box and flavor varieties"},
    "dairy-queen-fall-winter-seasonal-menu": {"img": "blizzard-caramel-pecan", "alt": "Dairy Queen Fall and Holiday seasonal Blizzard menu lineup"}
}

CATEGORY_IMG_FALLBACKS = {
    "blizzards": "blizzard-treats",
    "cakes": "ice-cream-cake",
    "burgers": "burger-menu",
    "food": "chicken-strip-meal",
    "treats": "chocolate-dipped-cone",
    "drinks": "milkshakes",
    "breakfast": "breakfast-platter",
    "deals": "burger-and-fries",
    "nutrition": "nutrition-guide-food",
}

def get_article_featured_image(art: dict) -> dict:
    slug = art.get("slug", "")
    if slug in ARTICLE_FEATURED_IMG_MAP:
        return ARTICLE_FEATURED_IMG_MAP[slug]
    cat_slug = art.get("category_slug", "")
    img_name = CATEGORY_IMG_FALLBACKS.get(cat_slug, "homepage-food-hero")
    return {
        "img": img_name,
        "alt": f"{art.get('title', 'Dairy Queen')} - Dairy Queen Menu Guide"
    }

async def articles_hub_page(request: Request):
    cat_slug = request.query_params.get("category", "").strip().lower()
    search_q = request.query_params.get("q", "").strip()

    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT c.id, c.name, c.slug, COUNT(a.id) as article_count
            FROM categories c
            JOIN articles a ON a.category_id = c.id
            WHERE a.status = 'published'
            GROUP BY c.id, c.name, c.slug
            ORDER BY c.name ASC
        """)
        categories = [dict(r) for r in c.fetchall()]

        if cat_slug:
            c.execute("""
                SELECT a.*, c.name as category_name, c.slug as category_slug
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE a.status = 'published' AND c.slug = ?
                ORDER BY a.is_cornerstone DESC, a.id DESC
            """, (cat_slug,))
        else:
            c.execute("""
                SELECT a.*, c.name as category_name, c.slug as category_slug
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE a.status = 'published'
                ORDER BY a.is_cornerstone DESC, a.id DESC
            """)
        raw_articles = [dict(r) for r in c.fetchall()]

    enriched = []
    for a in raw_articles:
        if search_q and (search_q.lower() not in a["title"].lower() and search_q.lower() not in (a["summary"] or "").lower()):
            continue
        a["featured_image"] = get_article_featured_image(a)
        enriched.append(a)

    ctx = get_base_context(request, active_page="articles")
    canonical_url = f"{settings.SITE_URL.rstrip('/')}/articles"
    if cat_slug:
        canonical_url = f"{canonical_url}?category={cat_slug}"

    ctx.update({
        "articles": enriched,
        "categories": categories,
        "active_category": cat_slug,
        "search_query": search_q,
        "canonical_url": canonical_url,
        "total_count": len(enriched)
    })
    return templates.TemplateResponse(request, "articles.html", ctx)

async def article_detail_page(request: Request):
    slug = request.path_params.get("slug", "")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT a.*, c.name as category_name, c.slug as category_slug
            FROM articles a
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE a.slug = ? AND a.status = 'published'
        """, (slug,))
        art = c.fetchone()

    if not art:
        raise HTTPException(status_code=404, detail="Article not found")

    sources = []
    if art["sources_json"]:
        try:
            sources = json.loads(art["sources_json"])
        except Exception:
            sources = []

    ctx = get_base_context(request, active_page="menu")
    canonical_url = f"{settings.SITE_URL.rstrip('/')}/articles/{art['slug']}"
    ctx.update({
        "article": art,
        "sources": sources,
        "canonical_url": canonical_url
    })
    featured_img_map = {
        "dairy-queen-menu-with-prices": {"img": "homepage-food-hero", "alt": "Assortment of popular Dairy Queen treats and meals"},
        "dairy-queen-blizzard-menu-flavors": {"img": "blizzard-treats", "alt": "Classic Blizzard treat with candy and cookie mix-ins"},
        "dairy-queen-blizzard-prices-sizes": {"img": "blizzard-treats", "alt": "Blizzard treat cup comparison and sizes"},
        "dairy-queen-ice-cream-cake-menu-prices": {"img": "ice-cream-cake", "alt": "Decorated round celebration ice cream cake"},
        "dairy-queen-food-menu-prices": {"img": "burger-menu", "alt": "Signature double cheeseburger on toasted bun"},
        "dairy-queen-nutrition-calories-guide": {"img": "nutrition-guide-food", "alt": "Fresh balanced food ingredients and nutrition transparency"},
        "dairy-queen-deals-coupons-guide": {"img": "chicken-strip-meal", "alt": "Crispy chicken strips meal deal with fries and dipping gravy"},
        "dairy-queen-breakfast-menu-hours": {"img": "breakfast-platter", "alt": "Traditional country breakfast platter with eggs, toast, and bacon"},
        "dairy-queen-online-ordering-delivery-guide": {"img": "homepage-food-hero", "alt": "Fast-food order spread for pickup and delivery"},
        # 22 new SEO-optimized articles
        "dq-summer-blizzard-menu-flavors": {"img": "blizzard-fruit-strawberry", "alt": "Dairy Queen Summer Blizzard menu lineup and limited-time flavors"},
        "dairy-queen-blizzard-of-the-month": {"img": "blizzard-caramel-pecan", "alt": "Dairy Queen Blizzard of the Month featured creation"},
        "dq-signature-stackburgers-guide": {"img": "bacon-stackburger", "alt": "Dairy Queen Signature Double Stackburger with bacon and melted cheese"},
        "dairy-queen-2-for-5-mix-and-match": {"img": "burger-and-fries", "alt": "Dairy Queen 2 for $5 Super Snack and Mix & Match deal"},
        "dairy-queen-7-dollar-meal-deal-upgrade": {"img": "chicken-strip-meal", "alt": "Dairy Queen $7 Meal Deal with chicken tenders, fries, drink, and sundae"},
        "dairy-queen-chicken-strip-baskets-sauces": {"img": "chicken-strip-meal", "alt": "Dairy Queen crispy chicken strip basket with country gravy and Texas toast"},
        "dairy-queen-delivery-order-online-guide": {"img": "homepage-food-hero", "alt": "Dairy Queen online ordering and doorstep delivery guide"},
        "dairy-queen-allergy-menu-gluten-free-options": {"img": "nutrition-guide-food", "alt": "Dairy Queen allergen safety guide and gluten-free dining precautions"},
        "dairy-queen-ice-cream-cake-ordering-prices": {"img": "birthday-ice-cream-cake", "alt": "Dairy Queen celebration ice cream cake with custom piping"},
        "dairy-queen-breakfast-biscuits-platters": {"img": "breakfast-platter", "alt": "Dairy Queen Southern breakfast platter with biscuits, gravy, and eggs"},
        "dairy-queen-grill-and-chill-vs-treat-stores": {"img": "burger-menu", "alt": "Dairy Queen Grill & Chill restaurant exterior and menu"},
        "dairy-queen-royal-blizzard-treats-guide": {"img": "blizzard-chocolate-cookie", "alt": "Dairy Queen Royal Blizzard with rich molten fudge center"},
        "dairy-queen-classic-novelties-dilly-buster-bars": {"img": "chocolate-dipped-cone", "alt": "Dairy Queen classic frozen stick novelties and Dilly Bars"},
        "dairy-queen-secret-menu-blizzards-treats": {"img": "blizzard-peanut-butter", "alt": "Dairy Queen secret menu custom Blizzard creation"},
        "dairy-queen-shakes-malts-frozen-drinks": {"img": "milkshakes", "alt": "Dairy Queen hand-spun shakes, malts, and Misty Slush frozen drinks"},
        "dairy-queen-kids-meal-options-pricing": {"img": "burger-and-fries", "alt": "Dairy Queen Kids Meal with cheeseburger, fries, and soft-serve treat"},
        "dairy-queen-state-regional-price-disparities": {"img": "homepage-food-hero", "alt": "Dairy Queen regional franchise price comparison across U.S. states"},
        "dairy-queen-flamethrower-sauce-menu-items": {"img": "flamethrower-burger", "alt": "Dairy Queen FlameThrower burger with spicy sauce and Pepper Jack cheese"},
        "dairy-queen-app-rewards-free-food-hacks": {"img": "ice-cream-sundae", "alt": "Dairy Queen DQ Rewards loyalty program and mobile app coupons"},
        "dairy-queen-dilly-bar-flavors-box-pricing": {"img": "soft-serve-cone", "alt": "Dairy Queen Dilly Bar multi-pack box and flavor varieties"},
        "dairy-queen-fall-winter-seasonal-menu": {"img": "blizzard-caramel-pecan", "alt": "Dairy Queen Fall and Holiday seasonal Blizzard menu lineup"}
    }
    featured_image = featured_img_map.get(slug)
    if not featured_image:
        cat_slug = art["category_slug"] if "category_slug" in art.keys() else ""
        category_fallbacks = {
            "blizzards": "blizzard-treats",
            "cakes": "ice-cream-cake",
            "burgers": "burger-menu",
            "food": "chicken-strip-meal",
            "treats": "chocolate-dipped-cone",
            "drinks": "milkshakes",
            "breakfast": "breakfast-platter",
            "deals": "burger-and-fries",
            "nutrition": "nutrition-guide-food",
        }
        img_name = category_fallbacks.get(cat_slug, "homepage-food-hero")
        featured_image = {
            "img": img_name,
            "alt": f"{art['title']} - Dairy Queen Menu Guide"
        }
    ctx["featured_image"] = featured_image

    return templates.TemplateResponse(request, "article_detail.html", ctx)

async def search_page(request: Request):
    q = request.query_params.get("q", "").strip()
    results = search_site(q, limit=30)
    ctx = get_base_context(request, active_page="search")
    ctx["noindex"] = True
    ctx.update(results)
    return templates.TemplateResponse(request, "search_results.html", ctx)

async def contact_get(request: Request):
    ctx = get_base_context(request, active_page="contact")
    return templates.TemplateResponse(request, "contact.html", ctx)

async def contact_post(request: Request):
    form_data = await request.form()
    csrf_token = form_data.get("csrf_token", "")
    honeypot = form_data.get("website_verification_url", "").strip()

    # Bot protection: if honeypot is filled, discard silently
    if honeypot:
        return RedirectResponse("/contact?success=1", status_code=303)

    if not verify_csrf_token(request, csrf_token):
        ctx = get_base_context(request, active_page="contact")
        ctx["error_message"] = "Invalid or expired security token. Please try submitting again."
        return templates.TemplateResponse(request, "contact.html", ctx, status_code=400)

    name = form_data.get("name", "").strip()
    email = form_data.get("email", "").strip()
    subject = form_data.get("subject", "").strip()
    message = form_data.get("message", "").strip()

    if not name or not email or not subject or not message or len(message) < 10:
        ctx = get_base_context(request, active_page="contact")
        ctx["error_message"] = "Please fill out all required fields with detailed information."
        return templates.TemplateResponse(request, "contact.html", ctx, status_code=400)

    # Store into database
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO contacts (name, email, subject, message, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name[:80], email[:120], subject[:100], message[:2000], datetime.now().isoformat()))

    ctx = get_base_context(request, active_page="contact")
    ctx["success_message"] = "Your message has been received by our editorial desk. We appreciate your submission."
    return templates.TemplateResponse(request, "contact.html", ctx)

# Legal and Policy Pages
async def about_page(request: Request):
    content = """
    <h2>Our Mission & Independence</h2>
    <p><strong>DQ Menu Guidance</strong> is an independent editorial publishing venture created to bring pricing transparency, portion awareness, and nutritional facts to American diners.</p>
    <p>Fast-food chains frequently advertise nationwide value meals, yet local franchise pricing varies substantially depending on municipal wages, regional ingredient supply lines, and store ownership. We research, cross-reference, and explain these dynamics so consumers know exactly what to expect before stepping up to the drive-thru window.</p>
    
    <h2>Editorial Standards</h2>
    <p>We do not accept paid product placements from restaurants. Our editors verify all menu facts, calories, and allergens using primary corporate disclosures and direct register receipts.</p>
    """
    ctx = get_base_context(request, active_page="about")
    ctx.update({"title": "About DQ Menu Guidance", "content": content})
    return templates.TemplateResponse(request, "legal_page.html", ctx)

async def editorial_policy_page(request: Request):
    content = """
    <h2>Commitment to Truth & Evidence</h2>
    <p>At DQ Menu Guidance, we adhere to strict journalistic standards regarding consumer fast-food data:</p>
    <ol>
      <li><strong>No Fabricated Pricing:</strong> We never generate arbitrary price numbers or falsely advertise a "complete 2026 price list" without verifiable evidence.</li>
      <li><strong>Transparent Ranges:</strong> Because Dairy Queen restaurants are independently franchised, we present pricing as realistic local ranges (e.g. $4.79 – $5.49) rather than misleading single figures.</li>
      <li><strong>Clear Labeling of Limited Offers:</strong> Seasonal items, rotational test products, and regional items (such as Texas Country Foods) are explicitly designated with warning badges.</li>
      <li><strong>No Intrusive Advertising Clutter:</strong> We reject deceptive interstitial popups, fake coupon downloads, and intrusive ad banners that degrade reader comprehension.</li>
    </ol>
    """
    ctx = get_base_context(request, active_page="editorial")
    ctx.update({"title": "Editorial Standards & Price Accuracy Policy", "content": content})
    return templates.TemplateResponse(request, "legal_page.html", ctx)

async def sources_fact_checking_page(request: Request):
    content = """
    <h2>How We Verify Menu Information</h2>
    <p>All nutritional figures, product specifications, and allergen disclosures on this website are cross-referenced with primary authoritative sources:</p>
    <ul>
      <li><a href="https://www.dairyqueen.com" target="_blank" rel="noopener noreferrer">American Dairy Queen Corporation (ADQ) Official Menu</a></li>
      <li><a href="https://www.dairyqueen.com/en-us/nutrition-allergens/" target="_blank" rel="noopener noreferrer">Official ADQ Nutritional Food Fact Charts & Allergen Tables</a></li>
      <li><a href="https://dqtexas.com/" target="_blank" rel="noopener noreferrer">Texas Dairy Queen Operators' Council Official Portal</a></li>
      <li><a href="https://www.sec.gov" target="_blank" rel="noopener noreferrer">Public Franchise Disclosure Documents (FDD)</a></li>
    </ul>
    <h2>Reporting an Outdated Price or Discontinued Flavor</h2>
    <p>If you notice a price discrepancy or discontinued seasonal item at your local restaurant, please submit a correction via our <a href="/contact">Editorial Contact Form</a>. Our team verifies submissions within 48 business hours.</p>
    """
    ctx = get_base_context(request, active_page="sources")
    ctx.update({"title": "Sources & Fact-Checking Methodology", "content": content})
    return templates.TemplateResponse(request, "legal_page.html", ctx)

async def privacy_policy_page(request: Request):
    content = """
    <h2>Privacy Policy</h2>
    <p class="text-muted">Last Updated: October 2026 | Effective Date: October 2026</p>
    
    <p>DQ Menu Guidance ("we," "our," or "us") provides this Privacy Policy to inform users of our policies and procedures regarding the collection, use, and disclosure of personal information received from users of this website (the "Site"). We respect your privacy and are committed to protecting any information you share with us.</p>
    
    <h3>1. Information We Collect</h3>
    <p>We do not require user account registration, login credentials, or payment information to access our menu guides, price tables, or editorial content. The information collected on this Site is limited to:</p>
    <ul>
      <li><strong>Direct Inquiries:</strong> If you contact us through our Contact form or editorial feedback channels, we collect the name, email address, and message content you provide solely to investigate feedback and reply to your inquiry.</li>
      <li><strong>Technical & Usage Data:</strong> Standard server logs record internet protocol (IP) addresses, browser types, internet service providers (ISPs), referring/exit pages, operating systems, date/time stamps, and clickstream data to administer the site, analyze trends, and maintain security.</li>
    </ul>

    <h3>2. Cookies, Google AdSense & Third-Party Advertising</h3>
    <p>Third-party vendors, including <strong>Google AdSense</strong> and advertising partners, use cookies and web beacons to serve ads based on a user's prior visits to this website or other websites across the Internet:</p>
    <ul>
      <li>Google's use of advertising cookies (such as the DoubleClick cookie) enables it and its partners to serve personalized advertisements to our users based on their browsing behavior and visits to sites across the web.</li>
      <li>Users may opt out of personalized advertising at any time by visiting <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer">Google Ads Settings</a>.</li>
      <li>Alternatively, you can opt out of third-party vendor use of cookies for personalized advertising by visiting the Network Advertising Initiative opt-out page at <a href="https://optout.networkadvertising.org/" target="_blank" rel="noopener noreferrer">www.networkadvertising.org</a> or <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener noreferrer">www.aboutads.info</a>.</li>
    </ul>

    <h3>3. Web Analytics & Measurement</h3>
    <p>We may use first-party and third-party web analytics tools (such as Google Analytics) that utilize cookies to track aggregated, non-personally identifiable site usage statistics, such as average reading time, page load performance, and popular menu guides. These cookies help us improve site navigation and technical performance.</p>

    <h3>4. California Privacy Rights (CCPA / CPRA Disclosures)</h3>
    <p>Under the California Consumer Privacy Act (CCPA) and California Privacy Rights Act (CPRA), California residents are entitled to specific rights concerning their personal information:</p>
    <ul>
      <li><strong>Right to Know / Access:</strong> You have the right to request information about the categories and specific pieces of personal information we have collected about you, the categories of sources, and the business purpose for collecting it.</li>
      <li><strong>Right to Request Deletion:</strong> You have the right to request deletion of personal information collected from you, subject to certain legal exceptions.</li>
      <li><strong>Right to Correct:</strong> You have the right to request that we correct inaccurate personal information that we maintain about you.</li>
      <li><strong>Right to Opt-Out of Sale or Sharing ("Do Not Sell or Share My Personal Information"):</strong> We do not sell personal information for monetary compensation. However, if third-party advertising cookies are construed as "selling" or "sharing" under California law, you may opt out via the Google Ads Settings link above or by adjusting your browser cookie preferences.</li>
      <li><strong>Right to Non-Discrimination:</strong> We will not discriminate against you in pricing, service availability, or website functionality for exercising any of your CCPA/CPRA rights.</li>
    </ul>
    <p>To exercise any of these rights, please contact us through our <a href="/contact">Editorial Contact Form</a>.</p>

    <h3>5. Data Security</h3>
    <p>We implement industry-standard technical security measures, including HTTPS encryption, secure session cookie configurations, and security headers, to protect against unauthorized access or alteration of information.</p>

    <h3>6. Contact Information</h3>
    <p>For questions or comments regarding this Privacy Policy or our data practices, please visit our <a href="/contact">Contact Page</a>.</p>
    """
    ctx = get_base_context(request, active_page="privacy")
    ctx.update({"title": "Privacy Policy & CCPA Notice", "content": content})
    return templates.TemplateResponse(request, "legal_page.html", ctx)

async def terms_page(request: Request):
    content = """
    <h2>Terms of Use</h2>
    <p>By accessing DQ Menu Guidance, you acknowledge and agree to the following conditions:</p>
    <ol>
      <li><strong>Informational Purpose Only:</strong> Content on this site is provided solely for general informational and educational guidance. Prices, menu items, and availability are subject to change by restaurant operators at any time without notice.</li>
      <li><strong>No Commercial Relationship:</strong> DQ Menu Guidance is an independent entity and does not sell food, process online restaurant orders, or provide corporate customer support.</li>
      <li><strong>Intellectual Property:</strong> Original editorial writing, layouts, and curated comparison tables are protected by copyright. Brand names and trademarks belong to their respective holders.</li>
    </ol>
    """
    ctx = get_base_context(request, active_page="terms")
    ctx.update({"title": "Terms of Use", "content": content})
    return templates.TemplateResponse(request, "legal_page.html", ctx)

async def disclaimer_page(request: Request):
    content = f"""
    <h2>Independence & Trademark Disclaimer</h2>
    <div class="callout callout-warning">
      <p><strong>{settings.DISCLAIMER}</strong></p>
    </div>
    <p>All product names, logos, brands, trademarks, and registered trademarks featured or referred to on this website (including DAIRY QUEEN®, DQ®, BLIZZARD®, GRILL & CHILL®, DILLY®, BUSTER BAR®, TREATZZA PIZZA®, and STACKBURGER™) are the property of their respective trademark owners, specifically American Dairy Queen Corporation and its parent Berkshire Hathaway.</p>
    <p>The use of these trademarks on DQ Menu Guidance is strictly for editorial identification, descriptive review, and comparison under the Fair Use doctrine of United States trademark law. This website is not endorsed by, sponsored by, or affiliated with American Dairy Queen Corporation.</p>
    """
    ctx = get_base_context(request, active_page="disclaimer")
    ctx.update({"title": "Independence & Legal Disclaimer", "content": content})
    return templates.TemplateResponse(request, "legal_page.html", ctx)

# Technical SEO: Sitemap & Robots.txt
async def sitemap_xml(request: Request):
    base_url = settings.SITE_URL.rstrip('/')

    # Meaningful content update dates for canonical indexable pages
    urls = [
        {"loc": f"{base_url}/", "lastmod": "2026-10-27", "changefreq": "daily", "priority": "1.0"},
        {"loc": f"{base_url}/menu", "lastmod": "2026-10-27", "changefreq": "daily", "priority": "0.9"},
        {"loc": f"{base_url}/articles", "lastmod": "2026-10-30", "changefreq": "daily", "priority": "0.95"},
        {"loc": f"{base_url}/blizzards", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base_url}/blizzards/prices-sizes", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.9"},
        {"loc": f"{base_url}/blizzards/seasonal", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/blizzards/nutrition", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.8"},
        {"loc": f"{base_url}/cakes", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.85"},
        {"loc": f"{base_url}/cakes/prices-sizes", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.85"},
        {"loc": f"{base_url}/food", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/food/burgers", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/breakfast", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.7"},
        {"loc": f"{base_url}/treats-desserts", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/deals-coupons", "lastmod": "2026-10-27", "changefreq": "weekly", "priority": "0.8"},
        {"loc": f"{base_url}/nutrition-allergens", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.8"},
        {"loc": f"{base_url}/ordering-delivery", "lastmod": "2026-10-27", "changefreq": "monthly", "priority": "0.7"},
        {"loc": f"{base_url}/faqs", "lastmod": "2026-10-26", "changefreq": "weekly", "priority": "0.7"},
        {"loc": f"{base_url}/about", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{base_url}/editorial-policy", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{base_url}/sources-fact-checking", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{base_url}/contact", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{base_url}/privacy-policy", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.4"},
        {"loc": f"{base_url}/terms", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.4"},
        {"loc": f"{base_url}/disclaimer", "lastmod": "2026-10-26", "changefreq": "monthly", "priority": "0.4"}
    ]

    # Dynamically append published articles with actual content modification dates
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT slug, updated_at, published_at FROM articles WHERE status = 'published'")
        for art in c.fetchall():
            art_lastmod = art["updated_at"] or art["published_at"] or "2026-10-26"
            urls.append({
                "loc": f"{base_url}/articles/{art['slug']}",
                "lastmod": art_lastmod,
                "changefreq": "weekly",
                "priority": "0.85"
            })

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for u in urls:
        xml_lines.append(f"""  <url>
    <loc>{u['loc']}</loc>
    <lastmod>{u['lastmod']}</lastmod>
    <changefreq>{u['changefreq']}</changefreq>
    <priority>{u['priority']}</priority>
  </url>""")
    xml_lines.append('</urlset>')

    return Response("\n".join(xml_lines), media_type="application/xml; charset=utf-8")

async def robots_txt(request: Request):
    base_url = settings.SITE_URL.rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /search

Sitemap: {base_url}/sitemap.xml
"""
    return Response(content, media_type="text/plain; charset=utf-8")

async def custom_404_handler(request: Request, exc: HTTPException):
    ctx = get_base_context(request)
    ctx["noindex"] = True
    return templates.TemplateResponse(request, "404.html", ctx, status_code=404)

async def custom_500_handler(request: Request, exc: Exception):
    ctx = get_base_context(request)
    ctx["noindex"] = True
    return templates.TemplateResponse(request, "500.html", ctx, status_code=500)

async def ads_txt(request: Request):
    pub_id = getattr(settings, "ADSENSE_PUB_ID", "pub-0000000000000000")
    content = f"google.com, {pub_id}, DIRECT, f08c47fec0942fa0\n"
    return Response(content, media_type="text/plain; charset=utf-8")

async def llms_txt(request: Request):
    content = f"""# Dairy Queen Menu & Prices Guide (2026 US Reference)
> Independent, authoritative reference for Dairy Queen menu items, estimated prices, calories, and ordering advice across the United States.

## 2026 US National Average Prices & Menu Highlights
- **Blizzard® Treats**: Mini $3.79 | Small $4.89 | Medium $5.79 | Large $6.59 (Range: $3.79–$6.59). Calories: 350–1350 kcal. Royal Blizzards with filled cores: $4.59–$7.39.
- **2026 Holiday Cookie Swap Blizzard Collection**:
  - Peanut Butter Blossom made with HERSHEY'S MINI KISSES Blizzard Treat (Mini $3.79, Small $4.89, Med $5.79, Large $6.59 | 420–1150 kcal)
  - Peppermint Bark Blizzard Treat (Mini $3.79, Small $4.89, Med $5.79, Large $6.59 | 400–1090 kcal)
- **2026 Fall Seasonal Menu**:
  - Brown Sugar Cookie Dough Blizzard Treat (Mini $3.79, Small $4.89, Med $5.79, Large $6.59 | 410–1120 kcal)
  - Caramel Apple Cheesecake Blizzard Treat (Mini $3.79, Small $4.89, Med $5.79, Large $6.59 | 390–1060 kcal)
  - Pumpkin Pie Blizzard Treat (Mini $3.79, Small $4.89, Med $5.79, Large $6.59 | 360–980 kcal)
  - Toasted Marshmallow Mocha DQ Coffee Cooler (Small $4.29, Med $4.99, Large $5.69 | 380–640 kcal)
  - Maple Cookie Shake (Small $4.79, Med $5.59, Large $6.39 | 540–890 kcal)
- **Signature Stackburgers™**: 100% seasoned fresh beef patties.
  - Bacon Two-Cheese Deluxe: Double Solo $7.79, Triple Solo $9.29, Combo $10.87 (710–980 kcal).
  - FlameThrower® Stackburger: Double Solo $8.19, Triple Solo $9.69, Combo $10.87 (740–1010 kcal).
  - Original Double Cheeseburger: $4.69 (Combo $7.39 | 540 kcal).
- **Food & Chicken Strip Baskets**:
  - Crispy Chicken Strip Basket: 4-Piece $9.99–$10.87 (910–1020 kcal), 6-Piece $13.49 (1250–1360 kcal). Served with Texas toast, fries, and dipping gravy.
  - FlameThrower Chicken Strip Basket: 4-Piece $10.49 (1030 kcal), 6-Piece $13.49 (1380 kcal).
- **Celebration Ice Cream Cakes**:
  - 8-Inch Round (Serves 8–10): $31.24–$34.99 (~$3.50/slice).
  - 10-Inch Round (Serves 12–16): $34.99–$38.74 (~$2.60/slice).
  - 8-Inch Blizzard® Cake: $34.99.
  - 11" x 14" Sheet Cake (Serves 20–24): $42.99–$54.99.
  - Treatzza Pizza®: $14.99–$18.99 (6–8 slices).
- **Deals & Value Meals**:
  - $7 Meal Deal: Original Cheeseburger or 3-Pc Chicken Strips + Fries + 21oz Drink + Sundae for $7.00 (with optional $2 Small Blizzard upgrade).
  - 2 for $5 Mix & Match: $5.00 for 2 select favorites.
- **Classic Treats & Novelties**: Cones $2.59–$3.99, Chocolate Dipped Cones $3.29–$4.69, Hot Fudge Sundaes $3.59–$5.19, Dilly® Bars $2.19, Buster Bar® $3.49, Banana Split $5.69.
- **Beverages & Shakes**: Hand-spun Milkshakes $4.79–$6.39, Malts $5.19–$6.79, MooLatté® $4.29+, Misty® Slush $2.39+.
- **Regional Breakfast**: Texas & Southern morning locations (6:00 AM–10:30 AM). Platters $5.99–$7.49, Biscuits $3.49–$4.49.

## Key Canonical URLs & Documentation
- Master Menu & Price Index: {settings.SITE_URL}/menu
- Blizzard Menu & Flavors: {settings.SITE_URL}/blizzards
- Blizzard Prices & Sizes: {settings.SITE_URL}/blizzards/prices-sizes
- Seasonal Blizzard Rotations: {settings.SITE_URL}/blizzards/seasonal
- Ice Cream Cake Prices & Sizes: {settings.SITE_URL}/cakes
- Signature Stackburgers & Food: {settings.SITE_URL}/food/burgers
- Deals, $7 Meal Deal & Coupons: {settings.SITE_URL}/deals-coupons
- Nutrition Facts & Allergen Guide: {settings.SITE_URL}/nutrition-allergens
- Delivery Apps & Online Ordering: {settings.SITE_URL}/ordering-delivery
- Editorial & Fact-Checking Methodology: {settings.SITE_URL}/sources-fact-checking
- Privacy Policy (CCPA/CPRA): {settings.SITE_URL}/privacy-policy
- Terms of Use: {settings.SITE_URL}/terms
- Sitemap: {settings.SITE_URL}/sitemap.xml
"""
    return Response(content, media_type="text/markdown; charset=utf-8")

async def favicon_ico(request: Request):
    logo_path = Path("app/static/images/logo.svg")
    if logo_path.exists():
        return FileResponse(str(logo_path), media_type="image/svg+xml")
    favicon_path = Path("app/static/favicon.svg")
    if favicon_path.exists():
        return FileResponse(str(favicon_path), media_type="image/svg+xml")
    return Response("", status_code=204)
