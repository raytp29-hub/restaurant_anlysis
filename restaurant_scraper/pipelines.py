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
        Process each item scraped by the spider
        """
        try:
            # Create a Restaurant object from ALL scraped data
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
            
            spider.logger.info(f"✅ Saved: {item['name']} - Rating: {item.get('rating_avg')} - Cuisines: {item.get('cuisine_type')}")
            
        except IntegrityError:
            self.session.rollback()
            spider.logger.warning(f"⚠️ Duplicate: {item['name']}")
            
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"❌ Error saving {item['name']}: {e}")
        
        return item