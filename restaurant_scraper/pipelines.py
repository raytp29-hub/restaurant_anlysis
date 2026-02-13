# Scrapy Pipeline to save restaurant data to PostgreSQL
from restaurant_scraper.database.connection import SessionLocal
from restaurant_scraper.database.models import Restaurant, MenuItem


class PostgresPipeline:
    
    def __init__(self):
        self.session = None
        
    def open_spider(self, spider):
        self.session = SessionLocal()
        spider.logger.info("Database session opened")
    
    def close_spider(self, spider):
        if self.session:
            self.session.close()
            spider.logger.info("Database session closed")
            
    def process_item(self, item, spider):
        """Route item to correct processor"""
        if 'dish_name' in item:
            return self.process_menu_item(item, spider)
        else:
            return self.process_restaurant(item, spider)
    
    def process_menu_item(self, item, spider):
        """Salva o aggiorna un piatto del menu"""
        try:
            # Trova il ristorante per URL
            restaurant = self.session.query(Restaurant).filter_by(
                source_url=item.get('restaurant_url')
            ).first()
            
            if restaurant:
                # Cerca se il piatto esiste già
                existing = self.session.query(MenuItem).filter_by(
                    restaurant_id=restaurant.id,
                    dish_name=item.get('dish_name')
                ).first()
                
                if existing:
                    # UPDATE
                    existing.price = item.get('price')
                    self.session.commit()
                    spider.logger.info(f"🔄 Updated menu item: {item.get('dish_name')}")
                else:
                    # INSERT
                    menu_item = MenuItem(
                        restaurant_id=restaurant.id,
                        dish_name=item.get('dish_name'),
                        price=item.get('price'),
                    )
                    self.session.add(menu_item)
                    self.session.commit()
                    spider.logger.info(f"🍽️ Saved menu item: {item.get('dish_name')}")
            else:
                spider.logger.warning(f"⚠️ Restaurant not found for: {item.get('dish_name')}")
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"❌ Error saving menu item: {e}")
        
        return item
    
    def process_restaurant(self, item, spider):
        """Salva o aggiorna un ristorante"""
        try:
            existing = self.session.query(Restaurant).filter_by(
                name=item.get('name'),
                city=item.get('city')
            ).first()
            
            if existing:
                existing.source_url = item.get('source_url')
                existing.rating_avg = item.get('rating_avg')
                existing.total_reviews = item.get('total_reviews')
                existing.cuisine_type = item.get('cuisine_type')
                existing.price_range = item.get('price_range')
                existing.website = item.get('website')
                existing.address = item.get('address')
                existing.phone = item.get('phone')
                
                self.session.commit()
                spider.logger.info(f"🔄 Updated: {item['name']}")
            else:
                restaurant = Restaurant(
                    name=item.get('name'),
                    city=item.get('city'),
                    source=item.get('source'),
                    source_url=item.get('source_url'),
                    rating_avg=item.get('rating_avg'),
                    total_reviews=item.get('total_reviews'),
                    cuisine_type=item.get('cuisine_type'),
                    price_range=item.get('price_range'),
                    website=item.get('website'),
                    address=item.get('address'),
                    phone=item.get('phone'),
                )
                self.session.add(restaurant)
                self.session.commit()
                spider.logger.info(f"✅ Saved: {item['name']}")
                
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"❌ Error saving {item.get('name')}: {e}")
        
        return item