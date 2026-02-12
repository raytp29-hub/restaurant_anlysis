"""
TripAdvisor Spider - Enhanced Version
Extracts comprehensive restaurant data for competitive analysis
"""
import scrapy
import re


class TripAdvisorSpider(scrapy.Spider):
    
    name = 'tripadvisor'
    allowed_domains = ['tripadvisor.com']
    

    def __init__(self, city="Catania", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.city = city
        
        # Start with the listing page
        self.start_urls = [
            'https://www.tripadvisor.com/Restaurants-g187888-Catania_Province_of_Catania_Sicily.html'
        ]
        
        
    def parse(self, response):
        """
        Parse the restaurant listing page
        Extract links to individual restaurant detail pages
        """
        self.logger.info(f"Scraping {self.city} restaurants listing...")
        
        # Find all restaurant detail page links
        restaurant_links = response.css('a[href*="Restaurant_Review"]::attr(href)').getall()
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in restaurant_links:
            if link not in seen and 'Restaurant_Review' in link:
                seen.add(link)
                unique_links.append(link)
        
        self.logger.info(f"Found {len(unique_links)} restaurant links")
        
        # Follow each restaurant link to get detailed info
        for link in unique_links[:30]:  # Limit to first 30 for testing
            full_url = response.urljoin(link)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_restaurant_detail,
                errback=self.handle_error
            )
    
    
    def parse_restaurant_detail(self, response):
        """
        Parse individual restaurant detail page
        Extract all relevant data for competitive analysis
        """
        # Extract restaurant name
        name = response.css('h1.biGQs._P.SewaP.CIuBz::text').get()
        if not name:
            name = response.css('h1::text').get()  # Fallback
        
        # Extract rating (e.g., "4.4")
        rating = response.css('[data-automation="bubbleRatingValue"] span::text').get()
        
        # Extract review count (e.g., "(166 reviews)")
        review_text = response.css('[data-automation="bubbleReviewCount"] span::text').get()
        review_count = None
        if review_text:
            # Extract number from "(166 reviews)" or "(166)"
            match = re.search(r'\((\d+)', review_text)
            if match:
                review_count = int(match.group(1))
        
        # Extract ranking (e.g., "#170 of 1,465 Restaurants in Catania")
        ranking_text = response.css('span.biGQs._P.VImYz.AWdfh::text').getall()
        ranking = None
        for text in ranking_text:
            if 'of' in text and 'Restaurants' in text:
                ranking = text.strip()
                break
        
        # Extract cuisine types (e.g., ["Italian", "Seafood"])
        cuisine_links = response.css('span.bTeln a::text').getall()
        cuisines = [c.strip() for c in cuisine_links if c.strip()]
        
        # Extract price range (e.g., "$$ - $$$")
        price_range = None
        price_elements = response.css('span.biGQs._P.VImYz.AWdfh::text').getall()
        for text in price_elements:
            if '$' in text:
                price_range = text.strip()
                break
        
        # Extract website URL
        website = response.css('a[data-automation="restaurantsWebsiteButton"]::attr(href)').get()
        
        # Extract address
        address = response.css('[data-automation="restaurantAddress"]::text').get()
        if not address:
            # Alternative selector if the above doesn't work
            address = response.css('span.DsyBj::text').get()
        
        # Extract phone
        phone = response.css('a[href^="tel:"]::text').get()
        
        # Log what we found
        self.logger.info(f"✅ Scraped: {name} - Rating: {rating} ({review_count} reviews)")
        
        # Yield the data
        yield {
            'name': name,
            'city': self.city,
            'source': 'tripadvisor',
            'source_url': response.url,
            'rating_avg': float(rating) if rating else None,
            'total_reviews': review_count,
            'ranking': ranking,
            'cuisine_type': ', '.join(cuisines) if cuisines else None,
            'price_range': price_range,
            'website': website,
            'address': address,
            'phone': phone,
        }
    
    
    def handle_error(self, failure):
        """Handle request failures"""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")