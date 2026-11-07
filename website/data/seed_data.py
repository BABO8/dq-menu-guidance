import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
from generate_articles import NEW_ARTICLES
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Ensure project root is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db, init_db
from app.auth import hash_password
from app.config import settings

def seed_all(force: bool = False):
    init_db()
    
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if already seeded
        cursor.execute("SELECT count(*) as count FROM categories")
        if cursor.fetchone()["count"] > 0 and not force:
            print("Database already contains data. Skipping initial seed.")
            return

        if force:
            print("Forcing full database re-seed...")
            cursor.execute("DELETE FROM menu_items")
            cursor.execute("DELETE FROM faqs")
            cursor.execute("DELETE FROM articles")
            cursor.execute("DELETE FROM categories")
            cursor.execute("DELETE FROM admin_users")

        print("Seeding categories...")
        categories = [
            ("Blizzard® Treats", "blizzards", "Soft serve blended with candies, cookies, and fruit puree toppings.", "blizzard", 1),
            ("Ice Cream Cakes", "cakes", "Decorated soft serve celebration cakes and Treatzza Pizzas.", "cake", 2),
            ("Burgers & Sandwiches", "burgers", "Signature 100% seasoned beef Stackburgers and grilled specialties.", "burger", 3),
            ("Food & Baskets", "food", "Crispy chicken strips, dipping gravies, fries, and savory sides.", "basket", 4),
            ("Treats & Novelties", "treats", "Classic cones, dipped cones, Dilly® Bars, Buster Bars, and sundaes.", "ice-cream", 5),
            ("Beverages & Shakes", "drinks", "Hand-spun milkshakes, malts, misty slushes, and fountain refreshments.", "drink", 6),
            ("Regional Breakfast", "breakfast", "Texas and select regional Southern breakfast platters, biscuits, and bowls.", "coffee", 7),
            ("Deals & Value Meals", "deals", "Official value meals, DQ Rewards promotions, and seasonal specials.", "tag", 8),
            ("Nutrition & Allergens", "nutrition", "Official nutritional disclosures, allergen cross-contact warnings, and dietary guidance.", "heart", 9)
        ]
        cursor.executemany("""
            INSERT INTO categories (name, slug, description, icon_name, display_order)
            VALUES (?, ?, ?, ?, ?)
        """, categories)

        # Retrieve category IDs
        cursor.execute("SELECT id, slug FROM categories")
        cat_map = {row["slug"]: row["id"] for row in cursor.fetchall()}

        print("Seeding verified US menu items...")
        menu_items = [
            # --- BLIZZARDS ---
            (
                cat_map["blizzards"],
                "OREO® Cookie Blizzard",
                "oreo-cookie-blizzard",
                "The iconic original: vanilla soft serve blended with crunchy OREO® cookie pieces.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "380 - 1140 kcal",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Vanilla soft serve blended with OREO cookie pieces. Calories span Mini (380), Small (620), Medium (860), through Large (1,140 kcal)."
            ),
            (
                cat_map["blizzards"],
                "Reese's® Peanut Butter Cup Blizzard",
                "reeses-peanut-butter-cup-blizzard",
                "Milk chocolate and peanut butter cups blended with creamy vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "410 - 1210 kcal",
                "Milk, Peanuts, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Core menu candy Blizzard featuring milk chocolate and peanut butter cups. Calories: Mini 410, Small 670, Medium 910, Large 1,210 kcal."
            ),
            (
                cat_map["blizzards"],
                "Chocolate Chip Cookie Dough Blizzard",
                "chocolate-chip-cookie-dough-blizzard",
                "Soft cookie dough bites and rich fudge chunks blended in vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "420 - 1340 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Soft cookie dough bites and rich fudge chunks in soft serve. Calories: Mini 420, Small 710, Medium 990, Large 1,340 kcal."
            ),
            (
                cat_map["blizzards"],
                "Butterfinger® Blizzard",
                "butterfinger-blizzard",
                "Crispy, crunchy peanut-buttery Butterfinger® candy bar pieces in vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "350 - 1060 kcal",
                "Milk, Peanuts, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Crisp Butterfinger candy pieces in soft serve. Official ADQ values: Mini (6 oz) 350 kcal, Small (12 oz) 590 kcal, Medium (16 oz) 800 kcal, Large (21 oz) 1,060 kcal."
            ),
            (
                cat_map["blizzards"],
                "Turtle Pecan Cluster Blizzard",
                "turtle-pecan-cluster-blizzard",
                "Pecan pieces blended with chocolate cone coating and decadent hot caramel.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "450 - 1350 kcal",
                "Milk, Tree Nuts (Pecans), Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Pecan pieces, chocolate cone coating, and caramel in soft serve. Calories: Mini 450, Small 730, Medium 1,010, Large 1,350 kcal."
            ),
            (
                cat_map["blizzards"],
                "Choco Brownie Extreme Blizzard",
                "choco-brownie-extreme-blizzard",
                "Chewy chocolate brownie pieces, choco chunks, and cocoa fudge blended in soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "420 - 1330 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Brownie pieces, choco chunks, and cocoa fudge. Official ADQ values: Mini (6 oz) 420 kcal, Small (12 oz) 740 kcal, Medium (16 oz) 980 kcal, Large (21 oz) 1,330 kcal."
            ),
            (
                cat_map["blizzards"],
                "Strawberry Cheesecake Blizzard",
                "strawberry-cheesecake-blizzard",
                "Real strawberry fruit topping and graham-crust cheesecake chunks in vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "350 - 1020 kcal",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Real strawberry fruit topping and graham crust cheesecake pieces. Calories: Mini 350, Small 560, Medium 760, Large 1,020 kcal."
            ),
            (
                cat_map["blizzards"],
                "Snickers® Brownie Blizzard",
                "snickers-brownie-blizzard",
                "Snickers® pieces, brownie bites, and caramel topping blended in soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "430 - 1310 kcal",
                "Milk, Peanuts, Soy, Wheat, Eggs",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Snickers bar pieces, chewy brownie chunks, and caramel. Calories: Mini 430, Small 710, Medium 970, Large 1,310 kcal."
            ),
            (
                cat_map["blizzards"],
                "Caramel Pecan Blizzard",
                "caramel-pecan-blizzard",
                "Crunchy roasted pecan pieces and thick caramel blended with vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "420 - 1240 kcal",
                "Milk, Tree Nuts (Pecans)",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Pecans and caramel blended in vanilla soft serve. Calories: Mini 420, Small 680, Medium 920, Large 1,240 kcal."
            ),
            (
                cat_map["blizzards"],
                "Royal OREO® Blizzard with Cold Fudge Center",
                "royal-oreo-blizzard",
                "OREO® cookie Blizzard with a decadent, molten core of rich cold fudge down the middle.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                4.59, 7.39, "Mini $4.59 | Small $5.69 | Med $6.59 | Lrg $7.39",
                "450 - 1310 kcal",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Premium Royal treat featuring vanilla soft serve with OREO pieces and a filled cold fudge core. Calories: Mini 450, Small 720, Medium 990, Large 1,310 kcal."
            ),

            # --- 2026 HOLIDAY COOKIE SWAP BLIZZARD COLLECTION ---
            (
                cat_map["blizzards"],
                "Peanut Butter Blossom made with HERSHEY'S MINI KISSES Blizzard Treat",
                "peanut-butter-blossom-hersheys-blizzard",
                "Peanut butter blossom cookies and HERSHEY'S® MINI KISSES® pieces blended with world-famous vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "420 - 1150 kcal",
                "Milk, Peanuts, Soy, Wheat, Eggs",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", "2026-11-01", "2026-12-31",
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Part of the 2026 Holiday Cookie Swap Blizzard Collection. Soft serve blended with peanut butter blossom cookies and Hershey's Mini Kisses. Calories: Mini 420, Small 690, Medium 940, Large 1,150 kcal."
            ),
            (
                cat_map["blizzards"],
                "Peppermint Bark Blizzard Treat",
                "peppermint-bark-blizzard",
                "Real peppermint bark candy pieces, rich choco chunks, and white peppermint chocolate blended in vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "400 - 1090 kcal",
                "Milk, Soy",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", "2026-11-01", "2026-12-31",
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Part of the 2026 Holiday Cookie Swap Blizzard Collection. Peppermint bark pieces and choco chunks in creamy soft serve. Calories: Mini 400, Small 650, Medium 880, Large 1,090 kcal."
            ),

            # --- 2026 FALL SEASONAL BLIZZARD MENU ---
            (
                cat_map["blizzards"],
                "Brown Sugar Cookie Dough Blizzard Treat",
                "brown-sugar-cookie-dough-blizzard",
                "Soft brown sugar cookie dough pieces, rich choco chunks, and maple caramel blended in vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "410 - 1120 kcal",
                "Milk, Soy, Wheat, Eggs",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", "2026-08-25", "2026-11-30",
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "2026 Fall seasonal Blizzard featuring brown sugar cookie dough pieces and rich choco chunks. Calories: Mini 410, Small 670, Medium 910, Large 1,120 kcal."
            ),
            (
                cat_map["blizzards"],
                "Caramel Apple Cheesecake Blizzard Treat",
                "caramel-apple-cheesecake-blizzard",
                "Real apple fruit topping, cheesecake chunks, and caramel drizzle blended with creamy vanilla soft serve.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "390 - 1060 kcal",
                "Milk, Soy, Wheat, Eggs",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", "2026-08-25", "2026-11-30",
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "2026 Fall seasonal favorite combining spiced apple fruit topping and graham crust cheesecake bites. Calories: Mini 390, Small 630, Medium 860, Large 1,060 kcal."
            ),
            (
                cat_map["blizzards"],
                "Pumpkin Pie Blizzard Treat",
                "pumpkin-pie-blizzard",
                "Real pumpkin pie spice mix and pie crust pieces blended with soft serve, crowned with whipped topping and nutmeg.",
                "Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz)",
                3.79, 6.59, "Mini $3.79 | Small $4.89 | Med $5.79 | Lrg $6.59",
                "360 - 980 kcal",
                "Milk, Soy, Wheat, Eggs",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", "2026-08-25", "2026-11-30",
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Iconic Fall staple blended with real pumpkin pie filling, pie crust pieces, and crowned with whipped topping. Calories: Mini 360, Small 580, Medium 790, Large 980 kcal."
            ),

            # --- ICE CREAM CAKES ---
            (
                cat_map["cakes"],
                "8-Inch Round Ice Cream Cake",
                "8-inch-round-ice-cream-cake",
                "Layers of vanilla and chocolate soft serve with a middle crunch layer of cocoa fudge and chocolate cookie crunch.",
                "8-Inch Round (Serves 8-10)",
                31.24, 34.99, "$31.24 - $34.99",
                "4000 kcal total (~400 kcal/slice)",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/cakes/",
                "Serves 8 to 10 guests. Features vanilla soft serve, chocolate soft serve, and the famous fudge crunch center. National average price: $31.24 - $34.99."
            ),
            (
                cat_map["cakes"],
                "10-Inch Round Ice Cream Cake",
                "10-inch-round-ice-cream-cake",
                "Large party size with vanilla and chocolate soft serve and thick chocolate cookie fudge center.",
                "10-Inch Round (Serves 12-16)",
                34.99, 38.74, "$34.99 - $38.74",
                "5900 kcal total (~420 kcal/slice)",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/cakes/",
                "Serves 12 to 16 guests. Highest volume efficiency per dollar of round celebration cakes. National average price: $34.99 - $38.74."
            ),
            (
                cat_map["cakes"],
                "8-Inch Blizzard® Cake",
                "blizzard-cake-8-inch",
                "Custom celebration cake topped with an entire layer of your choice of Blizzard (OREO®, Reese's®, etc.).",
                "8-Inch Round (Serves 8-10)",
                34.99, 39.99, "$34.99 - $39.99",
                "4300 - 5200 kcal total",
                "Milk, Soy, Wheat, Peanuts (varies by flavor)",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/cakes/",
                "Combines vanilla soft serve, fudge crunch center, and a full top layer of blended Blizzard treat. 2026 national average price: $34.99."
            ),
            (
                cat_map["cakes"],
                '11" x 14" Sheet Cake',
                "sheet-cake-11x14",
                "Large rectangular sheet cake with signature fudge and cookie crunch center.",
                "11x14 Rectangle (Serves 20-24)",
                42.99, 54.99, "$42.99 - $54.99",
                "8200 kcal total (~390 kcal/slice)",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/cakes/",
                "Ideal for school banquets, corporate milestones, and graduation parties. Advance notice typically required."
            ),
            (
                cat_map["cakes"],
                "Choco Brownie Treatzza Pizza®",
                "choco-brownie-treatzza-pizza",
                "Fudge crust layered with vanilla soft serve, brownie pieces, choco chunks, and cocoa fudge drizzle.",
                "Pre-sliced (Serves 6-8)",
                14.99, 18.99, "$14.99 - $18.99",
                "190 kcal / slice (8 slices)",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/cakes/",
                "Grab-and-go freezer case casual treat. Crust made from chocolate cookie crumb."
            ),
            (
                cat_map["cakes"],
                "Reese's® Peanut Butter Treatzza Pizza®",
                "reeses-treatzza-pizza",
                "Chocolate crust topped with soft serve, chopped Reese's peanut butter cups, and peanut butter sauce.",
                "Pre-sliced (Serves 6-8)",
                14.99, 18.99, "$14.99 - $18.99",
                "200 kcal / slice (8 slices)",
                "Milk, Peanuts, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/cakes/",
                "Pre-packaged frozen celebration treat for peanut butter fans."
            ),

            # --- BURGERS & SANDWICHES ---
            (
                cat_map["burgers"],
                "Bacon Two-Cheese Deluxe Signature Stackburger™",
                "bacon-two-cheese-deluxe-stackburger",
                "100% seasoned beef patties, thick-cut bacon, sharp American & white cheddar cheeses, tomato, pickles, and mayo.",
                "1/3 lb Double Solo, 1/2 lb Triple Solo, Combos",
                7.79, 9.29, "Double Solo $7.79 | Triple Solo $9.29 | Combo $10.87",
                "710 - 980 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Signature Stackburger on toasted bun. 2026 US National Averages: Double Solo $7.79, Triple Solo $9.29, Combo $10.87."
            ),
            (
                cat_map["burgers"],
                "FlameThrower® Signature Stackburger™",
                "flamethrower-signature-stackburger",
                "Spicy FlameThrower chili sauce, melted Pepper Jack cheese, jalapeño bacon, tomato, and fresh lettuce.",
                "1/3 lb Double Solo, 1/2 lb Triple Solo, Combos",
                8.19, 9.69, "Double Solo $8.19 | Triple Solo $9.69 | Combo $10.87",
                "740 - 1010 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "DQ's signature fiery burger. Double Solo $8.19, Triple Solo $9.69, Combo with fries and drink averaging $10.87."
            ),
            (
                cat_map["burgers"],
                "Original Double Cheeseburger",
                "original-double-cheeseburger",
                "Two seasoned 100% beef patties, melted American cheese, pickles, mustard, and ketchup on a toasted bun.",
                "Double Patty Solo or Combo",
                4.69, 5.49, "$4.69 - $5.49 (Combo $7.39 - $8.49)",
                "540 kcal",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Core value burger offering. Standard entrée choice in the $7 Meal Deal."
            ),
            (
                cat_map["burgers"],
                "Loaded A.1.® Steakhouse Signature Stackburger™",
                "loaded-a1-steakhouse-stackburger",
                "A.1.® thick steak sauce, crispy onion rings, melted cheddar cheese, applewood bacon, and mayo.",
                "Double Solo or Triple Solo",
                7.99, 9.49, "$7.99 - $9.49 (Combo $10.87)",
                "780 - 1050 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Savory steakhouse style burger served with thick A.1. sauce and onion rings."
            ),

            # --- FOOD & BASKETS ---
            (
                cat_map["food"],
                "Crispy Chicken Strip Basket (4-Piece)",
                "crispy-chicken-strip-basket-4pc",
                "Four 100% all-tenderloin white meat chicken strips, Texas toast, crispy fries, and country dipping gravy.",
                "4-Piece Basket",
                9.99, 10.87, "$9.99 - $10.87",
                "910 - 1020 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Flagship hot food entrée served with fries, Texas toast, and choice of dipping sauce. National average price: $9.99 - $10.87."
            ),
            (
                cat_map["food"],
                "Crispy Chicken Strip Basket (6-Piece)",
                "crispy-chicken-strip-basket-6pc",
                "Six 100% tenderloin white meat chicken strips, Texas toast, crispy fries, and country dipping gravy.",
                "6-Piece Basket",
                13.49, 13.49, "$13.49",
                "1250 - 1360 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Large hunger basket serving six tenderloin chicken strips with fries and Texas toast. 2026 US National Average: $13.49."
            ),
            (
                cat_map["food"],
                "FlameThrower Chicken Strip Basket (4-Piece)",
                "flamethrower-chicken-strip-basket-4pc",
                "Four tenderloin chicken strips tossed in fiery FlameThrower seasoning, served with Texas toast, fries, and spicy FlameThrower dipping sauce.",
                "4-Piece Basket",
                10.49, 10.49, "$10.49",
                "1030 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Four spicy seasoned chicken strips with fries, Texas toast, and FlameThrower sauce. 1,030 kcal."
            ),
            (
                cat_map["food"],
                "FlameThrower Chicken Strip Basket (6-Piece)",
                "flamethrower-chicken-strip-basket-6pc",
                "Six tenderloin chicken strips tossed in fiery FlameThrower seasoning, served with Texas toast, fries, and spicy FlameThrower dipping sauce.",
                "6-Piece Basket",
                13.49, 13.49, "$13.49",
                "1380 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Six spicy seasoned chicken strips with fries, Texas toast, and FlameThrower sauce. 1,380 kcal."
            ),
            (
                cat_map["food"],
                "Crispy Chicken Sandwich",
                "crispy-chicken-sandwich",
                "All-white meat crispy chicken filet, lettuce, tomato, and mayo on a toasted bun.",
                "Solo or Combo",
                5.49, 6.99, "$5.49 - $6.99",
                "550 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Tender crispy chicken breast filet on a bakery bun."
            ),
            (
                cat_map["food"],
                "Wild Alaskan Fish Sandwich",
                "wild-alaskan-fish-sandwich",
                "Crispy breaded wild Alaskan pollock filet, tangy tartar sauce, and shredded lettuce.",
                "Solo or Combo",
                4.99, 6.29, "$4.99 - $6.29",
                "420 kcal",
                "Fish, Milk, Soy, Wheat, Eggs",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Seasonal fish sandwich frequently promoted during Lenten periods."
            ),
            (
                cat_map["food"],
                "Regular French Fries",
                "regular-french-fries",
                "Hot, golden, crispy french fries salted to perfection.",
                "Regular (~4.5 oz)",
                2.49, 2.49, "$2.49",
                "280 kcal",
                "Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Standard side included with Grill & Chill combo meals and $7 Meal Deal. National average: $2.49."
            ),
            (
                cat_map["food"],
                "Large French Fries",
                "large-french-fries",
                "Large portion of golden, crispy french fries.",
                "Large (~6.5 oz)",
                3.49, 3.49, "$3.49",
                "430 kcal",
                "Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Large side of golden fries. National average: $3.49."
            ),
            (
                cat_map["food"],
                "Onion Rings",
                "onion-rings",
                "Thick-cut whole onion slices battered in crispy golden breading.",
                "Regular Side Order",
                3.29, 3.29, "$3.29",
                "360 kcal",
                "Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Crispy golden onion rings side. National average: $3.29."
            ),
            (
                cat_map["food"],
                "Cheese Curds",
                "cheese-curds",
                "Bite-sized real Wisconsin white cheddar cheese curds breaded and fried to gooey perfection.",
                "Regular Side Order",
                3.99, 3.99, "$3.99",
                "510 kcal",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Popular Midwest snack favorite fried golden. National average: $3.99."
            ),

            # --- TREATS & NOVELTIES ---
            (
                cat_map["treats"],
                "Classic Soft Serve Cone",
                "classic-soft-serve-cone",
                "World-famous Dairy Queen vanilla, chocolate, or twist soft serve with the signature curl on top.",
                "Small, Medium, Large",
                2.59, 3.99, "Small $2.59 | Medium $3.29 | Large $3.99",
                "230 - 450 kcal",
                "Milk, Wheat (cone)",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "The foundation of Dairy Queen soft serve since 1940. Free Cone Day promotional item."
            ),
            (
                cat_map["treats"],
                "Chocolate Dipped Cone",
                "chocolate-dipped-cone",
                "Vanilla soft serve dipped in rich chocolate coating that hardens into a crisp shell.",
                "Small, Medium, Large",
                3.29, 4.69, "Small $3.29 | Medium $3.99 | Large $4.69",
                "320 - 640 kcal",
                "Milk, Soy, Wheat (cone)",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "Classic treat with crunchy chocolate outer shell. 2026 US range: $3.29 to $4.69."
            ),
            (
                cat_map["treats"],
                "Hot Fudge Sundae",
                "hot-fudge-sundae",
                "Creamy vanilla soft serve crowned with rich hot fudge and finished with the signature curl.",
                "Small, Medium, Large",
                3.59, 5.19, "Small $3.59 | Medium $4.39 | Large $5.19",
                "300 - 610 kcal",
                "Milk, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "Standard sundae dessert included in the $7 Meal Deal. National average: $3.59 - $5.19."
            ),
            (
                cat_map["treats"],
                "Dilly® Bar",
                "dilly-bar",
                "Vanilla soft serve disc on a stick dipped in luscious chocolate confectionery coating.",
                "Single Bar or 6-Pack Box",
                2.19, 2.19, "$2.19 (6-Pack $11.49)",
                "220 kcal",
                "Milk, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "Pre-packaged frozen classic novelty invented in 1955. National average: $2.19."
            ),
            (
                cat_map["treats"],
                "Non-Dairy Dilly® Bar (Vegan / Gluten-Free)",
                "non-dairy-dilly-bar",
                "Coconut cream-based frozen dessert dipped in vegan chocolate confectionery coating.",
                "Single Bar or 6-Pack Box",
                2.39, 2.39, "$2.39 (6-Pack $12.49)",
                "240 kcal",
                "Coconut, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "Certified gluten-free and vegan treat made with coconut cream base."
            ),
            (
                cat_map["treats"],
                "Buster Bar®",
                "buster-bar",
                "Vanilla soft serve layered with crunchy peanuts, chocolate fudge, and a rich chocolate shell.",
                "Single Bar or 6-Pack Box",
                3.49, 3.49, "$3.49 (6-Pack $16.99)",
                "460 kcal",
                "Milk, Peanuts, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "Peanut and hot fudge novelty on a stick. National average: $3.49."
            ),
            (
                cat_map["treats"],
                "Peanut Buster® Parfait",
                "peanut-buster-parfait",
                "Alternating layers of vanilla soft serve, hot fudge, and salted roasted Spanish peanuts.",
                "Standard Parfait Cup",
                4.99, 4.99, "$4.99",
                "710 kcal",
                "Milk, Peanuts, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "Decadent parfait served in a tall clear cup with whole Spanish peanuts. National average: $4.99."
            ),
            (
                cat_map["treats"],
                "Banana Split",
                "banana-split",
                "Three swirls of vanilla soft serve nestled between banana halves, with chocolate, strawberry, and pineapple toppings.",
                "Standard Boat",
                5.69, 5.69, "$5.69",
                "520 kcal",
                "Milk, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/treats/",
                "Traditional banana split with three fruit and fudge toppings. National average: $5.69."
            ),

            # --- BEVERAGES & SHAKES ---
            (
                cat_map["drinks"],
                "Hand-Spun Milkshake (Chocolate / Strawberry / Vanilla)",
                "hand-spun-milkshake",
                "Creamy vanilla soft serve blended with real milk and flavored syrups, crowned with whipped topping.",
                "Small (16 oz), Medium (24 oz), Large (32 oz)",
                4.79, 6.39, "Small $4.79 | Medium $5.59 | Large $6.39",
                "530 - 990 kcal",
                "Milk, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/drinks/",
                "Classic thick milkshake hand-spun with milk and soft serve. 2026 US range: $4.79 - $6.39."
            ),
            (
                cat_map["drinks"],
                "Classic Malted Milkshake",
                "classic-malted-milkshake",
                "Vanilla soft serve blended with milk and sweet malt powder for a nostalgic soda-fountain flavor.",
                "Small (16 oz), Medium (24 oz), Large (32 oz)",
                5.19, 6.79, "Small $5.19 | Medium $5.99 | Large $6.79",
                "580 - 1060 kcal",
                "Milk, Soy, Wheat (malt)",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/drinks/",
                "Old-fashioned malted milkshake with premium malted milk powder."
            ),
            (
                cat_map["drinks"],
                "MooLatté® Frozen Coffee (Mocha / Caramel / Vanilla)",
                "moolatte-frozen-coffee",
                "Rich coffee blended with vanilla soft serve, ice, and flavored syrups, topped with whipped cream.",
                "Small (16 oz), Medium (24 oz), Large (32 oz)",
                4.29, 5.89, "Small $4.29 | Medium $5.09 | Large $5.89",
                "460 - 790 kcal",
                "Milk, Soy",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/drinks/",
                "Blended frozen coffee drink with soft serve. US starting price: $4.29."
            ),
            (
                cat_map["drinks"],
                "Misty® Slush (Blue Raspberry / Cherry / Strawberry Kiwi)",
                "misty-slush",
                "Cool, refreshing, fruit-flavored crushed ice beverage.",
                "Small (16 oz), Medium (24 oz), Large (32 oz)",
                2.39, 3.49, "Small $2.39 | Medium $2.89 | Large $3.49",
                "200 - 360 kcal",
                "None (Dairy-Free)",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "standard", None, None,
                "Official ADQ Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/drinks/",
                "Dairy-free crushed ice slush beverage. US starting price: $2.39."
            ),
            (
                cat_map["drinks"],
                "Toasted Marshmallow Mocha DQ Coffee Cooler",
                "toasted-marshmallow-mocha-coffee-cooler",
                "Rich mocha coffee blended with toasted marshmallow syrup and vanilla soft serve, topped with whipped cream.",
                "Small (16 oz), Medium (24 oz), Large (32 oz)",
                4.29, 5.69, "Small $4.29 | Medium $4.99 | Large $5.69",
                "380 - 640 kcal",
                "Milk, Soy",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", "2026-08-25", "2026-11-30",
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Seasonal Fall DQ Coffee Cooler specialty blended with toasted marshmallow flavor and cold-dosed coffee. Calories: Small 380, Medium 510, Large 640 kcal."
            ),
            (
                cat_map["drinks"],
                "Maple Cookie Shake",
                "maple-cookie-shake",
                "Hand-spun vanilla soft serve blended with rich maple syrup, spiced cookie pieces, and milk, garnished with whipped topping.",
                "Small (16 oz), Medium (24 oz), Large (32 oz)",
                4.79, 6.39, "Small $4.79 | Medium $5.59 | Large $6.39",
                "540 - 890 kcal",
                "Milk, Soy, Wheat",
                1, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Estimated Franchise Range",
                "seasonal", "2026-08-25", "2026-11-30",
                "Official ADQ Nutrition & Allergen Disclosures",
                "2026-10", "https://www.dairyqueen.com/en-us/nutrition-allergens/",
                "Hand-spun Fall seasonal milkshake featuring maple syrup and crunchy spiced cookie bits. Calories: Small 540, Medium 720, Large 890 kcal."
            ),

            # --- REGIONAL BREAKFAST ---
            (
                cat_map["breakfast"],
                "Texas Country Breakfast Platter",
                "texas-country-breakfast-platter",
                "Two eggs cooked to order, choice of sausage or bacon, crispy hash brown rounds, and buttered Texas toast with country gravy.",
                "Standard Breakfast Platter",
                5.99, 7.49, "$5.99 - $7.49",
                "760 - 920 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Regional / Needs Verification",
                "Regional Franchise Disclosures",
                "Estimated Regional Franchise Range",
                "standard", None, None,
                "Texas Dairy Queen Operators' Council",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Served exclusively at Texas DQ locations and select Southern franchises; operating hours typically between 6:00 AM and 10:30 AM."
            ),
            (
                cat_map["breakfast"],
                "Biscuit Sandwich (Sausage, Egg & Cheese)",
                "biscuit-sandwich-sausage-egg-cheese",
                "Fresh-baked buttermilk biscuit with savory pork sausage patty, folded egg, and melted American cheese.",
                "Single Biscuit Sandwich",
                3.49, 4.49, "$3.49 - $4.49",
                "510 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Regional / Needs Verification",
                "Regional Franchise Disclosures",
                "Estimated Regional Franchise Range",
                "standard", None, None,
                "Texas Dairy Queen Operators' Council",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Available only at participating breakfast-serving locations. Standard Treat-only locations do not serve hot breakfast."
            ),

            # --- DEALS & VALUE MEALS ---
            (
                cat_map["deals"],
                "$7 Meal Deal (with $2 Small Blizzard Upgrade)",
                "7-dollar-meal-deal",
                "Choice of Original Double Cheeseburger or 3-Piece Chicken Strips, regular fries, 21oz drink, and sundae for $7.00 (or $9.00 with optional $2.00 Small Blizzard upgrade).",
                "Complete Combo + Sundae (or +$2 Small Blizzard)",
                7.00, 9.00, "$7.00 ($9.00 with Small Blizzard upgrade)",
                "920 - 1280 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Verified National Promotion",
                "active", "2026-01-01", "2026-11-01",
                "Official ADQ National Promotional Disclosure",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Active through November 1, 2026. Features entrée choice, fries, 21oz fountain drink, and sundae, with optional $2 upgrade to a Small Blizzard."
            ),
            (
                cat_map["deals"],
                "2 for $5 Mix & Match",
                "2-for-5-mix-match",
                "Mix and match any two select favorites: Original Cheeseburger, 2-Piece Chicken Strips, Small Sundae, or Pretzel Sticks with Zesty Queso.",
                "Choice of 2 Selected Items",
                5.00, 5.00, "$5.00",
                "380 - 640 kcal",
                "Milk, Soy, Wheat",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Verified National Promotion",
                "active", None, None,
                "Official ADQ National Promotions",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Select participating Grill & Chill locations. Choice of 2 items for five dollars total."
            ),
            (
                cat_map["deals"],
                "$8 Meal Deal (Coming Nov 2, 2026)",
                "8-dollar-meal-deal",
                "Updated value meal announced October 26, 2026. Choice of 3-piece chicken strips or original double cheeseburger, fries, 21oz drink, and sundae with $2 small Blizzard upgrade option.",
                "Complete Combo + Dessert",
                8.00, 8.99, "$8.00 - $8.99",
                "980 - 1280 kcal",
                "Milk, Soy, Wheat, Eggs",
                0, 1, "Official Calories / Est. Price Range",
                "Official ADQ Disclosures",
                "Verified Official Launch Price",
                "scheduled", "2026-11-02", None,
                "Official ADQ National Press Announcement (Oct 26, 2026)",
                "2026-10", "https://www.dairyqueen.com/en-us/menu/food/",
                "Officially announced on October 26, 2026; launches nationwide November 2, 2026 at participating Grill & Chill locations. Features a +$2.00 upgrade to a Small Blizzard."
            )
        ]

        cursor.executemany("""
            INSERT INTO menu_items (
                category_id, name, slug, description, sizes_available,
                price_min, price_max, price_formatted, calories, allergens,
                is_seasonal, is_active, verification_status,
                nutrition_verified, price_verification, promotion_status,
                effective_start_date, effective_end_date, source_title,
                last_verified, source_url, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, menu_items)

        print(f"Seeded {len(menu_items)} verified menu items.")

        print("Seeding cornerstone editorial articles...")
        articles = [
            (
                "Dairy Queen Blizzard Menu & Flavors: Complete 2026 Guide",
                "dairy-queen-blizzard-menu-flavors",
                "Dairy Queen Blizzard Menu & Flavors (2026 Guide) | DQ Menu Guidance",
                "Complete guide to Dairy Queen Blizzard flavors: core Candy Classics, Royal filled creations, Holiday Cookie Swap collection, and Fall seasonal rotations.",
                None,
                "A comprehensive breakdown of all current Dairy Queen Blizzard flavors, mix-in formulas, custom ordering rules, and seasonal release schedules across US locations.",
                """<h2>The World of Dairy Queen Blizzard® Treats</h2>
<p>Since its revolutionary introduction in 1985, the Dairy Queen Blizzard® has stood as the benchmark for soft-serve ice cream treats. By blending thick, creamy vanilla soft serve with cookies, candies, brownies, and rich sauces at high velocity, Dairy Queen created a dessert so thick it defies gravity during the iconic upside-down flip test.</p>

<h2>Core Candy Classics & Timeless Favorites</h2>
<p>While Dairy Queen regularly introduces limited-edition rotational menus, several flagship recipes remain permanent fixtures at nearly every Grill & Chill and Treat store nationwide:</p>
<ul>
    <li><strong>OREO® Cookie Blizzard:</strong> The #1 all-time best seller. High-overrun vanilla soft serve blended with crunchy chocolate OREO cookie crumbles and creme.</li>
    <li><strong>Reese's® Peanut Butter Cup Blizzard:</strong> Chunks of real milk chocolate peanut butter cups blended with thick soft serve.</li>
    <li><strong>Butterfinger® Blizzard:</strong> Crisp, peanut-buttery Butterfinger bar pieces delivering signature honeycomb crunch.</li>
    <li><strong>Chocolate Chip Cookie Dough Blizzard:</strong> Soft, chewy cookie dough nuggets and rich cocoa fudge chunks.</li>
    <li><strong>Turtle Pecan Cluster Blizzard:</strong> Roasted whole pecans, caramel sauce, and chocolate confectionery coating.</li>
    <li><strong>Choco Brownie Extreme Blizzard:</strong> Triple-chocolate decadence featuring chewy brownie pieces, choco chunks, and cocoa fudge.</li>
</ul>

<h2>2026 Seasonal Collections</h2>
<p>Throughout the year, Dairy Queen rotates seasonal collections celebrating seasonal flavors:</p>
<ul>
    <li><strong>Holiday Cookie Swap Collection:</strong> Features Peanut Butter Blossom made with Hershey's Mini Kisses and Peppermint Bark Blizzard treats.</li>
    <li><strong>Fall Seasonal Lineup:</strong> Headlined by the iconic Pumpkin Pie Blizzard, Brown Sugar Cookie Dough, and Caramel Apple Cheesecake.</li>
</ul>

<h2>Custom Mix-Ins & Secret Combinations</h2>
<p>Most franchise stores permit customers to customize treats by requesting extra mix-ins, swapping chocolate soft serve for vanilla, or creating mashups like OREO with hot fudge or Reese's with cheesecake chunks.</p>""",
                cat_map["blizzards"],
                "published", 1, "DQ Menu Guidance Editorial Staff",
                "2026-10-26", "2026-10-28",
                json.dumps([
                    {"title": "American Dairy Queen Corporation Official Blizzard Menu", "url": "https://www.dairyqueen.com/en-us/menu/blizzards/"},
                    {"title": "ADQ Nutritional Food Fact Charts", "url": "https://www.dairyqueen.com/en-us/nutrition-allergens/"}
                ]),
                "verified"
            ),
            (
                "Dairy Queen Menu With Prices: 2026 Complete US Guide & Local Price Tracker",
                "dairy-queen-menu-with-prices",
                "Dairy Queen Menu With Prices (2026 Guide) | DQ Menu Guidance",
                "Detailed, verified Dairy Queen menu and price overview for US consumers. Check current prices for Blizzards, Stackburgers, ice cream cakes, and meal deals.",
                None,
                "An authoritative breakdown of Dairy Queen's US menu structure, pricing dynamics across Grill & Chill versus Treat stores, and how franchise ownership affects local checkout totals.",
                """<h2>Understanding How Dairy Queen Pricing Works in the United States</h2>
<p>If you have ever ordered an OREO® Blizzard in suburban Ohio and paid $4.79, only to order the exact same 16-ounce treat in downtown Seattle or an airport concourse and see $6.49 on your receipt, you have experienced Dairy Queen's decentralized franchise pricing model.</p>
<p>Unlike vertically integrated fast-food chains with mandatory corporate pricing caps, more than 99% of the roughly 4,300 American Dairy Queen locations are owned and operated by independent franchisees. While American Dairy Queen Corporation (ADQ) distributes suggested retail price guidelines, individual store owners retain contractual freedom to set retail prices based on local minimum wage laws, real estate costs, electricity rates for continuous refrigeration, and freight shipping surcharges.</p>

<h2>Grill & Chill vs. Treat-Only Locations</h2>
<p>One of the most frequent consumer confusions involves the menu disparity between location formats:</p>
<ul>
    <li><strong>DQ® Grill & Chill®:</strong> Full-scale restaurants serving both hot food (Signature Stackburgers, chicken strip baskets, fries, onion rings) and the complete dessert line. These locations represent the vast majority of standalone drive-thru stores built since 2002.</li>
    <li><strong>DQ® Treat Stores:</strong> Smaller storefronts—frequently found in shopping malls, strip centers, seasonal boardwalks, and classic walk-up counters—that possess no commercial fryers or grills. These stores serve strictly soft serve, Blizzards, shakes, and pre-packaged freezer cakes.</li>
</ul>

<h2>Core US Menu & Estimated Price Overview</h2>
<div class="table-responsive my-6">
    <table class="table-editorial">
        <thead>
            <tr>
                <th>Category</th>
                <th>Popular Menu Item</th>
                <th>Standard Sizes</th>
                <th>Estimated US Price Range</th>
                <th>Verification Status</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Blizzard® Treats</strong></td>
                <td>OREO® / Reese's® / Butterfinger®</td>
                <td>Mini, Small, Med, Large</td>
                <td>$3.79 – $6.59</td>
                <td><span class="badge badge-success">Verified Official</span></td>
            </tr>
            <tr>
                <td><strong>Signature Stackburgers</strong></td>
                <td>Bacon Two-Cheese / FlameThrower®</td>
                <td>Double Solo, Triple Solo</td>
                <td>$7.79 – $9.69</td>
                <td><span class="badge badge-success">Verified Official</span></td>
            </tr>
            <tr>
                <td><strong>Chicken Strip Baskets</strong></td>
                <td>4-Piece & 6-Piece Baskets</td>
                <td>With Fries & Texas Toast</td>
                <td>$9.99 – $13.49</td>
                <td><span class="badge badge-success">Verified Official</span></td>
            </tr>
            <tr>
                <td><strong>Celebration Cakes</strong></td>
                <td>8" & 10" Round Cakes</td>
                <td>Serves 8 – 16</td>
                <td>$31.24 – $38.74</td>
                <td><span class="badge badge-success">Verified Official</span></td>
            </tr>
            <tr>
                <td><strong>Value Promotions</strong></td>
                <td>$7 Meal Deal (+$2 Blizzard Upgrade)</td>
                <td>Entrée, Fries, Drink, Dessert</td>
                <td>$7.00 ($9.00 with Blizzard)</td>
                <td><span class="badge badge-success">Active Deal</span></td>
            </tr>
        </tbody>
    </table>
</div>""",
                cat_map["blizzards"],
                "published", 1, "DQ Menu Guidance Editorial Staff",
                "2026-10-26", "2026-10-28",
                json.dumps([
                    {"title": "American Dairy Queen Corporation Official Menu", "url": "https://www.dairyqueen.com"},
                    {"title": "ADQ Nutritional Food Fact Charts", "url": "https://www.dairyqueen.com/en-us/nutrition-allergens/"}
                ]),
                "verified"
            ),
            (
                "Dairy Queen Blizzard Prices and Sizes: 2026 Cost-Per-Ounce Analysis",
                "dairy-queen-blizzard-prices-sizes",
                "Dairy Queen Blizzard Prices and Sizes (2026) | DQ Menu Guidance",
                "A fluid-ounce and price-per-ounce value comparison of Mini, Small, Medium, and Large Dairy Queen Blizzards across US franchise regions.",
                None,
                "Detailed mathematical breakdown comparing fluid ounce capacity and pricing across Mini, Small, Medium, and Large cups to calculate actual value per dollar.",
                """<h2>Blizzard Sizes and Volume Math</h2>
<p>Dairy Queen serves Blizzards in four standardized paper cup sizes. However, because cup geometry widens toward the rim, volume scales faster than height:</p>
<div class="table-responsive my-6">
    <table class="table-editorial">
        <thead>
            <tr>
                <th>Cup Size</th>
                <th>Volume (fl oz)</th>
                <th>National Avg Price</th>
                <th>Cost per Ounce</th>
                <th>Average Calories</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Mini</strong></td>
                <td>6 fl oz</td>
                <td>$3.79</td>
                <td>$0.63 / oz</td>
                <td>350 – 450 kcal</td>
            </tr>
            <tr>
                <td><strong>Small</strong></td>
                <td>12 fl oz</td>
                <td>$4.89</td>
                <td>$0.41 / oz</td>
                <td>560 – 710 kcal</td>
            </tr>
            <tr>
                <td><strong>Medium</strong></td>
                <td>16 fl oz</td>
                <td>$5.79</td>
                <td>$0.36 / oz</td>
                <td>760 – 990 kcal</td>
            </tr>
            <tr>
                <td><strong>Large</strong></td>
                <td>21 fl oz</td>
                <td>$6.59</td>
                <td>$0.31 / oz</td>
                <td>1,020 – 1,340 kcal</td>
            </tr>
        </tbody>
    </table>
</div>""",
                cat_map["blizzards"],
                "published", 1, "DQ Menu Guidance Editorial Staff",
                "2026-10-26", "2026-10-28",
                json.dumps([
                    {"title": "ADQ Nutrition and Portion Sizing", "url": "https://www.dairyqueen.com/en-us/nutrition-allergens/"}
                ]),
                "verified"
            ),
            (
                "Dairy Queen Ice Cream Cakes: 2026 Prices, Sizes, Servings & Ordering Guide",
                "dairy-queen-cake-prices-sizes",
                "Dairy Queen Cake Prices & Sizes (2026 Guide) | DQ Menu Guidance",
                "Cost per slice, dimension comparison, and ordering timelines for 8-inch, 10-inch, sheet cakes, and Blizzard cakes.",
                None,
                "How much does a Dairy Queen cake cost? Dimensions, slice yields, cost-per-person analysis, and ordering rules across US locations.",
                """<h2>2026 Cake Pricing and Serving Breakdown</h2>
<div class="table-responsive my-6">
    <table class="table-editorial">
        <thead>
            <tr>
                <th>Cake Size & Style</th>
                <th>Dimensions</th>
                <th>Servings</th>
                <th>National Avg Price</th>
                <th>Cost per Serving</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>8-Inch Round</strong></td>
                <td>8" Diameter</td>
                <td>8 – 10 slices</td>
                <td>$31.24 – $34.99</td>
                <td>~$3.50</td>
            </tr>
            <tr>
                <td><strong>10-Inch Round</strong></td>
                <td>10" Diameter</td>
                <td>12 – 16 slices</td>
                <td>$34.99 – $38.74</td>
                <td>~$2.60</td>
            </tr>
            <tr>
                <td><strong>8-Inch Blizzard® Cake</strong></td>
                <td>8" Diameter</td>
                <td>8 – 10 slices</td>
                <td>$34.99</td>
                <td>~$3.80</td>
            </tr>
            <tr>
                <td><strong>11" x 14" Sheet Cake</strong></td>
                <td>11" x 14" Rectangle</td>
                <td>20 – 24 slices</td>
                <td>$42.99 – $54.99</td>
                <td>~$2.15</td>
            </tr>
            <tr>
                <td><strong>Treatzza Pizza®</strong></td>
                <td>Pre-sliced Crust</td>
                <td>6 – 8 slices</td>
                <td>$14.99 – $18.99</td>
                <td>~$2.10</td>
            </tr>
        </tbody>
    </table>
</div>""",
                cat_map["cakes"],
                "published", 1, "DQ Menu Guidance Editorial Staff",
                "2026-10-26", "2026-10-28",
                json.dumps([
                    {"title": "Dairy Queen Cake Ordering Platform", "url": "https://www.dairyqueen.com/en-us/menu/cakes/"}
                ]),
                "verified"
            ),
            (
                "Dairy Queen Signature Stackburgers: Menu, Flavors & FlameThrower Review",
                "dairy-queen-burger-menu-stackburgers",
                "Dairy Queen Burger Menu & Stackburgers (2026) | DQ Menu Guidance",
                "An examination of DQ's seasoned beef Stackburger platform, comparing calorie loads, sauces, and combo meal values.",
                None,
                "In-depth guide to Dairy Queen's 100% seasoned fresh beef Stackburgers, including the Bacon Two-Cheese Deluxe and fiery FlameThrower.",
                """<h2>The Signature Stackburger Lineup</h2>
<p>Launched to elevate DQ's savory reputation, Stackburgers feature seasoned 1/6 lb ground beef patties, melted dual cheeses placed strategically between meat layers, and toasted bakery buns.</p>
<div class="table-responsive my-6">
    <table class="table-editorial">
        <thead>
            <tr>
                <th>Stackburger Style</th>
                <th>Double Solo</th>
                <th>Triple Solo</th>
                <th>Combo Meal (Avg)</th>
                <th>Calories</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Bacon Two-Cheese Deluxe</strong></td>
                <td>$7.79</td>
                <td>$9.29</td>
                <td>$10.87</td>
                <td>710 – 980 kcal</td>
            </tr>
            <tr>
                <td><strong>FlameThrower® Stackburger</strong></td>
                <td>$8.19</td>
                <td>$9.69</td>
                <td>$10.87</td>
                <td>740 – 1,010 kcal</td>
            </tr>
            <tr>
                <td><strong>Original Double Cheeseburger</strong></td>
                <td>$4.69</td>
                <td>N/A</td>
                <td>$7.39</td>
                <td>540 kcal</td>
            </tr>
        </tbody>
    </table>
</div>""",
                cat_map["burgers"],
                "published", 1, "DQ Menu Guidance Editorial Staff",
                "2026-10-26", "2026-10-28",
                json.dumps([
                    {"title": "Dairy Queen Official Food Menu", "url": "https://www.dairyqueen.com/en-us/menu/food/"}
                ]),
                "verified"
            ),
            (
                "Dairy Queen Deals & $7 Meal Deal Guide (With 2026 Transition Analysis)",
                "dairy-queen-deals-coupons-meal-deal",
                "Dairy Queen Deals & $7 Meal Deal (2026 Guide) | DQ Menu Guidance",
                "How to maximize value at Dairy Queen using the $7 Meal Deal, DQ Rewards app coupons, 85-cent Blizzard promotions, and Free Cone Day.",
                None,
                "Guide to Dairy Queen savings strategies, detailing the $7 Meal Deal with its $2 Blizzard upgrade, app rewards, and limited-time coupons.",
                """<h2>The $7 Meal Deal & Upcoming Transition</h2>
<p>The $7 Meal Deal remains one of the best fast-food values in the country, bundling an entrée, fries, 21oz drink, and sundae. Customers can upgrade the sundae to a Small Blizzard for just $2.00.</p>""",
                cat_map["deals"],
                "published", 1, "DQ Menu Guidance Editorial Staff",
                "2026-10-26", "2026-10-28",
                json.dumps([
                    {"title": "Dairy Queen Official Deals", "url": "https://www.dairyqueen.com/en-us/deals-and-coupons/"}
                ]),
                "verified"
            ),
            (
                "Dairy Queen Breakfast Menu & Operating Hours: Complete Regional Guide",
                "dairy-queen-breakfast-menu-hours",
                "Dairy Queen Breakfast Menu & Hours (2026) | DQ Menu Guidance",
                "Where to find breakfast at Dairy Queen: Texas Country Foods, biscuit platters, morning operating hours, and how to confirm participating stores.",
                None,
                "Comprehensive guide to Dairy Queen's regional morning service, explaining why only select Texas and Southern locations serve breakfast.",
                """<h2>Regional Breakfast Service</h2>
<p>Breakfast is served primarily at Texas Dairy Queen locations and select rural Southern franchises. Most Northern and mall locations open at 10:30 AM or 11:00 AM.</p>""",
                cat_map["breakfast"],
                "published", 1, "DQ Menu Guidance Editorial Staff",
                "2026-10-26", "2026-10-28",
                json.dumps([
                    {"title": "Texas Dairy Queen Operators' Council Official Site", "url": "https://dqtexas.com/"}
                ]),
                "verified"
            )
        ]

        for art in NEW_ARTICLES:
            articles.append((
                art["title"],
                art["slug"],
                art["meta_title"],
                art["meta_description"],
                None,
                art["summary"],
                art["content"],
                cat_map.get(art["category_slug"], cat_map["blizzards"]),
                "published",
                0,
                art["author"],
                art["published_at"],
                art["updated_at"],
                json.dumps(art["sources"]),
                "verified"
            ))

        cursor.executemany("""
            INSERT INTO articles (
                title, slug, meta_title, meta_description, canonical_url, 
                summary, content, category_id, status, is_cornerstone, 
                author, published_at, updated_at, sources_json, review_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, articles)

        print("Seeding FAQs...")
        faqs = [
            (
                cat_map["blizzards"],
                "Why do Dairy Queen employees flip the Blizzard upside down?",
                "The upside-down flip test was introduced in 1985 to prove the thickness and quality of Dairy Queen's soft serve. The low air overrun and cold blending temperature create sufficient viscosity so the treat defies gravity without spilling. Many participating stores enforce an 'Upside Down or Next One's Free' policy at the drive-thru window.",
                1, 1
            ),
            (
                cat_map["blizzards"],
                "What is the most popular Blizzard flavor of all time?",
                "The OREO® Cookie Blizzard has consistently ranked as the #1 best-selling flavor across North America since its launch in 1985, followed closely by Reese's® Peanut Butter Cup and Chocolate Chip Cookie Dough.",
                2, 1
            ),
            (
                cat_map["cakes"],
                "Do I need to order a Dairy Queen ice cream cake in advance?",
                "Not necessarily. Most DQ Grill & Chill and Treat stores maintain a pre-decorated display freezer stocked with 8-inch and 10-inch round cakes that can be purchased immediately on a walk-in basis with complimentary custom lettering piped on the spot. However, custom designs, photo cakes, Blizzard cakes, or 11x14 sheet cakes generally require 24 to 48 hours notice.",
                3, 1
            ),
            (
                cat_map["burgers"],
                "What is the difference between a DQ Grill & Chill and a regular Dairy Queen?",
                "DQ Grill & Chill restaurants feature full commercial hot kitchens serving Signature Stackburgers, chicken strip baskets, fries, and warm meals alongside soft serve. Traditional Treat-only stores only possess soft serve machines and blenders, offering zero hot food.",
                4, 1
            ),
            (
                cat_map["deals"],
                "Does Dairy Queen still have the $5 Buck Lunch?",
                "The original $5 Buck Lunch was phased out nationwide and replaced by the $6 Meal Deal, and subsequently updated to the current $7 Meal Deal at participating locations. The package includes an entrée, fries, drink, and sundae.",
                5, 1
            ),
            (
                cat_map["nutrition"],
                "Does Dairy Queen offer non-dairy or vegan soft serve?",
                "While soft serve dispensed from the machines contains cow's milk dairy, Dairy Queen sells a factory-packaged Non-Dairy Dilly® Bar made with coconut cream and chocolate coating. It is certified vegan and gluten-free.",
                6, 1
            ),
            (
                cat_map["breakfast"],
                "Does every Dairy Queen serve breakfast?",
                "No. Breakfast is served primarily at Texas Dairy Queen locations and select rural Southern franchises. Most Northern and mall locations do not open until 10:30 AM or 11:00 AM.",
                7, 1
            ),
            (
                cat_map["deals"],
                "How do I get free Dairy Queen treats on my birthday?",
                "By signing up for the official DQ® Rewards program in the mobile app, members receive an annual birthday coupon (typically a buy-one-get-one Blizzard offer or discounted treat) delivered to their account wallet during their birth month.",
                8, 1
            ),
            (
                cat_map["breakfast"],
                "What time does Dairy Queen close tonight / open today / on Sundays?",
                "Standard Dairy Queen operating hours vary by franchise location and store format. Most DQ Grill & Chill restaurants open their dining rooms between 10:00 AM and 10:30 AM for lunch service, while Texas Country Foods locations serving breakfast open earlier at 6:00 AM or 7:00 AM daily. On weekdays, dining room lobbies typically close between 9:30 PM and 10:00 PM, while drive-thru windows commonly stay open until 10:30 PM, 11:00 PM, or midnight on Fridays and Saturdays. On Sundays, DQ stores typically open at 10:30 AM or 11:00 AM and close at 9:30 PM or 10:00 PM. Always check the official DQ app or local store locator to confirm closing times tonight.",
                9, 1
            ),
            (
                cat_map["breakfast"],
                "Does Dairy Queen serve breakfast all day or when does it end?",
                "No, Dairy Queen does not serve breakfast all day. Morning breakfast is offered primarily across Texas Dairy Queen (Texas Country Foods) locations and select Southern franchises. At participating locations, Dairy Queen stops serving breakfast at 10:30 AM Monday through Friday, and at 11:00 AM on Saturdays and Sundays. At cutoff time, kitchen grills and commercial fryers switch over entirely to the lunch menu, Stackburgers™, and chicken strip baskets.",
                10, 1
            ),
            (
                cat_map["blizzards"],
                "How much is an ice cream cake or a large Blizzard at Dairy Queen?",
                "In 2026, a Large (21 oz) Blizzard costs between $5.99 and $7.19 (national average $6.59), with Royal core-filled Blizzards averaging $6.99 to $7.49. Medium Blizzards cost $5.29 – $6.29 and Small Blizzards cost $4.69 – $5.49. Dairy Queen ice cream cakes range from $16.99–$21.99 for a 6-inch Mini (serves 2–4), $26.99–$34.99 for an 8-inch round (serves 8–10), $31.99–$41.99 for a 10-inch round (serves 12–16), and $42.99–$54.99 for an 11\" x 14\" Sheet Cake (serves 20–24).",
                11, 1
            ),
            (
                cat_map["nutrition"],
                "Does Dairy Queen have dairy-free or gluten-free options / fries?",
                "Yes, with important allergen distinctions. For dairy-free diners, Dairy Queen offers factory-sealed Non-Dairy Dilly® Bars made with coconut cream and vegan chocolate shell (traditional soft serve contains milk). For gluten-conscious guests, soft serve in a cup, vanilla shakes, and sundaes (chocolate, strawberry, hot fudge) contain no gluten ingredients. However, Dairy Queen french fries are cooked in shared commercial fryers with breaded chicken strips and onion rings, so they carry a cross-contact risk for individuals with Celiac disease.",
                12, 1
            ),
            (
                cat_map["cakes"],
                "How to order Dairy Queen ice cream cakes online?",
                "You can easily order custom Dairy Queen ice cream cakes online at DQCakes.com or through the official DQ mobile app. Select your preferred store, choose between 8-inch round (serves 8–10), 10-inch round (serves 12–16), or sheet cake sizes, customize your Blizzard flavor layer or classic fudge crunch center, and personalize with custom icing colors, edible photo prints, and celebration messages. Custom orders require 24 to 48 hours advance notice, while pre-made classic cakes can be bought directly from the store freezer case anytime.",
                13, 1
            ),
            (
                cat_map["breakfast"],
                "Is Dairy Queen open on holidays (Fourth of July, Easter, Thanksgiving, New Year)?",
                "Most Dairy Queen locations are open on the Fourth of July, Memorial Day, and Labor Day with normal summer operating hours. Locations frequently operate with reduced hours on Easter Sunday, Christmas Eve, and New Year's Day. However, virtually all Dairy Queen restaurants nationwide are closed on Thanksgiving Day and Christmas Day to allow franchise staff time with family. Check your local DQ store in the mobile app for specific holiday schedules.",
                14, 1
            ),
            (
                cat_map["drinks"],
                "Does Dairy Queen still sell Orange Julius?",
                "Yes, select co-branded 'DQ / Orange Julius' stores and shopping mall kiosks continue to sell Orange Julius smoothies, including the Original Orange Julius®, Strawberry Banana, Mango Pineapple, and Tripleberry Fruit Smoothies. While American Dairy Queen Corporation largely phased out the Orange Julius co-branding for new standalone Grill & Chill locations starting in 2019 (favoring Misty® Slushes and premium shakes), hundreds of legacy locations and mall treat centers continue blending Orange Julius favorites daily.",
                15, 1
            )
        ]

        cursor.executemany("""
            INSERT INTO faqs (category_id, question, answer, display_order, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, faqs)

        print("Seeding initial secure administrator account...")
        admin_pass = settings.ADMIN_INITIAL_PASSWORD or "DqPriceGuide2026!Admin"
        admin_hash = hash_password(admin_pass)
        cursor.execute("""
            INSERT INTO admin_users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("editorial_admin", "editor@menupriceguide.com", admin_hash, "admin", datetime.now().isoformat()))

        conn.commit()
        print("Database seed completed successfully.")

if __name__ == "__main__":
    seed_all(force=True)
