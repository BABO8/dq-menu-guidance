# DQ Menu Guidance (US Dairy Queen Reference)

**DQ Menu Guidance** is an independent, editorial-grade web application and technical SEO content hub designed for consumers in the United States researching Dairy Queen menu items, verified price ranges, Blizzard® treat sizes, ice cream celebration cakes, nutrition facts, and value deals.

---

## 1. Architecture & Technology Stack

| Layer | Technology | Function |
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3.14 + Starlette / FastAPI + Uvicorn** | High-performance asynchronous ASGI server-side rendered engine. Instant TTFB, 100% crawlable by Googlebot without client hydration delays. |
| **Templates & UI** | **Jinja2 + Editorial Design System + Vanilla JS** | Warm cream (`#FDFBF7`), deep navy (`#0F172A`), coral (`#E11D48`) and amber accents. Responsive typography, accessible focus rings (WCAG 2.2 AA), zero layout shifts. |
| **Database** | **SQLite (WAL Mode) with Foreign Keys** | Zero-daemon relational storage with transactions, indexed slug lookups, and prepared parameter binding. |
| **Search Engine** | **Sub-millisecond Tokenized Search (`app/search.py`)** | Live autocomplete endpoint (`/api/search/suggestions`), debounced client search, full-text ranking by title, category, and ingredient relevance. |
| **Authentication & Security** | **PBKDF2-HMAC-SHA256 + Signed Sessions + CSRF** | 600,000 hash iterations, cryptographic salts, HttpOnly session cookies, anti-CSRF token verification, bot honeypot, and strict CSP headers. |
| **SEO & Structured Data** | **Dynamic Sitemap, Robots.txt, JSON-LD** | Clean canonical URLs, OpenGraph sharing cards, `Article`, `BreadcrumbList`, `FAQPage`, and `WebSite` schema. |

---

## 2. Quick Local Setup Guide (Windows)

### Prerequisites
- Python 3.10+ installed on your system (Python 3.14 verified)
- Windows PowerShell or Command Prompt

### Step 1: Open PowerShell in Project Directory
```powershell
cd c:\Users\hp\Desktop\website
```

### Step 2: Install Python Dependencies
```powershell
python -m pip install uvicorn starlette jinja2 python-multipart itsdangerous httpx pytest
```

### Step 3: Run Database Setup & Verified Seed Data
The database will automatically initialize on first launch, or you can run the seed script directly:
```powershell
python -m data.seed_data
```

### Step 4: Start the Web Server
```powershell
python run.py
```
You will see:
```text
======================================================================
   MENU PRICE GUIDE - US DAIRY QUEEN EDITORIAL REFERENCE
======================================================================
 * Local URL:       http://localhost:8000/
 * Menu Hub:        http://localhost:8000/menu
 * Blizzard Prices: http://localhost:8000/blizzards/prices-sizes
 * Admin Dashboard: http://localhost:8000/admin
 * Admin Login:     editorial_admin (configured via ADMIN_INITIAL_PASSWORD in .env)
======================================================================
```

---

## 3. Key Website Routes

### Public Consumer Pages
- **Homepage:** `http://localhost:8000/`
- **Master Menu With Prices:** `http://localhost:8000/menu`
- **Blizzard® Flavors & Guide:** `http://localhost:8000/blizzards`
- **Blizzard® Prices & Sizes by Ounce:** `http://localhost:8000/blizzards/prices-sizes`
- **Current & Seasonal Blizzard Tracker:** `http://localhost:8000/blizzards/seasonal`
- **Blizzard® Calories & Nutrition Chart:** `http://localhost:8000/blizzards/nutrition`
- **Ice Cream Cake Menu & Pricing:** `http://localhost:8000/cakes`
- **Grill & Chill Hot Food Menu:** `http://localhost:8000/food`
- **Signature Stackburgers™:** `http://localhost:8000/food/burgers`
- **Regional Breakfast Menu & Hours:** `http://localhost:8000/breakfast`
- **Classic Cones, Sundaes & Dilly® Bars:** `http://localhost:8000/treats-desserts`
- **Nutrition, Calories & Allergen Disclosures:** `http://localhost:8000/nutrition-allergens`
- **Deals, Coupons & $7 Meal Deal:** `http://localhost:8000/deals-coupons`
- **Online Ordering & Delivery Guide:** `http://localhost:8000/ordering-delivery`
- **Frequently Asked Questions:** `http://localhost:8000/faqs`
- **Site Search:** `http://localhost:8000/search?q=blizzard`

### Legal & Editorial Policies
- **About Us:** `http://localhost:8000/about`
- **Editorial Standards:** `http://localhost:8000/editorial-policy`
- **Sources & Fact-Checking:** `http://localhost:8000/sources-fact-checking`
- **Contact Editorial Team:** `http://localhost:8000/contact`
- **Privacy Policy:** `http://localhost:8000/privacy-policy`
- **Terms of Use:** `http://localhost:8000/terms`
- **Independence Disclaimer:** `http://localhost:8000/disclaimer`

### Technical SEO Endpoints
- **XML Sitemap:** `http://localhost:8000/sitemap.xml`
- **Robots.txt:** `http://localhost:8000/robots.txt`

### Administrative Control Area
- **Admin Login:** `http://localhost:8000/admin/login`
- **Default Username:** `editorial_admin`
- **Admin Password:** Configured via `ADMIN_INITIAL_PASSWORD` in `.env` (or environment variable during initial seed)
- **Dashboard Overview:** `http://localhost:8000/admin/dashboard`
- **Article Manager:** `http://localhost:8000/admin/articles`
- **Menu Item Manager:** `http://localhost:8000/admin/menu-items`
- **Fact-Checking Queue:** `http://localhost:8000/admin/fact-check`
- **Keyword Map & CSV Exporter:** `http://localhost:8000/admin/keyword-map`
- **Contact Submissions Inbox:** `http://localhost:8000/admin/contacts`

---

## 4. Keyword Research & SEO Architecture

All 501 keywords supplied from the research workbook have been categorized into `keyword_map.csv` following strict search intent rules:
1. **US Priority:** International and Canadian regional terms (`ontario`, `ca menu`) are categorized as `Excluded/International` to focus search rank on the US market.
2. **Intent Grouping:** Variants such as `blizzard size prices`, `blizzard sizes and prices`, `small blizzard price`, and `cost of dq blizzard` are consolidated onto `/blizzards/prices-sizes` rather than splintering authority across thin sub-pages.
3. **Historical Consolidation:** Searches containing outdated years (`2021`, `2022`, `2023`) are routed to canonical pillar guides with clear freshness badges to protect against obsolescence.
4. **Structured Data:** Legitimate JSON-LD schema markup (`Article`, `BreadcrumbList`, `FAQPage`, `WebSite`) is rendered without manipulative fake review stars.

---

## 5. Security & Protection Controls

- **Authentication Guard:** Every administrative URL requires a valid cryptographic HMAC-signed session cookie. Unauthorized visitors attempting to mutate content are rejected and redirected to `/admin/login`.
- **CSRF Defense:** All POST/PUT/DELETE forms embed a signed CSRF token that is verified constant-time on the server.
- **SQL Injection Prevention:** All database operations utilize SQLite parameterized bindings (`?`), eliminating raw string interpolation.
- **XSS Sanitization:** Jinja2 contextual auto-escaping is enforced across all templates.
- **Anti-Spam Honeypot:** Contact form submissions feature invisible decoy fields (`website_verification_url`) to silently deflect automated spam bots.
- **Security Headers:**
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy: default-src 'self' ...`

---

## 6. Food Photography & Visual Media Assets

All 10 original, photorealistic food photography assets were generated specifically for DQ Menu Guidance without copyrighted logos, watermarks, or trademarked packaging. They are stored in `app/static/images/` in both next-generation WebP (ultra-fast loading, 85% quality) and lossless PNG fallback:

| Asset Filename | Format & Size | Featured Usage | Visual Description |
| :--- | :--- | :--- | :--- |
| `homepage-food-hero.webp` | WebP (147 KB) / PNG (1.5 MB) | Homepage Hero 16:9 Banner | Editorial assortment of soft-serve dessert, thick milkshake, double cheeseburger, and crispy chicken tenders with country gravy. |
| `blizzard-treats.webp` | WebP (59 KB) / PNG (1.2 MB) | Blizzard Hub & Category Card | Blended soft-serve dessert in a clear glass with visible chocolate sandwich cookie crumbles and candy chunks. |
| `ice-cream-cake.webp` | WebP (97 KB) / PNG (1.4 MB) | Cake Guide & Category Card | Decorated round celebration ice cream cake on a ceramic stand with a slice showing dark fudge and chocolate crunch ribbon. |
| `burger-menu.webp` | WebP (169 KB) / PNG (1.7 MB) | Burgers Hub & Category Card | Juicy double cheeseburger with melted sharp American cheese, fresh green lettuce, red tomato, and toasted brioche bun. |
| `chicken-strip-meal.webp` | WebP (140 KB) / PNG (1.6 MB) | Food Hub & Category Card | Four golden crispy chicken tenders with southern pepper gravy, golden fries, and buttered grilled Texas toast. |
| `soft-serve-cone.webp` | WebP (29 KB) / PNG (1.0 MB) | Treats Hub & Category Card | Classic vanilla soft-serve cone with signature curl top standing upright in a minimalist stand. |
| `milkshakes.webp` | WebP (90 KB) / PNG (1.4 MB) | Treats & Drinks Showcase | Retro-modern tall soda-fountain glass of thick chocolate milkshake with whipped cream and chocolate syrup drizzle. |
| `ice-cream-sundae.webp` | WebP (124 KB) / PNG (1.5 MB) | Treats & Novelties Showcase | Vintage tulip glass with vanilla soft serve, warm glossy hot fudge sauce, whipped cream, and a red cherry. |
| `breakfast-platter.webp` | WebP (146 KB) / PNG (1.6 MB) | Breakfast Menu Guide | Hearty diner breakfast platter with sunny-side up eggs, hash browns, bacon strips, and buttermilk biscuits with sausage gravy. |
| `nutrition-guide-food.webp` | WebP (189 KB) / PNG (1.7 MB) | Nutrition & Allergens Hub | Editorial flat-lay of fresh mixed berries, sliced strawberries, Greek yogurt, grilled chicken, and garden salad. |

---

## 7. Automated Testing & Verification

A comprehensive automated test suite is provided in `tests/test_all.py` and `tests/test_admin_auth.py`.

To run all automated tests:
```powershell
python -m pytest tests/ -v
```
Expected output:
```text
tests/test_admin_auth.py::test_password_hashing PASSED
tests/test_admin_auth.py::test_admin_login_flow PASSED
tests/test_admin_auth.py::test_unauthorized_post_rejected PASSED
tests/test_admin_auth.py::test_unauthorized_menu_item_create_rejected PASSED
tests/test_all.py::test_homepage_loads PASSED
tests/test_all.py::test_security_headers_present PASSED
tests/test_all.py::test_menu_hub_and_filtering PASSED
tests/test_all.py::test_blizzard_subpages PASSED
tests/test_all.py::test_cakes_and_food_pages PASSED
tests/test_all.py::test_breakfast_page PASSED
tests/test_all.py::test_deals_and_delivery_pages PASSED
tests/test_all.py::test_article_detail_and_structured_data PASSED
tests/test_all.py::test_unknown_url_returns_404 PASSED
tests/test_all.py::test_sitemap_and_robots PASSED
tests/test_all.py::test_api_search_suggestions PASSED
tests/test_all.py::test_site_search_page PASSED
tests/test_all.py::test_admin_routes_require_authentication PASSED
tests/test_all.py::test_contact_form_spam_honeypot PASSED
tests/test_all.py::test_food_images_load_and_have_correct_mimetype PASSED
tests/test_all.py::test_homepage_food_hero_and_cards_render PASSED
tests/test_all.py::test_category_pages_render_images PASSED
tests/test_all.py::test_article_page_renders_featured_image PASSED

======================== 22 passed in 4.64s ========================
```

---

## 8. Database Backup & Restore Guide

### Backing Up SQLite Database
SQLite supports hot backups using the command line or Python:
```powershell
# Create a timestamped backup copy
$backupDate = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item data\dq_guide.db "data\dq_guide_backup_$backupDate.db"
```

### Restoring SQLite Database
```powershell
# Stop the server, then restore:
Copy-Item "data\dq_guide_backup_20261026_120000.db" data\dq_guide.db
```

---

## 8. Production Deployment Instructions

### Option A: Standard Linux VPS (Ubuntu/Debian with Gunicorn & Nginx)
1. Clone the repository into `/var/www/menupriceguide`.
2. Create Python virtualenv: `python3 -m venv venv && source venv/bin/activate`.
3. Install requirements: `pip install uvicorn gunicorn starlette jinja2 python-multipart itsdangerous httpx`.
4. Copy `.env.example` to `.env` and set `DEBUG=False` and a secure random `SECRET_KEY`.
5. Run using Systemd service:
   ```ini
   [Unit]
   Description=DQ Menu Guidance ASGI
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/menupriceguide
   ExecStart=/var/www/menupriceguide/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app -b 127.0.0.1:8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
6. Configure Nginx with SSL (Let's Encrypt Certbot) reverse-proxying `proxy_pass http://127.0.0.1:8000;`.

### Option B: Cloud Containers (Docker / Render / Railway / Fly.io)
Add a standard `Dockerfile`:
```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir uvicorn starlette jinja2 python-multipart itsdangerous httpx pytest
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 9. Content Verification & Editorial Checklist

Before publishing major menu updates:
- [ ] Confirm item is currently offered in US stores via [dairyqueen.com](https://www.dairyqueen.com).
- [ ] Record calorie figures directly from official ADQ Nutrition Food Fact charts.
- [ ] Set price ranges reflecting regional minimum wage disparities (e.g. \$4.29 – \$5.49).
- [ ] Check if the item is limited-time or seasonal and assign the `Seasonal / Limited Time` badge.
- [ ] Verify that hot food items note "Grill & Chill / Brazier exclusive" availability.
- [ ] Check `/admin/fact-check` monthly to review any items pending update.
