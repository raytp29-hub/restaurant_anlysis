"""
TripAdvisor Spider - Catania Restaurants
Simple version: Extract and print restaurant names
"""
import scrapy
import re

class TripAdvisorSpider(scrapy.Spider):
    
    name = 'tripadvisor'
    

    allowed_domains = ['tripadvisor.com']
    

    def __init__(self, city="Catania", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.city = city
        
        self.start_urls = [
            'https://www.tripadvisor.com/Restaurants-g187888-Catania_Province_of_Catania_Sicily.html'
        ]
        
        
    def parse(self, response):
        # Extract restaurant data
        self.logger.info(f"Scraping {self.city}...")
        
        restaurant_links = response.css('a[href*=Restaurant_Review]')
        
        
        all_names = restaurant_links.css('div.biGQs._P.SewaP::text').getall()
        
        seen = set()
        restaurants = []
        
        for name in all_names:
            if not name.strip():
                continue
            
            if name in ['Find a reservation', 'Reserve a table', 'Book', 'Prenota']:
                continue
            
            clean_name = re.sub(r'^\d+\.\s*', '', name)
            
            if clean_name in seen:
                continue
            seen.add(clean_name)
            restaurants.append(clean_name)
            
            
        self.logger.info(f"Found {len(restaurants)} unique restaurants")
        
        for i, name in enumerate(restaurants[:30], 1):
            self.logger.info(f'{i}. {name}')
            
            yield {
                'name': name,
                'city': self.city,
                'source': 'tripadvisor',
            }
            
        self.logger.info(f'Complete scraping {len(restaurants)} restaurants')