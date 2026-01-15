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
        This method is called for EVERY restaurant the spider yields
        
        Args:
            item: Dictionary with restaurant data {'name': ..., 'city': ...}
            spider: The spider instance
            
        Returns:
            item: The same item (allows other pipelines to process it)
        """
        try:
            # Create a Restaurant object from the scraped data
            restaurant = Restaurant(
                name=item['name'],
                city=item['city'],
                source=item['source']
            )
            
            # Add to database session (staged, not saved yet)
            self.session.add(restaurant)
            
            # Commit to database (actually save it)
            self.session.commit()
            
            spider.logger.info(f"✅ Saved: {item['name']}")
            
        except IntegrityError:
            # This happens if restaurant already exists (duplicate)
            self.session.rollback()  # Undo the failed add
            spider.logger.warning(f"⚠️ Duplicate: {item['name']} (already in database)")
            
        except Exception as e:
            # Any other error
            self.session.rollback()
            spider.logger.error(f"❌ Error saving {item['name']}: {e}")
        
        # Always return the item (important for Scrapy)
        return item
            