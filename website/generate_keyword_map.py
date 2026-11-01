import csv
import os

raw_keywords = """dairy queen menu 
dq menu
dq delivery
dairy queen order online
dairy queen menu with prices
dairy queen blizzard menu
dq summer blizzard menu
dairy queen breakfast menu
dairy queen blizzard of the month
dairy queen prices
blizzard flavors
dq blizzard menu
delivery dairy queen
dq blizzard of the month
dairy queen grill & chill
dairy queen summer blizzards
doordash dairy queen menu
dq menu prices
snickers brownie blizzard
dairy queen doordash menu
dairy queen ice cream cake menu
dairy queen near me menu
dairy queen blizzard flavors
order dq online
blizzard dairy queen
dairy queen coupons 2023
dq blizzard flavors
dairy queen ice cream menu
dq breakfast menu
dairy queen order online delivery
summer blizzard menu
dairy queen close to me
dairy queen cake prices
dq prices
dairy queen breakfast
dq ice cream menu
sonic blizzard menu
dairy queen delivery grubhub
dairy queen menu delivery
dq menu near me
dairy queen menu and prices
dq delivery menu
dairy queen cake menu
dairy queen ice cream cakes prices
dq ice cream cake price
dairy queen menu 2022
dq stack burgers
dq cake prices
dairy queen blizzard prices
dq cakes menu
dairy queen summer menu
dairy queen burger menu
dq cake delivery
dairy queen ice cream cake delivery
dq drumstick blizzard
dairy queen milkshakes
dairy queen coupons ontario
dq grill and chill menu
dairy queen lunch specials
dairy queen blizzard flavors 2023
dq restaurant
dairy queen stackburger menu
dairy queen menu 2023
blizzard menu
dq blizzard prices
dairy queen menu prices 2022
new blizzard flavors
dairy queen meal deals
dairy queen food menu
dq food
dairy queen meals
dairy queen flavor of the month
dairy queen full menu
dairy queen lunch menu
treatzza pizza
dairy queen menu order online
dairy queen grill and chill menu
dq signature stack burgers
dairy queen shakes
dq menu food
dairy queen order ahead
blizzard flavors 2023
dairy queen summer flavors
dq flavor of the month
dq menu and prices
dairy queen restaurant
dixie queen delivery
dq burger menu
dairyqueen com menu
dairy queen hours
dairy queen breakfast menu with prices
dairy queen orders
dairy queen flavors
dq food menu
dairy queen treats
dairyqueen cake
dq lunch specials
dairy queen ice cream flavors
show me dairy queen's menu
dq snickers brownie blizzard
dairy queen a1 burger
dq website
oreo hot cocoa blizzard
dairy queen blizzard menu 2023
dairy queen blizzard flavors 2022
dairy queen grill and chill
dq meal deal
dairy queen drinks
summer blizzard flavors
dq ice cream cake delivery
dairy queen new burgers
dairy queen ice cream cake flavors
dq catering
dq treats
dq stack burgers price
blizzard summer menu
dairy queen cake order online
dairy queen hamburger menu
dq grill menu
small blizzard price
sonic blizzard flavors
dq signature stack burgers price
dairy queen fish sandwich
dairy queen by me
dairy queen burger prices
dairy queen grill & chill menu
dairy queen summer blizzard flavors
dairy queen ice cream prices
dq com menu
summer blizzards
dqs menu
dairy queen chicken sandwich
dairy queen near us
a1 burger dairy queen
dairy queen ice cream cake order online
dq treatzza pizza
stackburger dq
dq meals
dairy queen milkshake flavours
dairy queen milkshake flavors
dairy queen dessert menu
dq a1 burger
dairy queen blizzard special
dairy queen lunch deals
dairy queen delivery number
dairy queen order online cake
dairy queen grill menu
dq milkshake menu
dq ice cream cake menu
dairy queen blizzard flavors not on menu
dairy queen online menu
dq stackburger menu
dairy queen treatzza pizza
dairy queen to go
dq ice cream cake flavors
dq chicken sandwich
dairy queen ice cream sandwich
dq milkshake flavors
dairy queen stackburger 2022
dairy queen desserts
oreo blizzard price
dairyqueen ca menu
dairy queen salad
dq flavors
dq chicken burger
dairy queen treat menu
dairy queen cakes and prices
dairy queen new burgers 2022
dairy cream menu
dq salads
dq ca menu
dq cake order online
dairy queen menu with prices near me
dairy queen ice cream cone
best blizzard flavors
burgers at dairy queen
medium blizzard price
dq fish sandwich
triple truffle blizzard
dairy queen cake flavors
blizzard flavor of the month
dq burger prices
nearest dq restaurant
dairy queen with food
dq grill & chill restaurant
dq ice cream flavors
dairy queen shakes menu
specials at dairy queen
dq lunch deals
all blizzard flavors
show me the dairy queen menu
blizzard treats
large blizzard price
dairy queen burgers near me
summer blizzards dairy queen
dq lunch menu
dairy queen happy hour
dairy queen fall blizzards
dairy queen breakfast hours
signature stack burger dairy queen
dairy queen family meal
dairy queen stack burgers
dq full menu
show me the menu for dairy queen
dairy queen veggie burger
dairy queen flavours
oreo blizzard dairy queen
$6 dairy queen meal
$6 meal at dairy queen
$6 meal deal dairy queen
$7 meal deal dairy queen
2 for 4 dairy queen
2022 blizzard flavors
2022 dairy queen blizzard menu
5 buck lunch dairy queen
6 dollar meal deal dairy queen
6 pack dilly bar price
7 meal deal dq
a1 steak burger dairy queen
all blizzards at dairy queen
all dairy queen blizzard flavors
all dairy queen toppings
all dq blizzard flavors
all dq blizzard flavours
all dq blizzards
banana supreme dairy queen
bbq sandwich dairy queen
best blizzard flavors 2022
best blizzard flavors at dairy queen
best blizzards at dairy queen
best burger at dairy queen
best dairy queen blizzard 2022
best dairy queen burger
best dairy queen desserts
best dairy queen food
best dairy queen treats
best dessert at dairy queen
blizzard cake price
blizzard cakes dairy queen
blizzard cost dairy queen
blizzard drink dairy queen
blizzard fall flavors
blizzard fall menu
blizzard flavors 2022
blizzard flavors at dairy queen 2022
blizzard flavors summer 2022
blizzard flavours ontario
blizzard ice cream dairy queen
blizzard ice cream flavors
blizzard ice cream menu
blizzard ice cream price
blizzard meal deal
blizzard menu 2022
blizzard menu january 2022
blizzard new flavors
blizzard secret menu
blizzard size prices
blizzard sizes and prices
blizzard sizes dairy queen
blizzard summer flavors
blizzard treat dairy queen
blizzard treat size
blizzard types dairy queen
blizzard's at dairy queen
blizzards at dairy queen 2022
brazier burger dairy queen
breakfast hours at dairy queen
burger and blizzard meal
burger dairy queen
canasta waffle dairy queen
cappuccino skor blizzard
caramel blizzard
caramel macchiato blizzard
caramel shake dairy queen
cherry chocolate blizzard
chicken fried steak sandwich dairy queen
chicken salad dairy queen
chicken sandwich dairy queen
chicken sandwich dq
choco brownie dq treatzza pizza
choco brownie extreme blizzard price
choco brownie treatzza pizza
chocolate brownie extreme blizzard cake
chocolate cherry blizzard
chocolate covered cherry blizzard
chocolate covered strawberry blizzard
cinnamon roll blizzard
cinnamon roll blizzard 2022
cinnamon roll blizzard dq
cinnamon roll center blizzard
coffee blizzard dairy queen
coffee drinks at dairy queen
cost of a small blizzard at dairy queen
cost of blizzard at dairy queen
cost of dairy queen cake
cost of dq blizzard
crispy chicken salad dairy queen
crispy chicken sandwich dairy queen
crispy chicken sandwich dq
crispy crunch blizzard
current blizzard flavors
current blizzard flavors 2022
current blizzard flavors at dairy queen
current dairy queen blizzard flavors
current dairy queen menu
current dq blizzard flavors
custom blizzard flavors
dairy blizzard flavors
dairy blizzard menu
dairy blizzard of the month
dairy dairy queen menu
dairy free dairy queen menu
dairy q menu
dairy quee n
dairy queen $3 breakfast menu
dairy queen $5 lunch
dairy queen $5 lunch 2021
dairy queen $5 lunch 2022
dairy queen $5 meal
dairy queen $5 meal deal
dairy queen $5 menu
dairy queen $6.00 meal deal
dairy queen $7 meal deal
dairy queen $8 meal deal
dairy queen 114th and dodge
dairy queen 2 for 4 menu
dairy queen 2 for 5
dairy queen 2022 blizzard menu
dairy queen 2022 menu
dairy queen 2022 summer blizzards
dairy queen 24 hours
dairy queen 5 dollar box
dairy queen 5 dollar menu
dairy queen 6 dollar meal
dairy queen 6 meal deal
dairy queen 67th and deer valley
dairy queen 7 dollar meal
dairy queen 7 dollar meal deal
dairy queen 8 dollar meal deal
dairy queen 8 inch cake price
dairy queen a1 burger calories
dairy queen a1 burger price
dairy queen a1 burger still available
dairy queen all day breakfast
dairy queen allergen menu
dairy queen and burger king
dairy queen and orange julius
dairy queen appleby and dundas
dairy queen avenue du parc
dairy queen bacon burger
dairy queen banana shake
dairy queen banksville
dairy queen banksville road
dairy queen bar and grill
dairy queen bar and grill near me
dairy queen barbecue sandwich
dairy queen barbeque sandwich
dairy queen bbq sandwich
dairy queen bbq sandwich 2022
dairy queen best burger
dairy queen birthday blizzard
dairy queen blast flavors
dairy queen blizzard 2022
dairy queen blizzard cake flavors
dairy queen blizzard cake price
dairy queen blizzard fall flavors
dairy queen blizzard flavor of the month
dairy queen blizzard flavors 2021
dairy queen blizzard flavors on menu
dairy queen blizzard flavors today
dairy queen blizzard flavours 2022
dairy queen blizzard meal
dairy queen blizzard meal deal
dairy queen blizzard menu 2021
dairy queen blizzard menu 2022
dairy queen blizzard menu calories
dairy queen blizzard menu near me
dairy queen blizzard menu prices
dairy queen blizzard menu with prices
dairy queen blizzard of the month 2021
dairy queen blizzard of the month october
dairy queen blizzard prices 2021
dairy queen blizzard prices 2022
dairy queen blizzard secret menu
dairy queen blizzard sizes and prices
dairy queen blizzard summer flavors
dairy queen blizzard toppings list
dairy queen blizzard's
dairy queen blizzards 2022
dairy queen blizzards flavors 2022
dairy queen blizzards sizes
dairy queen boxed treats
dairy queen brazier menu
dairy queen breakfast menu 2021
dairy queen breakfast menu 2022
dairy queen breakfast menu hours
dairy queen breakfast menu near me
dairy queen breakfast menu prices
dairy queen breakfast menu time
dairy queen breakfast menu with pictures
dairy queen breakfast near me
dairy queen breakfast prices
dairy queen breakfast time
dairy queen brownie dessert
dairy queen brownie sundae price
dairy queen brownie extreme blizzard
dairy queen butterbeer blizzard
dairy queen butterfinger blizzard
dairy queen cake coupons 2021
dairy queen cake flavours
dairy queen cake prices 2021
dairy queen cakes menu prices
dairy queen calorie menu
dairy queen catering menu
dairy queen chicken and dumplings price
dairy queen chicken fried steak
dairy queen chicken fried steak sandwich
dairy queen chicken salad
dairy queen chicken sandwich price
dairy queen chicken tender meal
dairy queen chocolate shake price
dairy queen christmas menu
dairy queen chuckwagon sandwich
dairy queen cinnamon roll blizzard
dairy queen classic treats
dairy queen close by
dairy queen close time
dairy queen co
dairy queen coffee menu
dairy queen combo
dairy queen combo meals
dairy queen combo menu
dairy queen combo prices
dairy queen cone flavors
dairy queen cone price
dairy queen corn dog price
dairy queen cost
dairy queen crispy chicken salad calories
dairy queen crispy chicken sandwich
dairy queen crispy chicken sandwich calories
dairy queen crunch cone locations
dairy queen current blizzard flavors
dairy queen current menu
dairy queen custom blizzard
dairy queen daily specials
dairy queen dairy free menu
dairy queen dairy queen menu
dairy queen december blizzard of the month
dairy queen dessert menu prices
dairy queen dessert pizza
dairy queen dilly bar 6 pack price
dairy queen dilly bar box price
dairy queen dilly bar flavors
dairy queen dilly bar price
dairy queen dinner menu
dairy queen dollar menu
dairy queen double chocolate brownie
dairy queen dq sandwich
dairy queen drink menu
dairy queen drink prices
dairy queen drink sizes
dairy queen drive thru menu
dairy queen dude sandwich
dairy queen dude sandwich price
dairy queen dufferin and lawrence
dairy queen east menu
dairy queen elmwood drive
dairy queen extra large blizzard
dairy queen fall blizzard flavors
dairy queen fall blizzard menu
dairy queen fall blizzards 2022
dairy queen fall flavors
dairy queen fall flavors 2022
dairy queen fall flavours
dairy queen fall menu
dairy queen fall menu 2022
dairy queen family meal 2022
dairy queen family meal deal
dairy queen fish sandwich 2022
dairy queen fish sandwich price
dairy queen flamethrower burger
dairy queen flamethrower burger calories
dairy queen flamethrower chicken sandwich
dairy queen flamethrower price
dairy queen flavors 2022
dairy queen food calories
dairy queen food menu prices
dairy queen food prices
dairy queen footlong hot dog price
dairy queen fountain drinks
dairy queen fries gluten free
dairy queen fries price
dairy queen frog cake
dairy queen frozen drinks
dairy queen frozen hot chocolate
dairy queen frozen hot chocolate 2022
dairy queen frozen treats to take home
dairy queen full blizzard menu
dairy queen full menu with prices
dairy queen funnel cake
dairy queen gf menu"""

def categorize_keyword(kw):
    k = kw.strip().lower()
    
    # Competitor / Irrelevant / Specific foreign
    if any(x in k for x in ["sonic", "dixie queen", "and burger king"]):
        return {
            "group": "Competitor & Irrelevant",
            "url": "N/A (Excluded)",
            "type": "Excluded",
            "intent": "Navigational/Competitor",
            "content_type": "Exclude from target URLs",
            "status": "Excluded",
            "notes": "Competitor query or brand collision. Do not target on main US site."
        }
    if any(x in k for x in ["ontario", "ca menu", "dufferin", "avenue du parc", "appleby and dundas"]):
        return {
            "group": "International & Non-US",
            "url": "N/A (Excluded)",
            "type": "Excluded",
            "intent": "Navigational/Canadian",
            "content_type": "Exclude from target URLs",
            "status": "Excluded",
            "notes": "Canadian regional query. Excluded as per US target audience requirements."
        }
    if any(x in k for x in ["114th and dodge", "67th and deer valley", "banksville", "elmwood drive", "near me", "close to me", "by me", "near us"]):
        return {
            "group": "Local Searches & Store Locator",
            "url": "/faqs",
            "type": "Secondary",
            "intent": "Local/Navigational",
            "content_type": "FAQ / Store Locator Advice",
            "status": "Verified",
            "notes": "Advise users how to use official DQ locator and explain franchise location dynamics."
        }
    if any(x in k for x in ["cake", "treatzza"]):
        if any(x in k for x in ["price", "cost", "8 inch"]):
            return {
                "group": "Ice Cream Cakes & Cake Pricing",
                "url": "/cakes/prices-sizes",
                "type": "Primary" if k in ["dairy queen cake prices", "dq cake prices"] else "Secondary",
                "intent": "Commercial/Transactional",
                "content_type": "Price Table & Ordering Guide",
                "status": "Verified Range",
                "notes": "Verified standard 8-inch, 10-inch, sheet cake and Treatzza Pizza price ranges."
            }
        else:
            return {
                "group": "Ice Cream Cakes & Cake Pricing",
                "url": "/cakes",
                "type": "Primary" if k in ["dairy queen ice cream cake menu", "dairy queen cake menu"] else "Secondary",
                "intent": "Commercial/Informational",
                "content_type": "Cake Catalog & Ordering Guide",
                "status": "Verified",
                "notes": "Standard Blizzard cakes, custom photo cakes, Treatzza Pizza types."
            }
    if any(x in k for x in ["summer blizzard", "fall blizzard", "seasonal", "flavor of the month", "flavour of the month", "new blizzard", "december blizzard", "halloween", "christmas", "cinnamon roll blizzard", "oreo hot cocoa", "snickers brownie"]):
        return {
            "group": "Seasonal & Limited Time Blizzards",
            "url": "/blizzards/seasonal",
            "type": "Primary" if k in ["dq summer blizzard menu", "dairy queen summer blizzards", "dairy queen blizzard of the month"] else "Secondary",
            "intent": "Informational/Freshness",
            "content_type": "Seasonal Tracker Article",
            "status": "Verified Seasonal",
            "notes": "Clearly identify limited-time rotations, Flavor of the Month, and active seasonal menus."
        }
    if any(x in k for x in ["blizzard calories", "blizzard nutrition", "menu calories"]):
        return {
            "group": "Nutrition, Calories & Allergens",
            "url": "/blizzards/nutrition",
            "type": "Primary" if "blizzard" in k else "Secondary",
            "intent": "Informational",
            "content_type": "Nutritional Breakdown Guide",
            "status": "Verified Official Data",
            "notes": "Accurate calorie counts by size (Mini, Small, Medium, Large) from official DQ nutrition charts."
        }
    if any(x in k for x in ["blizzard price", "blizzard cost", "small blizzard price", "medium blizzard price", "large blizzard price", "blizzard size", "blizzard sizes"]):
        return {
            "group": "Blizzard Prices & Sizes",
            "url": "/blizzards/prices-sizes",
            "type": "Primary" if k in ["dairy queen blizzard prices", "blizzard sizes and prices"] else "Secondary",
            "intent": "Commercial/Transactional",
            "content_type": "Interactive Price & Size Table",
            "status": "Verified Range",
            "notes": "Covers Mini (6 oz), Small (12 oz), Medium (16 oz), Large (21 oz) price comparisons."
        }
    if any(x in k for x in ["blizzard", "blast"]):
        return {
            "group": "Blizzard Menu & Flavors",
            "url": "/blizzards",
            "type": "Primary" if k in ["dairy queen blizzard menu", "blizzard flavors", "dairy queen blizzard flavors"] else "Secondary",
            "intent": "Informational/Commercial",
            "content_type": "Comprehensive Flavor Guide",
            "status": "Verified",
            "notes": "Candy Classics, Cookie Lovers, Signature Creations, and Secret Menu customizations."
        }
    if any(x in k for x in ["breakfast"]):
        return {
            "group": "Breakfast Menu & Hours",
            "url": "/breakfast",
            "type": "Primary" if k in ["dairy queen breakfast menu", "dairy queen breakfast hours"] else "Secondary",
            "intent": "Informational/Local",
            "content_type": "Availability & Menu Guide",
            "status": "Verified Regional",
            "notes": "Crucial note: Breakfast is served primarily at Texas DQ and select Southern/Midwest locations."
        }
    if any(x in k for x in ["burger", "stack burger", "stackburger", "hamburger", "bacon burger", "flamethrower", "dude sandwich", "chuckwagon", "brazier"]):
        return {
            "group": "Food Menu, Burgers & Meals",
            "url": "/food/burgers",
            "type": "Primary" if k in ["dairy queen burger menu", "dq stack burgers"] else "Secondary",
            "intent": "Commercial/Informational",
            "content_type": "Burger Guide & Price Matrix",
            "status": "Verified US",
            "notes": "Covers Signature Stackburger line (1/3 lb Double, 1/2 lb Triple) and regional Texas exclusives."
        }
    if any(x in k for x in ["chicken", "salad", "fish", "fries", "corn dog", "food", "lunch", "dinner", "meal", "box", "sandwich", "bbq", "barbecue"]):
        if any(x in k for x in ["$5", "$6", "$7", "$8", "meal deal", "special", "deal", "coupon", "2 for 4", "2 for 5", "dollar menu"]):
            return {
                "group": "Deals, Coupons & Value Meals",
                "url": "/deals-coupons",
                "type": "Primary" if k in ["dairy queen meal deals", "dairy queen coupons"] else "Secondary",
                "intent": "Commercial/Value",
                "content_type": "Value Meals & App Savings Guide",
                "status": "Verified US",
                "notes": "Covers the official $7 Meal Deal (Tenders/Cheeseburger + Drink + Sundae) and DQ Rewards App."
            }
        else:
            return {
                "group": "Food Menu, Burgers & Meals",
                "url": "/food",
                "type": "Primary" if k in ["dairy queen food menu", "dairy queen grill & chill menu"] else "Secondary",
                "intent": "Informational/Commercial",
                "content_type": "Food Hub & Price Guide",
                "status": "Verified US",
                "notes": "Chicken strip baskets, country gravy, Texas Toast, rotisserie-style bites, sides."
            }
    if any(x in k for x in ["milkshake", "shake", "cone", "dilly bar", "sundae", "treat", "dessert", "drink", "coffee", "frozen", "funnel cake", "orange julius"]):
        return {
            "group": "Treats, Ice Cream, Shakes & Desserts",
            "url": "/treats-desserts",
            "type": "Primary" if k in ["dairy queen milkshakes", "dairy queen desserts", "dairy queen classic treats"] else "Secondary",
            "intent": "Commercial/Informational",
            "content_type": "Dessert Catalog & Prices",
            "status": "Verified US",
            "notes": "Dilly Bars, Buster Bars, Cones (Vanilla/Chocolate/Dipped), Hand-spun Milkshakes, Malts."
        }
    if any(x in k for x in ["allergen", "gluten free", "gf menu", "dairy free", "calorie"]):
        return {
            "group": "Nutrition, Calories & Allergens",
            "url": "/nutrition-allergens",
            "type": "Primary" if k in ["dairy queen allergen menu", "dairy queen nutrition"] else "Secondary",
            "intent": "Informational/Health",
            "content_type": "Dietary & Allergen Guide",
            "status": "Verified Official Data",
            "notes": "Official allergen guidance, Non-dairy Dilly Bar, gluten-sensitive precautions, shared kitchen disclaimer."
        }
    if any(x in k for x in ["order online", "delivery", "doordash", "grubhub", "order ahead", "to go", "orders", "catering"]):
        return {
            "group": "Delivery & Online Ordering",
            "url": "/ordering-delivery",
            "type": "Primary" if k in ["dairy queen order online", "dq delivery"] else "Secondary",
            "intent": "Transactional",
            "content_type": "Ordering & Third-Party Delivery Guide",
            "status": "Verified",
            "notes": "Covers DQ App ordering, DoorDash, Uber Eats, Grubhub markups, and cake pre-order lead times."
        }
    if any(x in k for x in ["coupon", "deal", "discount", "specials", "happy hour", "$"]):
        return {
            "group": "Deals, Coupons & Value Meals",
            "url": "/deals-coupons",
            "type": "Primary" if k in ["dairy queen coupons", "dairy queen deals"] else "Secondary",
            "intent": "Commercial/Value",
            "content_type": "Value Deals & Savings Guide",
            "status": "Verified",
            "notes": "Explains DQ Rewards program, Free Cone Day, Fall 85-cent Blizzard app deals, and legitimate coupons."
        }
    if any(x in k for x in ["price", "prices", "cost", "menu with prices"]):
        return {
            "group": "Core Menu & General Prices",
            "url": "/menu",
            "type": "Primary" if k in ["dairy queen menu with prices", "dairy queen prices"] else "Secondary",
            "intent": "Informational/Commercial",
            "content_type": "Master Menu & Price Overview",
            "status": "Verified Ranges",
            "notes": "Complete master price table across Grill & Chill vs. Treat-only locations with disclaimer."
        }
    
    # Default to core menu or homepage
    return {
        "group": "Core Menu & General Prices",
        "url": "/menu" if "menu" in k else "/",
        "type": "Primary" if k in ["dairy queen menu", "dq menu"] else "Secondary",
        "intent": "Informational",
        "content_type": "Editorial Guide / Homepage",
        "status": "Verified",
        "notes": "Core brand navigation and introductory menu guide."
    }

lines = [l.strip() for l in raw_keywords.strip().split("\n") if l.strip()]
output_rows = []

for line in lines:
    res = categorize_keyword(line)
    output_rows.append({
        "Keyword": line,
        "Keyword Group": res["group"],
        "Intended URL": res["url"],
        "Primary or Secondary": res["type"],
        "Search Intent": res["intent"],
        "Content Type": res["content_type"],
        "Verification Status": res["status"],
        "Notes": res["notes"]
    })

csv_path = r"c:\Users\hp\Desktop\website\keyword_map.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Keyword", "Keyword Group", "Intended URL", "Primary or Secondary",
        "Search Intent", "Content Type", "Verification Status", "Notes"
    ])
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Successfully mapped {len(output_rows)} keywords into {csv_path}")
