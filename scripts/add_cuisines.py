# Add project root to path FIRST
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Now imports will work
from restaurant_scraper.database.connection import engine
from restaurant_scraper.database.models import Restaurant, CuisineType, RestaurantCuisine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Create session
Session = sessionmaker(bind=engine)
session = Session()  # ✅ Don't forget the ()!

# Function to add cuisine
def add_cuisine(session, cuisine_name):
    existing_cuisine = session.query(CuisineType).filter_by(name=cuisine_name).first()
    
    if existing_cuisine:
        return existing_cuisine
    else:
        new_cuisine = CuisineType(name=cuisine_name)
        session.add(new_cuisine)
        return new_cuisine

# Add cuisines
cuisine_list = ["Italian", "Seafood", "Pizza", "Mediterranean", "Sicilian", "Cafe", "International"]
cuisines = {}

for cuisine_name in cuisine_list:
    cuisine_obj = add_cuisine(session, cuisine_name)
    cuisines[cuisine_name] = cuisine_obj

# Get all restaurants
restaurants = session.query(Restaurant).all()
print(f"Found {len(restaurants)} restaurants")

# Link restaurants to cuisines
for restaurant in restaurants:
    name_lower = restaurant.name.lower()
    
    # Everyone gets Italian (it's Catania!)
    restaurant.cuisines.append(cuisines["Italian"])
    
    # Check for Pizza
    if "pizza" in name_lower:
        restaurant.cuisines.append(cuisines["Pizza"])
    
    # Check for Seafood
    if "pesce" in name_lower or "seafood" in name_lower or "mare" in name_lower:
        restaurant.cuisines.append(cuisines["Seafood"])
    
    # Check for Sicilian
    if "sicilian" in name_lower or "sicilia" in name_lower:
        restaurant.cuisines.append(cuisines["Sicilian"])
    
    # Trattoria/Locanda = Traditional Italian
    if "trattoria" in name_lower or "locanda" in name_lower or "osteria" in name_lower:
        if cuisines["Mediterranean"] not in restaurant.cuisines:
            restaurant.cuisines.append(cuisines["Mediterranean"])

print("\n=== Linking complete! ===")

# Commit changes
session.commit()
print("✅ Changes committed to database!")

# Test: Show first 3 restaurants with their cuisines
print("\n=== Test Results ===")
for restaurant in restaurants[:3]:
    print(f"\n{restaurant.name}:")
    for cuisine in restaurant.cuisines:
        print(f"  - {cuisine.name}")

session.close()