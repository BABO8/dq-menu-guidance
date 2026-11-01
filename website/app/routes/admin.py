import csv
import json
from datetime import datetime
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response, FileResponse
from starlette.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from app.config import settings
from app.database import get_db
from app.auth import (
    verify_password, create_admin_session, get_current_admin,
    generate_csrf_token, verify_csrf_token,
    check_login_rate_limit, record_failed_login, clear_failed_logins
)

def safe_float(val, default=None):
    if val is None or str(val).strip() == "":
        return default
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return default

def safe_int(val, default=None):
    if val is None or str(val).strip() == "":
        return default
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return default

templates = Jinja2Templates(directory="app/templates")

def require_admin(request: Request):
    admin = get_current_admin(request)
    if not admin:
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    return admin

def admin_context(request: Request, user: dict, extra: dict = None) -> dict:
    ctx = {
        "request": request,
        "settings": settings,
        "user": user,
        "noindex": True,
        "csrf_token": generate_csrf_token(request)
    }
    if extra:
        ctx.update(extra)
    return ctx

# 1. Login & Logout
async def admin_login_get(request: Request):
    if get_current_admin(request):
        return RedirectResponse("/admin/dashboard", status_code=303)
    ctx = {
        "request": request,
        "settings": settings,
        "noindex": True,
        "csrf_token": generate_csrf_token(request),
        "error": None
    }
    return templates.TemplateResponse(request, "admin/login.html", ctx)

async def admin_login_post(request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, retry_after = check_login_rate_limit(client_ip)
    if not allowed:
        ctx = {
            "request": request,
            "settings": settings,
            "noindex": True,
            "csrf_token": generate_csrf_token(request),
            "error": f"Too many failed login attempts. Please wait {retry_after} seconds before trying again."
        }
        return templates.TemplateResponse(request, "admin/login.html", ctx, status_code=429)

    form = await request.form()
    csrf_token = form.get("csrf_token", "")
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()

    if not verify_csrf_token(request, csrf_token):
        ctx = {"request": request, "settings": settings, "noindex": True, "csrf_token": generate_csrf_token(request), "error": "Invalid CSRF security token."}
        return templates.TemplateResponse(request, "admin/login.html", ctx, status_code=400)

    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM admin_users WHERE username = ?", (username,))
        user_row = c.fetchone()

    if not user_row or not verify_password(password, user_row["password_hash"]):
        record_failed_login(client_ip)
        ctx = {"request": request, "settings": settings, "noindex": True, "csrf_token": generate_csrf_token(request), "error": "Invalid username or password."}
        return templates.TemplateResponse(request, "admin/login.html", ctx, status_code=401)

    # Success: reset failed attempt counter and update last login
    clear_failed_logins(client_ip)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("UPDATE admin_users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user_row["id"]))

    token = create_admin_session(user_row["username"], role=user_row["role"])
    response = RedirectResponse("/admin/dashboard", status_code=303)
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        max_age=settings.ADMIN_SESSION_EXPIRY_HOURS * 3600,
        path="/"
    )
    return response

async def admin_logout(request: Request):
    response = RedirectResponse("/admin/login", status_code=303)
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
    return response

# 2. Dashboard
async def admin_dashboard(request: Request):
    user = require_admin(request)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT count(*) as count FROM articles")
        art_count = c.fetchone()["count"]
        c.execute("SELECT count(*) as count FROM menu_items WHERE is_active = 1")
        menu_count = c.fetchone()["count"]
        c.execute("SELECT count(*) as count FROM menu_items WHERE verification_status != 'Verified Official'")
        unverified_count = c.fetchone()["count"]
        c.execute("SELECT count(*) as count FROM contacts WHERE status = 'new'")
        contacts_count = c.fetchone()["count"]

        c.execute("""
            SELECT a.*, c.name as category_name 
            FROM articles a 
            LEFT JOIN categories c ON a.category_id = c.id 
            ORDER BY a.id DESC LIMIT 5
        """)
        recent_articles = c.fetchall()

    ctx = admin_context(request, user, {
        "counts": {
            "articles": art_count,
            "menu_items": menu_count,
            "unverified": unverified_count,
            "contacts": contacts_count
        },
        "recent_articles": recent_articles
    })
    return templates.TemplateResponse(request, "admin/dashboard.html", ctx)

# 3. Articles Management
async def admin_articles_list(request: Request):
    user = require_admin(request)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT a.*, c.name as category_name 
            FROM articles a 
            LEFT JOIN categories c ON a.category_id = c.id 
            ORDER BY a.id DESC
        """)
        articles = c.fetchall()

    ctx = admin_context(request, user, {"articles": articles})
    return templates.TemplateResponse(request, "admin/articles_list.html", ctx)

async def admin_article_new_get(request: Request):
    user = require_admin(request)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY name ASC")
        categories = c.fetchall()

    ctx = admin_context(request, user, {"article": None, "categories": categories})
    return templates.TemplateResponse(request, "admin/article_edit.html", ctx)

async def admin_article_new_post(request: Request):
    user = require_admin(request)
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    title = form.get("title", "").strip()
    slug = form.get("slug", "").strip()
    category_id = form.get("category_id") or None
    meta_title = form.get("meta_title", "").strip() or title
    meta_description = form.get("meta_description", "").strip()
    canonical_url = form.get("canonical_url", "").strip()
    summary = form.get("summary", "").strip()
    content = form.get("content", "").strip()
    status = form.get("status", "published")
    is_cornerstone = 1 if form.get("is_cornerstone") else 0
    author = form.get("author", "").strip() or "DQ Menu Guidance Editorial Staff"
    review_status = form.get("review_status", "verified")
    sources_json = form.get("sources_json", "[]").strip()

    now = datetime.now().strftime("%Y-%m-%d")

    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO articles (
                title, slug, meta_title, meta_description, canonical_url,
                summary, content, category_id, status, is_cornerstone,
                author, published_at, updated_at, sources_json, review_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, slug, meta_title, meta_description, canonical_url,
            summary, content, category_id, status, is_cornerstone,
            author, now, now, sources_json, review_status
        ))

    return RedirectResponse("/admin/articles", status_code=303)

async def admin_article_edit_get(request: Request):
    user = require_admin(request)
    art_id = request.path_params.get("id")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM articles WHERE id = ?", (art_id,))
        art = c.fetchone()
        c.execute("SELECT * FROM categories ORDER BY name ASC")
        categories = c.fetchall()

    if not art:
        raise HTTPException(status_code=404, detail="Article not found")

    ctx = admin_context(request, user, {"article": art, "categories": categories})
    return templates.TemplateResponse(request, "admin/article_edit.html", ctx)

async def admin_article_edit_post(request: Request):
    user = require_admin(request)
    art_id = request.path_params.get("id")
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    title = form.get("title", "").strip()
    slug = form.get("slug", "").strip()
    category_id = form.get("category_id") or None
    meta_title = form.get("meta_title", "").strip() or title
    meta_description = form.get("meta_description", "").strip()
    canonical_url = form.get("canonical_url", "").strip()
    summary = form.get("summary", "").strip()
    content = form.get("content", "").strip()
    status = form.get("status", "published")
    is_cornerstone = 1 if form.get("is_cornerstone") else 0
    author = form.get("author", "").strip() or "DQ Menu Guidance Editorial Staff"
    review_status = form.get("review_status", "verified")
    sources_json = form.get("sources_json", "[]").strip()

    now = datetime.now().strftime("%Y-%m-%d")

    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE articles SET
                title = ?, slug = ?, meta_title = ?, meta_description = ?, canonical_url = ?,
                summary = ?, content = ?, category_id = ?, status = ?, is_cornerstone = ?,
                author = ?, updated_at = ?, sources_json = ?, review_status = ?
            WHERE id = ?
        """, (
            title, slug, meta_title, meta_description, canonical_url,
            summary, content, category_id, status, is_cornerstone,
            author, now, sources_json, review_status, art_id
        ))

    return RedirectResponse("/admin/articles", status_code=303)

async def admin_article_delete_post(request: Request):
    user = require_admin(request)
    art_id = request.path_params.get("id")
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM articles WHERE id = ?", (art_id,))

    return RedirectResponse("/admin/articles", status_code=303)

# 4. Menu Items Management
async def admin_menu_items_list(request: Request):
    user = require_admin(request)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT m.*, c.name as category_name 
            FROM menu_items m 
            LEFT JOIN categories c ON m.category_id = c.id 
            ORDER BY c.display_order ASC, m.id ASC
        """)
        items = c.fetchall()

    ctx = admin_context(request, user, {"menu_items": items})
    return templates.TemplateResponse(request, "admin/menu_items_list.html", ctx)

async def admin_menu_item_new_get(request: Request):
    user = require_admin(request)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories ORDER BY name ASC")
        categories = c.fetchall()

    ctx = admin_context(request, user, {"item": None, "categories": categories})
    return templates.TemplateResponse(request, "admin/menu_item_edit.html", ctx)

async def admin_menu_item_new_post(request: Request):
    user = require_admin(request)
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    name = form.get("name", "").strip()
    slug = form.get("slug", "").strip()
    category_id = form.get("category_id") or None
    description = form.get("description", "").strip()
    sizes_available = form.get("sizes_available", "").strip()
    price_min = safe_float(form.get("price_min"))
    price_max = safe_float(form.get("price_max"))
    price_formatted = form.get("price_formatted", "").strip()
    calories = form.get("calories", "").strip()
    allergens = form.get("allergens", "").strip()
    is_seasonal = 1 if form.get("is_seasonal") else 0
    verification_status = form.get("verification_status", "Location-Dependent Range")
    nutrition_verified = form.get("nutrition_verified", "Official ADQ Disclosures").strip()
    price_verification = form.get("price_verification", "Estimated Franchise Range").strip()
    promotion_status = form.get("promotion_status", "standard").strip()
    effective_start_date = form.get("effective_start_date", "").strip() or None
    effective_end_date = form.get("effective_end_date", "").strip() or None
    source_title = form.get("source_title", "Official American Dairy Queen Corporation").strip()
    last_verified = form.get("last_verified", "").strip() or datetime.now().strftime("%Y-%m")
    source_url = form.get("source_url", "").strip()
    notes = form.get("notes", "").strip()

    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO menu_items (
                category_id, name, slug, description, sizes_available,
                price_min, price_max, price_formatted, calories, allergens,
                is_seasonal, is_active, verification_status,
                nutrition_verified, price_verification, promotion_status,
                effective_start_date, effective_end_date, source_title,
                last_verified, source_url, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            category_id, name, slug, description, sizes_available,
            price_min, price_max, price_formatted, calories, allergens,
            is_seasonal, verification_status,
            nutrition_verified, price_verification, promotion_status,
            effective_start_date, effective_end_date, source_title,
            last_verified, source_url, notes
        ))

    return RedirectResponse("/admin/menu-items", status_code=303)

async def admin_menu_item_edit_get(request: Request):
    user = require_admin(request)
    item_id = request.path_params.get("id")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))
        item = c.fetchone()
        c.execute("SELECT * FROM categories ORDER BY name ASC")
        categories = c.fetchall()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    ctx = admin_context(request, user, {"item": item, "categories": categories})
    return templates.TemplateResponse(request, "admin/menu_item_edit.html", ctx)

async def admin_menu_item_edit_post(request: Request):
    user = require_admin(request)
    item_id = request.path_params.get("id")
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    name = form.get("name", "").strip()
    slug = form.get("slug", "").strip()
    category_id = form.get("category_id") or None
    description = form.get("description", "").strip()
    sizes_available = form.get("sizes_available", "").strip()
    price_min = safe_float(form.get("price_min"))
    price_max = safe_float(form.get("price_max"))
    price_formatted = form.get("price_formatted", "").strip()
    calories = form.get("calories", "").strip()
    allergens = form.get("allergens", "").strip()
    is_seasonal = 1 if form.get("is_seasonal") else 0
    verification_status = form.get("verification_status", "Location-Dependent Range")
    nutrition_verified = form.get("nutrition_verified", "Official ADQ Disclosures").strip()
    price_verification = form.get("price_verification", "Estimated Franchise Range").strip()
    promotion_status = form.get("promotion_status", "standard").strip()
    effective_start_date = form.get("effective_start_date", "").strip() or None
    effective_end_date = form.get("effective_end_date", "").strip() or None
    source_title = form.get("source_title", "Official American Dairy Queen Corporation").strip()
    last_verified = form.get("last_verified", "").strip() or datetime.now().strftime("%Y-%m")
    source_url = form.get("source_url", "").strip()
    notes = form.get("notes", "").strip()

    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE menu_items SET
                category_id = ?, name = ?, slug = ?, description = ?, sizes_available = ?,
                price_min = ?, price_max = ?, price_formatted = ?, calories = ?, allergens = ?,
                is_seasonal = ?, verification_status = ?,
                nutrition_verified = ?, price_verification = ?, promotion_status = ?,
                effective_start_date = ?, effective_end_date = ?, source_title = ?,
                last_verified = ?, source_url = ?, notes = ?
            WHERE id = ?
        """, (
            category_id, name, slug, description, sizes_available,
            price_min, price_max, price_formatted, calories, allergens,
            is_seasonal, verification_status,
            nutrition_verified, price_verification, promotion_status,
            effective_start_date, effective_end_date, source_title,
            last_verified, source_url, notes, item_id
        ))

    return RedirectResponse("/admin/menu-items", status_code=303)

async def admin_menu_item_delete_post(request: Request):
    user = require_admin(request)
    item_id = request.path_params.get("id")
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))

    return RedirectResponse("/admin/menu-items", status_code=303)

# 5. Fact Check Queue
async def admin_fact_check_queue(request: Request):
    user = require_admin(request)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT m.*, c.name as category_name 
            FROM menu_items m 
            LEFT JOIN categories c ON m.category_id = c.id 
            ORDER BY m.category_id ASC, m.id ASC
        """)
        items = c.fetchall()

    ctx = admin_context(request, user, {"items": items})
    return templates.TemplateResponse(request, "admin/fact_check.html", ctx)

async def admin_fact_check_verify(request: Request):
    user = require_admin(request)
    item_id = request.path_params.get("id")
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    today_str = datetime.now().strftime("%Y-%m")
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE menu_items 
            SET last_verified = ?,
                nutrition_verified = 'Official ADQ Disclosures',
                price_verification = 'Verified Franchise Estimate'
            WHERE id = ?
        """, (today_str, item_id))

    return RedirectResponse("/admin/fact-check", status_code=303)

# 6. Keyword Map Viewer & Downloader
async def admin_keyword_map(request: Request):
    user = require_admin(request)
    csv_file = settings.DATABASE_PATH.parent.parent / "keyword_map.csv"
    keywords = []
    if csv_file.exists():
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            keywords = list(reader)

    ctx = admin_context(request, user, {"keywords": keywords})
    return templates.TemplateResponse(request, "admin/keyword_map.html", ctx)

async def admin_keyword_map_download(request: Request):
    user = require_admin(request)
    csv_file = settings.DATABASE_PATH.parent.parent / "keyword_map.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="Keyword map file not found")
    return FileResponse(
        path=str(csv_file),
        filename="dairy_queen_keyword_map.csv",
        media_type="text/csv"
    )

# 7. Contacts Inbox
async def admin_contacts_list(request: Request):
    user = require_admin(request)
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM contacts ORDER BY id DESC")
        contacts = c.fetchall()

    ctx = admin_context(request, user, {"contacts": contacts})
    return templates.TemplateResponse(request, "admin/contacts_list.html", ctx)

async def admin_contact_delete_post(request: Request):
    user = require_admin(request)
    contact_id = request.path_params.get("id")
    form = await request.form()
    if not verify_csrf_token(request, form.get("csrf_token", "")):
        raise HTTPException(status_code=400, detail="Invalid CSRF token")

    with get_db() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))

    return RedirectResponse("/admin/contacts", status_code=303)
