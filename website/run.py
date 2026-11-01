import sys
from pathlib import Path
import uvicorn

# Ensure the project directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print("=" * 70)
    print("   MENU PRICE GUIDE - US DAIRY QUEEN EDITORIAL REFERENCE")
    print("=" * 70)
    print(" * Local URL:       http://localhost:8000/")
    print(" * Menu Hub:        http://localhost:8000/menu")
    print(" * Blizzard Prices: http://localhost:8000/blizzards/prices-sizes")
    print(" * Admin Dashboard: http://localhost:8000/admin")
    print(" * Admin Login:     editorial_admin (set via ADMIN_INITIAL_PASSWORD in .env)")
    print("=" * 70)
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
