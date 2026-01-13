from restaurant_scraper.database.connection import SessionLocal
from restaurant_scraper.database.models import Restaurant, MenuItem



def test_insert_data():
    """Test inserting a restaurant and menu items"""
    
    # Create session
    session = SessionLocal()
    
    try:
        # Create a restaurant
        restaurant = Restaurant(
            name="Ristorante Fichera",
            address="Via Umberto I, 3",
            city="Catania",
            latitude=37.5024,
            longitude=15.0873,
            cuisine_type="Sicilian",
            price_range="€€",
            rating_avg=4.5,
            total_reviews=156,
            source="tripadvisor"
        )
        
        # Add to session
        session.add(restaurant)
        session.commit()  # This saves to database and assigns an ID
        
        print(f"✅ Restaurant created with ID: {restaurant.id}")
        print(f"   Name: {restaurant.name}")
        
        # Create menu items for this restaurant
        menu_items = [
            MenuItem(
                restaurant_id=restaurant.id,
                dish_name="Arancini al Ragù",
                description="Traditional Sicilian rice balls with meat sauce",
                price=3.50,
                category="antipasti"
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                dish_name="Pasta alla Norma",
                description="Pasta with eggplant, tomato, and ricotta salata",
                price=12.00,
                category="primi"
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                dish_name="Cannoli Siciliani",
                description="Crispy pastry filled with sweet ricotta",
                price=5.00,
                category="dessert"
            )
        ]
        
        # Add all menu items
        session.add_all(menu_items)
        session.commit()
        
        print(f"✅ Added {len(menu_items)} menu items")
        
        # Query and display
        print("\n📋 Menu Items:")
        for item in menu_items:
            print(f"   - {item.dish_name}: €{item.price}")
        
        # Test relationship
        print(f"\n🔗 Restaurant has {len(restaurant.menu_items)} menu items (via relationship)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

def test_query_data():
    """Test querying data"""
    session = SessionLocal()
    
    try:
        # Query all restaurants
        restaurants = session.query(Restaurant).all()
        print(f"\n📊 Found {len(restaurants)} restaurant(s) in database:")
        
        for rest in restaurants:
            print(f"\n{rest}")
            print(f"   Menu items: {len(rest.menu_items)}")
            
    finally:
        session.close()

if __name__ == "__main__":
    print("🧪 Testing Database Operations...\n")
    test_insert_data()
    test_query_data()
    print("\n✅ All tests completed!")