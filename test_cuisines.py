# test_cuisines.py
from restaurant_scraper.database.connection import engine
from restaurant_scraper.database.models import Restaurant, CuisineType
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

# Test 1: How many cuisines?
print(f"✅ Total cuisines: {session.query(CuisineType).count()}")

# Test 2: Show 5 restaurants with their cuisines
print("\n=== Sample Restaurants ===")
for restaurant in session.query(Restaurant).limit(5):
    print(f"\n{restaurant.name}:")
    for cuisine in restaurant.cuisines:
        print(f"  - {cuisine.name}")

# Test 3: Show how many restaurants per cuisine
print("\n=== Restaurants per Cuisine ===")
for cuisine in session.query(CuisineType).all():
    count = len(cuisine.restaurants)
    print(f"{cuisine.name}: {count} restaurants")

session.close()