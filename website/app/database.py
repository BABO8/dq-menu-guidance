import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from app.config import settings

def get_db_path() -> Path:
    settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return settings.DATABASE_PATH

@contextmanager
def get_db():
    conn = sqlite3.connect(get_db_path(), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes the database schema with necessary tables, indexes, and constraints."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                icon_name TEXT DEFAULT 'cup',
                display_order INTEGER DEFAULT 0
            );
        """)

        # Menu Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                sizes_available TEXT,
                price_min REAL,
                price_max REAL,
                price_formatted TEXT,
                calories TEXT,
                allergens TEXT,
                is_seasonal INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                verification_status TEXT DEFAULT 'Location-Dependent Range',
                nutrition_verified TEXT DEFAULT 'Official ADQ Disclosures',
                price_verification TEXT DEFAULT 'Estimated Franchise Range',
                promotion_status TEXT DEFAULT 'standard',
                effective_start_date TEXT,
                effective_end_date TEXT,
                source_title TEXT DEFAULT 'Official American Dairy Queen Corporation',
                last_verified TEXT,
                source_url TEXT,
                notes TEXT
            );
        """)

        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                meta_title TEXT,
                meta_description TEXT,
                canonical_url TEXT,
                summary TEXT,
                content TEXT NOT NULL,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                status TEXT DEFAULT 'published',
                is_cornerstone INTEGER DEFAULT 0,
                author TEXT DEFAULT 'DQ Menu Guidance Editorial Team',
                published_at TEXT,
                updated_at TEXT,
                sources_json TEXT,
                review_status TEXT DEFAULT 'verified'
            );
        """)

        # FAQs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                display_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            );
        """)

        # Admin Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TEXT NOT NULL,
                last_login TEXT
            );
        """)

        # Contact submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                ip_hash TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT NOT NULL
            );
        """)

        # Dynamic column migrations for menu_items
        cursor.execute("PRAGMA table_info(menu_items);")
        existing_cols = {col["name"] for col in cursor.fetchall()}
        
        column_defs = {
            "nutrition_verified": "TEXT DEFAULT 'Official ADQ Disclosures'",
            "price_verification": "TEXT DEFAULT 'Estimated Franchise Range'",
            "promotion_status": "TEXT DEFAULT 'standard'",
            "effective_start_date": "TEXT",
            "effective_end_date": "TEXT",
            "source_title": "TEXT DEFAULT 'Official American Dairy Queen Corporation'"
        }
        
        for col_name, col_type in column_defs.items():
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE menu_items ADD COLUMN {col_name} {col_type};")

        # Indexes for fast lookup and search
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_menu_category ON menu_items(category_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_menu_slug ON menu_items(slug);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs(category_id);")

        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database schema successfully initialized.")
