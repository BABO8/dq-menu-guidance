import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    SITE_NAME: str = "DQ Menu Guidance"
    SITE_TAGLINE: str = "Independent US Dairy Queen Menu, Prices & Nutrition Reference"
    
    # Environment mode: 'development', 'staging', 'production'
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    
    # Debug mode defaults to True only in development
    DEBUG: bool = os.getenv("DEBUG", "True" if ENVIRONMENT == "development" else "False").lower() in ("true", "1")
    
    # Canonical public URL (Never defaults to localhost in production)
    SITE_URL: str = os.getenv(
        "SITE_URL",
        "http://localhost:8000" if DEBUG else "https://your-production-domain.com"
    ).rstrip("/")
    
    # Cryptographic secret key for session signing and CSRF tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-in-production-dq-2026-v1")
    
    # Cookie security settings
    SESSION_COOKIE_NAME: str = "mpg_session"
    CSRF_COOKIE_NAME: str = "mpg_csrf"
    COOKIE_SAMESITE: str = "lax"
    
    @property
    def COOKIE_SECURE(self) -> bool:
        """Enforces Secure flag on cookies in production or whenever HTTPS is configured."""
        env_secure = os.getenv("COOKIE_SECURE")
        if env_secure is not None:
            return env_secure.lower() in ("true", "1", "yes")
        return (not self.DEBUG) or self.SITE_URL.startswith("https://")
    
    # Allowed hosts for trusted host middleware
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        raw = os.getenv("ALLOWED_HOSTS", "*")
        return [h.strip() for h in raw.split(",") if h.strip()]
    
    # Database configuration
    DATABASE_PATH: Path = BASE_DIR / "data" / "dq_guide.db"
    
    # Session lifetime
    ADMIN_SESSION_EXPIRY_HOURS: int = 8
    
    # Brute-force throttling settings
    LOGIN_MAX_FAILED_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_WINDOW_SECONDS: int = 900  # 15 minutes
    
    # Optional initial administrator password override
    ADMIN_INITIAL_PASSWORD: str = os.getenv("ADMIN_INITIAL_PASSWORD", "")
    
    # Google AdSense Publisher ID
    ADSENSE_PUB_ID: str = os.getenv("ADSENSE_PUB_ID", "pub-0000000000000000")

    # Legal independence disclaimer
    DISCLAIMER: str = (
        "DQ Menu Guidance is an independent fan and informational guide and is not affiliated with, "
        "endorsed by, or sponsored by American Dairy Queen Corporation. Menu items, prices, "
        "availability, ingredients, and promotions may vary by location and change over time. "
        "Confirm current details with the restaurant."
    )

    def validate_production_settings(self):
        """Enforces security constraints when running outside of local development."""
        if not self.DEBUG or self.ENVIRONMENT == "production":
            dev_default = "dev-insecure-secret-key-change-in-production-dq-2026-v1"
            if self.SECRET_KEY == dev_default or len(self.SECRET_KEY) < 32:
                raise RuntimeError(
                    "FATAL SECURITY ERROR: Insecure or default SECRET_KEY detected in production! "
                    "You must supply a strong, randomly generated SECRET_KEY (at least 32 characters) "
                    "via environment variables before running in production."
                )
            if "localhost" in self.SITE_URL.lower() or "127.0.0.1" in self.SITE_URL:
                raise RuntimeError(
                    "FATAL CONFIG ERROR: SITE_URL cannot point to localhost in production. "
                    "Configure your confirmed public domain (e.g., https://your-domain.com)."
                )

settings = Settings()
