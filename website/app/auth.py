import hashlib
import hmac
import secrets
import json
import base64
import time
import bcrypt
from typing import Optional, Dict, Any, Tuple
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.exceptions import HTTPException
from app.config import settings

# In-memory tracking for failed login attempts (keyed by client IP or username)
_failed_login_attempts: Dict[str, list] = {}

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt with standard work factor."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against bcrypt or legacy pbkdf2 hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        # Check bcrypt prefix
        if hashed_password.startswith(("$2b$", "$2a$", "$2y$")):
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        
        # Legacy PBKDF2-HMAC-SHA256
        if hashed_password.startswith("pbkdf2:"):
            method, salt, key_hex = hashed_password.split('$')
            _, _, iterations_str = method.split(':')
            iterations = int(iterations_str)
            
            computed_key = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode('utf-8'),
                salt.encode('utf-8'),
                iterations
            )
            return hmac.compare_digest(computed_key.hex(), key_hex)
        return False
    except Exception:
        return False

def sign_data(data: dict) -> str:
    """Signs a dict payload into a base64 string with HMAC-SHA256 signature."""
    payload_json = json.dumps(data, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8')
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"{payload_b64}.{signature}"

def verify_signed_data(token: str) -> Optional[dict]:
    """Verifies a signed token and returns the dict payload if valid and not expired."""
    if not token or '.' not in token:
        return None
    try:
        payload_b64, signature = token.split('.', 1)
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_sig, signature):
            return None
        
        payload_json = base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
        data = json.loads(payload_json)
        
        # Check expiry
        if "exp" in data and time.time() > data["exp"]:
            return None
            
        return data
    except Exception:
        return None

def create_admin_session(username: str, role: str = "admin") -> str:
    """Creates a signed session token with a random nonce to protect against session fixation."""
    payload = {
        "user": username,
        "role": role,
        "exp": time.time() + (settings.ADMIN_SESSION_EXPIRY_HOURS * 3600),
        "nonce": secrets.token_hex(16)
    }
    return sign_data(payload)

def get_current_admin(request: Request) -> Optional[dict]:
    """Retrieves and validates admin session from the cookie."""
    cookie_val = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not cookie_val:
        return None
    return verify_signed_data(cookie_val)

def generate_csrf_token(request: Request) -> str:
    """
    Returns the CSRF token associated with the current request state.
    The CSRFMiddleware handles generating and setting the signed cookie on the response.
    """
    return getattr(request.state, "csrf_token", "")

def verify_csrf_token(request: Request, submitted_token: str) -> bool:
    """
    Verifies that submitted CSRF token matches the signed cookie value.
    Validates both signature and constant-time match.
    """
    if not submitted_token:
        return False
    cookie_token = request.cookies.get(settings.CSRF_COOKIE_NAME)
    if not cookie_token:
        return False
    data = verify_signed_data(cookie_token)
    if not data or "csrf" not in data:
        return False
    return hmac.compare_digest(data["csrf"], submitted_token.strip())

# Login Throttling / Brute-force protection
def check_login_rate_limit(key: str) -> Tuple[bool, int]:
    """
    Checks if a client IP or username has exceeded failed login limits.
    Returns (is_allowed, seconds_remaining_in_lockout).
    """
    now = time.time()
    window = settings.LOGIN_LOCKOUT_WINDOW_SECONDS
    max_attempts = settings.LOGIN_MAX_FAILED_ATTEMPTS
    
    attempts = _failed_login_attempts.get(key, [])
    # Filter attempts within window
    attempts = [t for t in attempts if now - t < window]
    _failed_login_attempts[key] = attempts
    
    if len(attempts) >= max_attempts:
        oldest_attempt = attempts[0]
        retry_after = int(window - (now - oldest_attempt))
        return False, max(1, retry_after)
    
    return True, 0

def record_failed_login(key: str):
    """Records a failed login attempt for the key."""
    now = time.time()
    attempts = _failed_login_attempts.get(key, [])
    attempts.append(now)
    _failed_login_attempts[key] = attempts

def clear_failed_logins(key: str):
    """Resets failed login counter upon successful authentication."""
    _failed_login_attempts.pop(key, None)
