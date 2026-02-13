# Scrapy Pipeline to save restaurant data to PostgreSQL
from restaurant_scraper.database.connection import SessionLocal
from restaurant_scraper.database.models import Restaurant
from sqlalchemy.exc import IntegrityError


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
        """
        Process each item - UPDATE if exists, INSERT if new
        """
        try:
            # Cerca se esiste già (per nome e città)
            existing = self.session.query(Restaurant).filter_by(
                name=item.get('name'),
                city=item.get('city')
            ).first()
            
            if existing:
                # UPDATE - aggiorna i dati esistenti
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
                # INSERT - crea nuovo record
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
            spider.logger.error(f"❌ Error saving {item['name']}: {e}")
        
        return item