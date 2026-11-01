import os
import sys
import secrets
import time
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings
from app.auth import sign_data, verify_signed_data
from app.database import init_db
from data.seed_data import seed_all
from app.routes.public import (
    home_page, menu_hub_page, blizzards_page, blizzard_prices_page,
    seasonal_blizzards_page, blizzard_nutrition_page, cakes_page,
    cake_prices_page, food_page, burgers_page, breakfast_page,
    treats_desserts_page, nutrition_allergens_page, deals_coupons_page,
    ordering_delivery_page, faqs_page, articles_hub_page, article_detail_page, search_page,
    contact_get, contact_post, about_page, editorial_policy_page,
    sources_fact_checking_page, privacy_policy_page, terms_page,
    disclaimer_page, sitemap_xml, robots_txt, ads_txt, llms_txt, favicon_ico, custom_404_handler, custom_500_handler
)
from app.routes.admin import (
    admin_login_get, admin_login_post, admin_logout,
    admin_dashboard, admin_articles_list, admin_article_new_get, admin_article_new_post,
    admin_article_edit_get, admin_article_edit_post, admin_article_delete_post,
    admin_menu_items_list, admin_menu_item_new_get, admin_menu_item_new_post,
    admin_menu_item_edit_get, admin_menu_item_edit_post, admin_menu_item_delete_post,
    admin_fact_check_queue, admin_fact_check_verify,
    admin_keyword_map, admin_keyword_map_download,
    admin_contacts_list, admin_contact_delete_post
)
from app.routes.api import api_search_suggestions, api_search_full

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        return response

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Static files do not require CSRF token handling
        if request.url.path.startswith("/static"):
            return await call_next(request)

        cookie_val = request.cookies.get(settings.CSRF_COOKIE_NAME)
        verified_data = verify_signed_data(cookie_val) if cookie_val else None

        needs_cookie = False
        if verified_data and "csrf" in verified_data:
            raw_csrf = verified_data["csrf"]
        else:
            raw_csrf = secrets.token_hex(32)
            signed_csrf = sign_data({"csrf": raw_csrf, "exp": time.time() + 86400})
            request.state.new_csrf_cookie = signed_csrf
            needs_cookie = True

        request.state.csrf_token = raw_csrf
        response = await call_next(request)

        if needs_cookie and hasattr(request.state, "new_csrf_cookie"):
            response.set_cookie(
                key=settings.CSRF_COOKIE_NAME,
                value=request.state.new_csrf_cookie,
                httponly=True,
                samesite=settings.COOKIE_SAMESITE,
                secure=settings.COOKIE_SECURE,
                max_age=86400,
                path="/"
            )
        return response

routes = [
    # Static files
    Mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static"),

    # Public Routes
    Route("/", home_page, methods=["GET"]),
    Route("/menu", menu_hub_page, methods=["GET"]),
    Route("/blizzards", blizzards_page, methods=["GET"]),
    Route("/blizzards/prices-sizes", blizzard_prices_page, methods=["GET"]),
    Route("/blizzards/seasonal", seasonal_blizzards_page, methods=["GET"]),
    Route("/blizzards/nutrition", blizzard_nutrition_page, methods=["GET"]),
    Route("/cakes", cakes_page, methods=["GET"]),
    Route("/cakes/prices-sizes", cake_prices_page, methods=["GET"]),
    Route("/food", food_page, methods=["GET"]),
    Route("/food/burgers", burgers_page, methods=["GET"]),
    Route("/breakfast", breakfast_page, methods=["GET"]),
    Route("/treats-desserts", treats_desserts_page, methods=["GET"]),
    Route("/nutrition-allergens", nutrition_allergens_page, methods=["GET"]),
    Route("/deals-coupons", deals_coupons_page, methods=["GET"]),
    Route("/ordering-delivery", ordering_delivery_page, methods=["GET"]),
    Route("/faqs", faqs_page, methods=["GET"]),
    Route("/articles", articles_hub_page, methods=["GET"]),
    Route("/blog", articles_hub_page, methods=["GET"]),
    Route("/articles/{slug}", article_detail_page, methods=["GET"]),
    Route("/search", search_page, methods=["GET"]),
    Route("/contact", contact_get, methods=["GET"]),
    Route("/contact", contact_post, methods=["POST"]),

    # Informational & Policy Pages
    Route("/about", about_page, methods=["GET"]),
    Route("/editorial-policy", editorial_policy_page, methods=["GET"]),
    Route("/sources-fact-checking", sources_fact_checking_page, methods=["GET"]),
    Route("/privacy-policy", privacy_policy_page, methods=["GET"]),
    Route("/terms", terms_page, methods=["GET"]),
    Route("/disclaimer", disclaimer_page, methods=["GET"]),

    # Technical SEO
    Route("/sitemap.xml", sitemap_xml, methods=["GET"]),
    Route("/robots.txt", robots_txt, methods=["GET"]),
    Route("/ads.txt", ads_txt, methods=["GET"]),
    Route("/llms.txt", llms_txt, methods=["GET"]),
    Route("/favicon.ico", favicon_ico, methods=["GET"]),

    # API endpoints
    Route("/api/search/suggestions", api_search_suggestions, methods=["GET"]),
    Route("/api/search/full", api_search_full, methods=["GET"]),

    # Admin Auth
    Route("/admin/login", admin_login_get, methods=["GET"]),
    Route("/admin/login", admin_login_post, methods=["POST"]),
    Route("/admin/logout", admin_logout, methods=["GET"]),

    # Protected Admin Routes
    Route("/admin", admin_dashboard, methods=["GET"]),
    Route("/admin/dashboard", admin_dashboard, methods=["GET"]),
    Route("/admin/articles", admin_articles_list, methods=["GET"]),
    Route("/admin/articles/new", admin_article_new_get, methods=["GET"]),
    Route("/admin/articles/new", admin_article_new_post, methods=["POST"]),
    Route("/admin/articles/edit/{id:int}", admin_article_edit_get, methods=["GET"]),
    Route("/admin/articles/edit/{id:int}", admin_article_edit_post, methods=["POST"]),
    Route("/admin/articles/delete/{id:int}", admin_article_delete_post, methods=["POST"]),
    Route("/admin/menu-items", admin_menu_items_list, methods=["GET"]),
    Route("/admin/menu-items/new", admin_menu_item_new_get, methods=["GET"]),
    Route("/admin/menu-items/new", admin_menu_item_new_post, methods=["POST"]),
    Route("/admin/menu-items/edit/{id:int}", admin_menu_item_edit_get, methods=["GET"]),
    Route("/admin/menu-items/edit/{id:int}", admin_menu_item_edit_post, methods=["POST"]),
    Route("/admin/menu-items/delete/{id:int}", admin_menu_item_delete_post, methods=["POST"]),
    Route("/admin/fact-check", admin_fact_check_queue, methods=["GET"]),
    Route("/admin/fact-check/verify/{id:int}", admin_fact_check_verify, methods=["POST"]),
    Route("/admin/keyword-map", admin_keyword_map, methods=["GET"]),
    Route("/admin/keyword-map/download", admin_keyword_map_download, methods=["GET"]),
    Route("/admin/contacts", admin_contacts_list, methods=["GET"]),
    Route("/admin/contacts/delete/{id:int}", admin_contact_delete_post, methods=["POST"]),
]

app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    middleware=[
        Middleware(SecurityHeadersMiddleware),
        Middleware(CSRFMiddleware)
    ],
    exception_handlers={404: custom_404_handler, 500: custom_500_handler}
)

# Startup validation & database initialization
settings.validate_production_settings()
init_db()
seed_all()
