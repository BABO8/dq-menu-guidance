import pytest
import xml.etree.ElementTree as ET
from starlette.testclient import TestClient
from app.main import app
from app.config import Settings, settings

@pytest.fixture
def client():
    return TestClient(app)

def test_homepage_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Dairy Queen Menu &amp; Prices Guide" in res.text or "Dairy Queen Menu & Prices Guide" in res.text
    assert "DQ Menu Guidance is an independent" in res.text
    # Verify noindex is NOT on public homepage
    assert "noindex" not in res.text
    # Verify canonical is present
    assert '<link rel="canonical" href="http://localhost:8000/">' in res.text

def test_security_headers_present(client):
    res = client.get("/")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Strict-Transport-Security" in res.headers
    assert "Content-Security-Policy" in res.headers
    assert "Permissions-Policy" in res.headers

def test_menu_hub_and_filtering(client):
    res = client.get("/menu")
    assert res.status_code == 200
    assert "Master Menu With Prices" in res.text
    assert "OREO® Cookie Blizzard" in res.text

    # Test category filter
    res_filtered = client.get("/menu?category=blizzards")
    assert res_filtered.status_code == 200
    assert "OREO® Cookie Blizzard" in res_filtered.text

def test_canonical_urls_strip_query_params(client):
    # Visiting /menu with search query parameters must canonicalize to clean /menu
    res = client.get("/menu?category=blizzards&search=oreo&utm_source=test")
    assert res.status_code == 200
    assert '<link rel="canonical" href="http://localhost:8000/menu">' in res.text
    assert "category=blizzards" not in res.text.split('rel="canonical"')[1].split('>')[0]

def test_blizzard_subpages(client):
    # Prices and sizes
    res_prices = client.get("/blizzards/prices-sizes")
    assert res_prices.status_code == 200
    assert "Mini Blizzard" in res_prices.text
    assert "Large Blizzard" in res_prices.text
    assert "6 fl oz" in res_prices.text

    # Seasonal tracker
    res_seasonal = client.get("/blizzards/seasonal")
    assert res_seasonal.status_code == 200
    assert "Snickers® Brownie Blizzard" in res_seasonal.text

    # Nutrition chart
    res_nutrition = client.get("/blizzards/nutrition")
    assert res_nutrition.status_code == 200
    assert "1,140 kcal" in res_nutrition.text

def test_cakes_page_and_prices_sizes_page(client):
    # /cakes: Main Styles, Varieties, and Layers overview
    res_cakes = client.get("/cakes")
    assert res_cakes.status_code == 200
    assert "8-Inch Round Cake" in res_cakes.text
    assert "Treatzza Pizza" in res_cakes.text
    assert "Celebration Cake Styles & Varieties" in res_cakes.text

    # /cakes/prices-sizes: Distinct page for price math, slice yields, and cost per serving
    res_cake_prices = client.get("/cakes/prices-sizes")
    assert res_cake_prices.status_code == 200
    assert "2026 Cake Price & Slice Yield Comparison" in res_cake_prices.text
    assert "The 8-Inch vs. 10-Inch Value Math" in res_cake_prices.text
    assert '<link rel="canonical" href="http://localhost:8000/cakes/prices-sizes">' in res_cake_prices.text

def test_food_and_breakfast_pages(client):
    res_food = client.get("/food")
    assert res_food.status_code == 200
    assert "Chicken Strip Baskets" in res_food.text

    res_burg = client.get("/food/burgers")
    assert res_burg.status_code == 200
    assert "Signature Stackburgers" in res_burg.text

    res_brk = client.get("/breakfast")
    assert res_brk.status_code == 200
    assert "Texas" in res_brk.text

def test_deals_and_delivery_pages(client):
    res_deals = client.get("/deals-coupons")
    assert res_deals.status_code == 200
    assert "$7 Meal Deal" in res_deals.text

    res_deliv = client.get("/ordering-delivery")
    assert res_deliv.status_code == 200
    assert "DoorDash" in res_deliv.text

def test_article_detail_and_structured_data(client):
    res = client.get("/articles/dairy-queen-menu-with-prices")
    assert res.status_code == 200
    assert "schema.org" in res.text
    assert '"@type": "Article"' in res.text
    assert "Primary Editorial Sources" in res.text
    # Verify self-referencing canonical URL
    assert '<link rel="canonical" href="http://localhost:8000/articles/dairy-queen-menu-with-prices">' in res.text
    # Verify it does NOT cross-canonicalize to /menu
    assert '<link rel="canonical" href="https://menupriceguide.com/menu">' not in res.text

def test_unknown_url_returns_404_with_noindex(client):
    res = client.get("/nonexistent-invalid-page-12345")
    assert res.status_code == 404
    assert "Page Not Found (404)" in res.text
    assert '<meta name="robots" content="noindex, nofollow">' in res.text

def test_search_page_has_noindex(client):
    res = client.get("/search?q=stackburger")
    assert res.status_code == 200
    assert "Search Results for" in res.text
    assert '<meta name="robots" content="noindex, nofollow">' in res.text

def test_sitemap_xml_validity(client):
    res_sitemap = client.get("/sitemap.xml")
    assert res_sitemap.status_code == 200
    assert "application/xml" in res_sitemap.headers["content-type"]

    # Parse XML to verify well-formed syntax
    root = ET.fromstring(res_sitemap.content)
    assert root.tag.endswith("urlset")

    locs = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert len(locs) >= 20

    # Verify critical routes are included
    assert "http://localhost:8000/" in locs
    assert "http://localhost:8000/menu" in locs
    assert "http://localhost:8000/cakes" in locs
    assert "http://localhost:8000/cakes/prices-sizes" in locs
    assert "http://localhost:8000/blizzards/prices-sizes" in locs
    assert "http://localhost:8000/articles/dairy-queen-menu-with-prices" in locs

    # Non-indexable pages must NOT be in sitemap
    assert not any("/search" in loc for loc in locs)
    assert not any("/admin" in loc for loc in locs)

    # Verify lastmod tags exist and have valid date format YYYY-MM-DD
    lastmods = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")]
    assert len(lastmods) == len(locs)
    for lm in lastmods:
        assert len(lm) == 10
        assert lm.count("-") == 2

def test_robots_txt_format_and_rules(client):
    res_robots = client.get("/robots.txt")
    assert res_robots.status_code == 200
    assert "text/plain" in res_robots.headers["content-type"]
    assert "Disallow: /admin/" in res_robots.text
    assert "Disallow: /api/" in res_robots.text
    assert "Disallow: /search" in res_robots.text
    assert "Sitemap: http://localhost:8000/sitemap.xml" in res_robots.text

def test_csrf_cookie_issuance_and_contact_submission(client):
    # 1. GET /contact receives CSRF cookie
    res_get = client.get("/contact")
    assert res_get.status_code == 200
    assert settings.CSRF_COOKIE_NAME in res_get.cookies

    # 2. Extract CSRF token from form
    csrf_token = res_get.text.split('name="csrf_token" value="')[1].split('"')[0]
    assert len(csrf_token) == 64

    # 3. Submit contact form with valid CSRF token and cookie
    res_post = client.post("/contact", data={
        "csrf_token": csrf_token,
        "name": "Jane Diner",
        "email": "jane@example.com",
        "subject": "Menu Question",
        "message": "Hello, I wanted to verify the mini Blizzard pricing."
    })
    assert res_post.status_code == 200
    assert "Your message has been received" in res_post.text

    # 4. Submit contact form with invalid CSRF token -> Rejected with 400
    res_bad = client.post("/contact", data={
        "csrf_token": "forged_invalid_token",
        "name": "Attacker",
        "email": "hacker@evil.com",
        "subject": "CSRF Attack",
        "message": "Testing CSRF rejection."
    })
    assert res_bad.status_code == 400
    assert "Invalid or expired security token" in res_bad.text

def test_contact_form_spam_honeypot(client):
    # If bot fills honeypot field, it should redirect silently and not store
    res = client.post("/contact", data={
        "csrf_token": "any",
        "website_verification_url": "http://spambot.com",
        "name": "Spammer",
        "email": "spam@spam.com",
        "subject": "Deals",
        "message": "Buy cheap products"
    }, follow_redirects=False)
    assert res.status_code == 303

def test_production_configuration_validation():
    # In production mode, default secret key or localhost SITE_URL must raise RuntimeError
    prod_settings = Settings()
    prod_settings.ENVIRONMENT = "production"
    prod_settings.DEBUG = False
    prod_settings.SECRET_KEY = "dev-insecure-secret-key-change-in-production-dq-2026-v1"
    prod_settings.SITE_URL = "http://localhost:8000"

    with pytest.raises(RuntimeError, match="Insecure or default SECRET_KEY"):
        prod_settings.validate_production_settings()

    # Even with strong key, localhost in SITE_URL must raise
    prod_settings.SECRET_KEY = "a-very-strong-production-secret-key-64-characters-random-string"
    with pytest.raises(RuntimeError, match="SITE_URL cannot point to localhost"):
        prod_settings.validate_production_settings()

    # Valid production settings pass
    prod_settings.SITE_URL = "https://menupriceguide.com"
    prod_settings.validate_production_settings()  # Should not raise

def test_food_images_load_and_have_correct_mimetype(client):
    image_names = [
        "homepage-food-hero", "blizzard-treats", "blizzard-chocolate-cookie",
        "blizzard-peanut-butter", "blizzard-fruit-strawberry", "blizzard-caramel-pecan",
        "ice-cream-cake", "birthday-ice-cream-cake", "chocolate-fudge-cake",
        "burger-menu", "burger-and-fries", "bacon-stackburger",
        "flamethrower-burger", "chicken-strip-meal", "french-fries-sides",
        "soft-serve-cone", "chocolate-dipped-cone", "ice-cream-sundae",
        "milkshakes", "breakfast-platter", "nutrition-guide-food"
    ]
    assert len(image_names) == 21
    from pathlib import Path
    img_dir = Path("app/static/images")
    for name in image_names:
        res = client.get(f"/static/images/{name}.webp")
        assert res.status_code == 200, f"Missing WebP image {name}"
        assert res.headers["content-type"] == "image/webp"

        # Verify optimized file size is strictly under 50 KB
        file_path = img_dir / f"{name}.webp"
        assert file_path.exists()
        assert file_path.stat().st_size < 50 * 1024, f"{name}.webp exceeds 50 KB"

def test_homepage_food_hero_and_cards_render(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "homepage-food-hero.webp" in res.text
    assert "blizzard-treats.webp" in res.text
    assert "ice-cream-cake.webp" in res.text
    assert "burger-menu.webp" in res.text
    assert "chicken-strip-meal.webp" in res.text
    assert "soft-serve-cone.webp" in res.text
    assert "nutrition-guide-food.webp" in res.text
    assert 'loading="lazy"' in res.text
    assert 'fetchpriority="high"' in res.text

def test_category_pages_render_images(client):
    # Blizzard page with flavor gallery
    res_b = client.get("/blizzards")
    assert "blizzard-treats.webp" in res_b.text
    assert "blizzard-chocolate-cookie.webp" in res_b.text
    assert "blizzard-peanut-butter.webp" in res_b.text
    assert "blizzard-fruit-strawberry.webp" in res_b.text
    assert "blizzard-caramel-pecan.webp" in res_b.text

    # Cakes page with celebration styles gallery
    res_c = client.get("/cakes")
    assert "ice-cream-cake.webp" in res_c.text
    assert "birthday-ice-cream-cake.webp" in res_c.text
    assert "chocolate-fudge-cake.webp" in res_c.text

    # Cake Prices page
    res_cp = client.get("/cakes/prices-sizes")
    assert "ice-cream-cake.webp" in res_cp.text

    # Food page with hot food gallery
    res_f = client.get("/food")
    assert "chicken-strip-meal.webp" in res_f.text
    assert "burger-and-fries.webp" in res_f.text
    assert "french-fries-sides.webp" in res_f.text

    # Burgers page with stackburger gallery
    res_burg = client.get("/food/burgers")
    assert "burger-menu.webp" in res_burg.text
    assert "bacon-stackburger.webp" in res_burg.text
    assert "flamethrower-burger.webp" in res_burg.text
    assert "burger-and-fries.webp" in res_burg.text

    # Breakfast page
    res_brk = client.get("/breakfast")
    assert "breakfast-platter.webp" in res_brk.text

    # Treats page with 4 dessert types
    res_t = client.get("/treats-desserts")
    assert "soft-serve-cone.webp" in res_t.text
    assert "chocolate-dipped-cone.webp" in res_t.text
    assert "ice-cream-sundae.webp" in res_t.text
    assert "milkshakes.webp" in res_t.text

    # Nutrition page
    res_n = client.get("/nutrition-allergens")
    assert "nutrition-guide-food.webp" in res_n.text

    # Deals page with $7 meal deal burger and fries photo
    res_d = client.get("/deals-coupons")
    assert "burger-and-fries.webp" in res_d.text

    # Master menu page with hero spread
    res_m = client.get("/menu")
    assert "homepage-food-hero.webp" in res_m.text

    # Seasonal page with caramel pecan blizzard banner
    res_s = client.get("/blizzards/seasonal")
    assert "blizzard-caramel-pecan.webp" in res_s.text

    # Ordering & delivery page with hero spread
    res_o = client.get("/ordering-delivery")
    assert "homepage-food-hero.webp" in res_o.text

def test_article_page_renders_featured_image(client):
    res = client.get("/articles/dairy-queen-blizzard-menu-flavors")
    assert res.status_code == 200
    assert "blizzard-treats.webp" in res.text
    assert "article-lead-img" in res.text

def test_blizzard_calorie_corrections_in_template_and_db(client):
    # Public nutrition template check
    res = client.get("/blizzards/nutrition")
    assert res.status_code == 200
    # Butterfinger official values: 350, 590, 800, 1060 kcal
    assert "350 kcal" in res.text
    assert "590 kcal" in res.text
    assert "800 kcal" in res.text
    assert "1,060 kcal" in res.text
    # Choco Brownie Extreme official values: 420, 740, 980, 1330 kcal
    assert "420 kcal" in res.text
    assert "740 kcal" in res.text
    assert "980 kcal" in res.text
    assert "1,330 kcal" in res.text

    # Database verification
    from app.database import get_db
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT calories, notes FROM menu_items WHERE slug = 'butterfinger-blizzard'")
        bf = c.fetchone()
        assert bf["calories"] == "350 - 1060 kcal"
        assert "350 kcal" in bf["notes"]
        assert "1,060 kcal" in bf["notes"]

        c.execute("SELECT calories, notes FROM menu_items WHERE slug = 'choco-brownie-extreme-blizzard'")
        cbe = c.fetchone()
        assert cbe["calories"] == "420 - 1330 kcal"
        assert "740 kcal" in cbe["notes"]
        assert "1,330 kcal" in cbe["notes"]

def test_meal_deal_promotions_and_scheduling(client):
    # Verify deals & coupons page
    res = client.get("/deals-coupons")
    assert res.status_code == 200
    assert "$7 Meal Deal" in res.text
    assert "Active Deal" in res.text
    assert "Nov 1, 2026" in res.text
    assert "$8 Meal Deal" in res.text
    assert "Nov 2, 2026" in res.text
    assert "$2" in res.text and "Small Blizzard" in res.text

    # Database promotion fields verification
    from app.database import get_db
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT promotion_status, effective_start_date, effective_end_date FROM menu_items WHERE slug = '7-dollar-meal-deal'")
        d7 = c.fetchone()
        assert d7["promotion_status"] == "active"
        assert d7["effective_end_date"] == "2026-11-01"

        c.execute("SELECT promotion_status, effective_start_date, price_formatted FROM menu_items WHERE slug = '8-dollar-meal-deal'")
        d8 = c.fetchone()
        assert d8 is not None
        assert d8["promotion_status"] == "scheduled"
        assert d8["effective_start_date"] == "2026-11-02"
        assert "$8.00" in d8["price_formatted"]

def test_data_integrity_and_unsupported_claims_removal():
    from app.database import get_db
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT name, slug, notes, nutrition_verified, price_verification, source_url FROM menu_items")
        items = c.fetchall()
        assert len(items) >= 32

        for item in items:
            notes = (item["notes"] or "").lower()
            # Verify unsupported marketing claims have been purged
            assert "top-selling" not in notes, f"Unsupported claim in {item['name']}"
            assert "100% of dq locations" not in notes, f"Unsupported claim in {item['name']}"
            assert "standard candy classic on all us menus" not in notes, f"Unsupported claim in {item['name']}"

            # Verify separation of nutrition vs price verification
            assert item["nutrition_verified"] in ("Official ADQ Disclosures", "Regional Franchise Disclosures")
            assert item["price_verification"] is not None and len(item["price_verification"]) > 0

            # Verify official or specific source URL
            assert item["source_url"].startswith("https://www.dairyqueen.com")


def test_production_readiness_overhaul(client):
    # 1. HTML lang & Meta tags
    res = client.get("/")
    assert res.status_code == 200
    assert '<html lang="en-US">' in res.text
    assert '<meta property="og:locale" content="en_US">' in res.text
    assert '<meta name="twitter:card" content="summary_large_image">' in res.text

    # 2. Exact footer disclaimer
    exact_disclaimer = "Disclaimer: This website is an independent informational guide for U.S. consumers and is not affiliated with, associated with, authorized by, endorsed by, or in any way officially connected with American Dairy Queen Corporation (dairyqueen.com). All product names, logos, and brands are property of their respective owners. Prices and menu availability vary by U.S. franchise location and state."
    assert exact_disclaimer in res.text

    # 3. Privacy Policy CCPA & AdSense disclosures
    res_privacy = client.get("/privacy-policy")
    assert res_privacy.status_code == 200
    assert "Google AdSense" in res_privacy.text
    assert "California Consumer Privacy Act (CCPA)" in res_privacy.text
    assert "Do Not Sell or Share My Personal Information" in res_privacy.text

    # 4. JSON-LD Structured Data
    assert '"@type": "FAQPage"' in res.text
    assert '"@type": "Question"' in res.text

    res_menu = client.get("/menu")
    assert res_menu.status_code == 200
    assert '"@type": "Menu"' in res_menu.text
    assert '"@type": "MenuSection"' in res_menu.text
    assert '"@type": "MenuItem"' in res_menu.text
    assert '"@type": "Offer"' in res_menu.text
    assert '"priceCurrency": "USD"' in res_menu.text
    assert '"@type": "NutritionInformation"' in res_menu.text

    # 5. Database 2026 pricing verification
    from app.database import get_db
    with get_db() as conn:
        c = conn.cursor()
        # Verify 2 for $5 Mix & Match
        c.execute("SELECT price_min, price_max FROM menu_items WHERE slug = '2-for-5-mix-match'")
        row = c.fetchone()
        assert row is not None
        assert row["price_min"] == 5.00 and row["price_max"] == 5.00

        # Verify chicken strip basket 4pc and 6pc
        c.execute("SELECT slug, price_min, price_max FROM menu_items WHERE slug IN ('crispy-chicken-strip-basket-4pc', 'crispy-chicken-strip-basket-6pc')")
        baskets = {r["slug"]: r for r in c.fetchall()}
        assert "crispy-chicken-strip-basket-4pc" in baskets
        assert baskets["crispy-chicken-strip-basket-4pc"]["price_min"] == 9.99
        assert "crispy-chicken-strip-basket-6pc" in baskets
        assert baskets["crispy-chicken-strip-basket-6pc"]["price_min"] == 13.49

        # Verify classic treats
        c.execute("SELECT slug, price_min, price_max FROM menu_items WHERE slug IN ('dilly-bar', 'buster-bar', 'banana-split')")
        treats = {r["slug"]: r for r in c.fetchall()}
        assert treats["dilly-bar"]["price_min"] == 2.19
        assert treats["buster-bar"]["price_min"] == 3.49
        assert treats["banana-split"]["price_min"] == 5.69

def test_custom_500_handler():
    import asyncio
    from starlette.requests import Request
    from app.routes.public import custom_500_handler

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/simulated-error",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
    }
    req = Request(scope)
    resp = asyncio.run(custom_500_handler(req, RuntimeError("Simulated internal error")))
    assert resp.status_code == 500
    assert b"500" in resp.body
    assert b"Server Error" in resp.body or b"Internal Server Error" in resp.body
    assert b"noindex" in resp.body

def test_ads_and_llms_and_favicon(client):
    # ads.txt verification
    res_ads = client.get("/ads.txt")
    assert res_ads.status_code == 200
    assert "google.com" in res_ads.text
    assert "DIRECT" in res_ads.text
    assert res_ads.headers["content-type"].startswith("text/plain")

    # llms.txt verification
    res_llms = client.get("/llms.txt")
    assert res_llms.status_code == 200
    assert "Dairy Queen" in res_llms.text
    assert "Peanut Butter Blossom" in res_llms.text
    assert res_llms.headers["content-type"].startswith("text/markdown")

    # favicon.ico verification
    res_fav = client.get("/favicon.ico")
    assert res_fav.status_code == 200
    assert "<svg" in res_fav.text

def test_2026_seasonal_items_in_db():
    from app.database import get_db
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT slug, name, price_formatted, calories, is_seasonal 
            FROM menu_items 
            WHERE slug IN (
                'peanut-butter-blossom-hersheys-blizzard',
                'peppermint-bark-blizzard',
                'brown-sugar-cookie-dough-blizzard',
                'caramel-apple-cheesecake-blizzard',
                'pumpkin-pie-blizzard',
                'toasted-marshmallow-mocha-coffee-cooler',
                'maple-cookie-shake',
                'flamethrower-chicken-strip-basket-4pc',
                'flamethrower-chicken-strip-basket-6pc'
            )
        """)
        rows = {r["slug"]: r for r in c.fetchall()}
        
        # Verify 2026 Holiday Cookie Swap
        assert "peanut-butter-blossom-hersheys-blizzard" in rows
        assert "420 - 1150 kcal" == rows["peanut-butter-blossom-hersheys-blizzard"]["calories"]
        assert rows["peanut-butter-blossom-hersheys-blizzard"]["is_seasonal"] == 1
        
        assert "peppermint-bark-blizzard" in rows
        assert "400 - 1090 kcal" == rows["peppermint-bark-blizzard"]["calories"]

        # Verify 2026 Fall Seasonal Menu
        assert "brown-sugar-cookie-dough-blizzard" in rows
        assert "410 - 1120 kcal" == rows["brown-sugar-cookie-dough-blizzard"]["calories"]

        assert "caramel-apple-cheesecake-blizzard" in rows
        assert "390 - 1060 kcal" == rows["caramel-apple-cheesecake-blizzard"]["calories"]

        assert "pumpkin-pie-blizzard" in rows
        assert "360 - 980 kcal" == rows["pumpkin-pie-blizzard"]["calories"]

        assert "toasted-marshmallow-mocha-coffee-cooler" in rows
        assert "380 - 640 kcal" == rows["toasted-marshmallow-mocha-coffee-cooler"]["calories"]

        assert "maple-cookie-shake" in rows
        assert "540 - 890 kcal" == rows["maple-cookie-shake"]["calories"]

        # Verify FlameThrower chicken strip baskets
        assert "flamethrower-chicken-strip-basket-4pc" in rows
        assert "1030 kcal" == rows["flamethrower-chicken-strip-basket-4pc"]["calories"]

        assert "flamethrower-chicken-strip-basket-6pc" in rows
        assert "1380 kcal" == rows["flamethrower-chicken-strip-basket-6pc"]["calories"]

def test_regional_price_comparisons_and_schemas(client):
    # Regional tables in index, blizzard_prices, cake_prices
    r_idx = client.get("/")
    assert r_idx.status_code == 200
    assert "U.S. Regional Price Comparison" in r_idx.text
    assert "Low-Cost States" in r_idx.text

    r_blizz = client.get("/blizzards/prices-sizes")
    assert r_blizz.status_code == 200
    assert "U.S. Regional Blizzard Price Comparison" in r_blizz.text
    assert "California, New York, Washington" in r_blizz.text

    r_cake = client.get("/cakes/prices-sizes")
    assert r_cake.status_code == 200
    assert "U.S. Regional Ice Cream Cake Price Comparison" in r_cake.text

    # Valid FAQPage JSON-LD schemas
    r_faqs = client.get("/faqs")
    assert r_faqs.status_code == 200
    assert '"@type": "FAQPage"' in r_faqs.text

    r_deals = client.get("/deals-coupons")
    assert r_deals.status_code == 200
    assert '"@type": "FAQPage"' in r_deals.text
    assert "What is included in the Dairy Queen $7 Meal Deal?" in r_deals.text

    r_deliv = client.get("/ordering-delivery")
    assert r_deliv.status_code == 200
    assert '"@type": "FAQPage"' in r_deliv.text
    assert "Can you get Dairy Queen Blizzards delivered?" in r_deliv.text

    # MenuSection schemas
    r_cakes = client.get("/cakes")
    assert r_cakes.status_code == 200
    assert '"@type": "MenuSection"' in r_cakes.text
    assert '"priceCurrency": "USD"' in r_cakes.text

    r_food = client.get("/food")
    assert r_food.status_code == 200
    assert '"@type": "MenuSection"' in r_food.text
    assert '"priceCurrency": "USD"' in r_food.text

    # Legal page compliance module
    r_legal = client.get("/terms")
    assert r_legal.status_code == 200
    assert "DoubleClick Cookie Notice" in r_legal.text
    assert "California Privacy Rights (CCPA / CPRA)" in r_legal.text
    assert "Non-Affiliation Trademark Disclaimer" in r_legal.text


def test_nutrition_and_allergen_overhaul(client):
    # 1. Blizzard Nutrition Page
    r_nut = client.get("/blizzards/nutrition")
    assert r_nut.status_code == 200
    assert "Dairy Queen Blizzard" in r_nut.text and "Calories & Nutrition" in r_nut.text
    assert '"@type": "NutritionInformation"' in r_nut.text
    assert '"@type": "FAQPage"' in r_nut.text
    assert "What is the lowest calorie DQ Blizzard?" in r_nut.text
    assert "How many calories are in a Mini vs. Large Blizzard?" in r_nut.text
    
    # Required 2026 flavors
    flavors = [
        "OREO", "Reese's", "Chocolate Chip Cookie Dough", "Butterfinger",
        "Turtle Pecan Cluster", "Choco Brownie Extreme", "Strawberry Cheesecake",
        "Royal OREO", "Brown Sugar Cookie Dough", "Pumpkin Pie",
        "Caramel Apple Cheesecake", "Peppermint Bark"
    ]
    for flavor in flavors:
        assert flavor in r_nut.text, f"Missing flavor {flavor} in blizzard_nutrition.html"

    # Required nutrient columns
    assert "Total Fat" in r_nut.text
    assert "Carbs / Sugars" in r_nut.text
    assert "Protein" in r_nut.text
    assert "Main Allergens" in r_nut.text

    # 2. Nutrition & Allergens Page
    r_all = client.get("/nutrition-allergens")
    assert r_all.status_code == 200
    assert "Allergen Matrix" in r_all.text
    assert "Gluten-Free & Dairy-Free Options at Dairy Queen (2026)" in r_all.text
    assert "Non-Dairy Dilly" in r_all.text
    assert "Starkiss" in r_all.text
    assert "shared commercial fryers" in r_all.text.lower() or "shared fryers" in r_all.text.lower()
    assert '"@type": "FAQPage"' in r_all.text


def test_article_detail_and_search_zero_results(client):
    # 1. Article Detail Overhaul
    r_art = client.get("/articles/dairy-queen-blizzard-menu-flavors")
    assert r_art.status_code == 200
    assert "U.S. Menu Research Team" in r_art.text
    assert "Fact-Checked & Updated for 2026" in r_art.text
    assert "tocContainer" in r_art.text
    assert "/blizzards/prices-sizes" in r_art.text
    assert "/cakes/prices-sizes" in r_art.text
    assert "/deals-coupons" in r_art.text
    assert "/food" in r_art.text
    assert "/blizzards/nutrition" in r_art.text
    assert '"@type": "Article"' in r_art.text

    # 2. Search Page Zero Results & Quick-Links
    r_srch = client.get("/search?q=xyznonexistentterm99")
    assert r_srch.status_code == 200
    assert "No exact results found" in r_srch.text
    assert "blizzard-treats.webp" in r_srch.text
    assert "burger-menu.webp" in r_srch.text
    assert "chicken-strip-meal.webp" in r_srch.text
    assert "ice-cream-cake.webp" in r_srch.text

    # 3. Interactive Price & Tax Calculator
    r_bp = client.get("/blizzards/prices-sizes")
    assert "dqPriceCalculator" in r_bp.text
    assert "calc-item-select" in r_bp.text
    assert "calc-region-select" in r_bp.text

    r_idx = client.get("/")
    assert "dqPriceCalculator" in r_idx.text


def test_expanded_editorial_articles_collection(client):
    from app.database import get_db
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM articles WHERE status = 'published'")
        count = c.fetchone()[0]
        assert count >= 29, f"Expected at least 29 published articles, found {count}"

    # Verify a selection of the newly generated high-intent SEO articles
    sample_slugs = [
        "dq-summer-blizzard-menu-flavors",
        "dairy-queen-blizzard-of-the-month",
        "dq-signature-stackburgers-guide",
        "dairy-queen-2-for-5-mix-and-match",
        "dairy-queen-7-dollar-meal-deal-upgrade",
        "dairy-queen-chicken-strip-baskets-sauces",
        "dairy-queen-delivery-order-online-guide",
        "dairy-queen-nutrition-calories-guide",
        "dairy-queen-allergy-menu-gluten-free-options",
        "dairy-queen-ice-cream-cake-ordering-prices",
        "dairy-queen-breakfast-biscuits-platters",
        "dairy-queen-grill-and-chill-vs-treat-stores",
        "dairy-queen-royal-blizzard-treats-guide",
        "dairy-queen-classic-novelties-dilly-buster-bars",
        "dairy-queen-secret-menu-blizzards-treats",
        "dairy-queen-shakes-malts-frozen-drinks",
        "dairy-queen-kids-meal-options-pricing",
        "dairy-queen-state-regional-price-disparities",
        "dairy-queen-flamethrower-sauce-menu-items",
        "dairy-queen-app-rewards-free-food-hacks",
        "dairy-queen-dilly-bar-flavors-box-pricing",
        "dairy-queen-fall-winter-seasonal-menu"
    ]

    for slug in sample_slugs:
        res = client.get(f"/articles/{slug}")
        assert res.status_code == 200, f"Article {slug} returned {res.status_code}"
        assert '<meta property="og:type" content="article">' in res.text
        assert "article-lead-img" in res.text
        assert "eeat-trust-bar" in res.text
        assert "link-silo-card" in res.text

    # Verify dedicated /articles and /blog Hub Page
    res_hub = client.get("/articles")
    assert res_hub.status_code == 200
    assert "Dairy Queen Menu Guides & Articles (2026)" in res_hub.text
    assert "All Guides (29)" in res_hub.text
    assert '"@type": "CollectionPage"' in res_hub.text
    assert '"@type": "BreadcrumbList"' in res_hub.text
    assert "articleFilterInput" in res_hub.text

    # Verify /blog alias route
    res_blog = client.get("/blog")
    assert res_blog.status_code == 200
    assert "Dairy Queen Menu Guides & Articles (2026)" in res_blog.text

    # Verify category filtering
    res_cat = client.get("/articles?category=blizzards")
    assert res_cat.status_code == 200
    assert "Summer Blizzard" in res_cat.text

    # Verify homepage and navbar crawl links to /articles
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert '<a href="/articles" class="nav-link' in res_home.text
    assert 'href="/articles"' in res_home.text
    assert "View All 29 Guides" in res_home.text
