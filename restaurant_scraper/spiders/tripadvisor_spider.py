"""
TripAdvisor Spider - Playwright Version
Extracts comprehensive restaurant data for competitive analysis
"""

from scrapy_playwright.page import PageMethod
import scrapy
import re


class TripAdvisorSpider(scrapy.Spider):
    
    name = 'tripadvisor'
    allowed_domains = ['tripadvisor.com']
    

    def __init__(self, city="Catania", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.city = city
        self.pages_scraped = 0
        self.max_pages = 5
        
    def start_requests(self):
        """Use Playwright for the initial request"""
        url = 'https://www.tripadvisor.com/Restaurants-g187888-Catania_Province_of_Catania_Sicily.html'
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
            "playwright_include_page": True,
            "playwright_page_methods": [
                PageMethod("wait_for_timeout", 3000),  # Aspetta 3 secondi
                PageMethod("wait_for_selector", "a[href*='Restaurant_Review']", timeout=10000),
            ],
        },
        callback=self.parse
    )
        
        
    def parse(self, response):
        """
        Parse the restaurant listing page
        Extract links to individual restaurant detail pages
        """
        self.logger.info(f"Scraping {self.city} restaurants listing...")
        self.logger.info(f"Response status: {response.status}")
        
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
        for link in unique_links[:100]:
            full_url = response.urljoin(link)
            yield scrapy.Request(
                url=full_url,
                meta={"playwright": True},
                callback=self.parse_restaurant_detail,
                errback=self.handle_error
            )
    
   
        
        
        self.pages_scraped += 1
        self.logger.info(f"📄 Page {self.pages_scraped} of {self.max_pages} completed")
        
        if self.pages_scraped < self.max_pages:
            next_page = response.css('a[data-smoke-attr="pagination-next-arrow"]::attr(href)').get()
        
            if next_page:
                next_url = response.urljoin(next_page)
                self.logger.info(f"Going to next page: {next_url}")
                yield scrapy.Request(
                    url=next_url,
                    meta={"playwright":True},
                    callback=self.parse
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
        
        # Extract review count - prova selettore alternativo
        review_texts = response.css('div.biGQs._P.SewaP.kSNRl.KeZJf::text').getall()
        review_count = None
        if review_texts:
            full_text = ''.join(review_texts)
            full_text = full_text.replace(',', '')
            match = re.search(r'(\d+)', full_text)
            if match:
                review_count = int(match.group(1))

        # Extract cuisine types - filtra il ranking
        cuisine_elements = response.css('span.bTeln a span.biGQs::text').getall()
        cuisines = [c.strip() for c in cuisine_elements if c.strip() and '$' not in c and '€' not in c and '#' not in c and 'of' not in c]

        # Extract ranking (e.g., "#170 of 1,465 Restaurants in Catania")
        ranking_text = response.css('span.biGQs._P.VImYz.AWdfh::text').getall()
        ranking = None
        for text in ranking_text:
            if 'of' in text and 'Restaurants' in text:
                ranking = text.strip()
                break

        
        
        # Extract price range
        price_range = None
        price_elements = response.css('span.biGQs._P.VImYz.AWdfh::text').getall()
        for text in price_elements:
            if '$' in text or '€' in text:
                price_range = text.strip()
                break
        
        # Extract website URL
        website = response.css('a[data-automation="restaurantsWebsiteButton"]::attr(href)').get()
        
        # Extract address (usually in popup, may be None)
        address = response.css('[data-automation="restaurantsMapLinkOnName"]::text').get()
        
        # Extract phone from href
        phone_href = response.css('a[href^="tel:"]::attr(href)').get()
        phone = None
        if phone_href:
            phone = phone_href.replace('tel:', '').strip()
        
        # Log what we found
        self.logger.info(f"✅ Scraped: {name} - Rating: {rating} ({review_count} reviews) - Cuisines: {cuisines}")
        
        
        # Controlla se esiste il bottone menu
        menu_button = response.css('button[data-automation="restaurantsMenuButton"]')

        
        if menu_button:
            self.logger.info(f"🍽️ Menu found for {name}, fetching...")
            yield scrapy.Request(
                url=response.url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        # Rimuovi TUTTI gli overlay possibili
                        PageMethod("evaluate", """
                            document.querySelectorAll('#onetrust-consent-sdk, .onetrust-pc-dark-filter, [class*="onetrust"]').forEach(el => el.remove());
                        """),
                        PageMethod("wait_for_timeout", 500),
                        PageMethod("click", "button[data-automation='restaurantsMenuButton']"),
                        PageMethod("wait_for_selector", "div.Jyhuy", timeout=5000),
                    ],
                    "restaurant_name": name,
                },
                callback=self.parse_menu,
                errback=self.handle_error,
                dont_filter=True,
            )
        
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


    def parse_menu(self, response):
        """Extract menu items from restaurant"""
        restaurant_name = response.meta.get('restaurant_name')
        self.logger.info(f"🍽️ Parsing menu for {restaurant_name}")
        
        items = response.css('div.Jyhuy')
        self.logger.info(f"Found {len(items)} menu items")  # Debug
        
        for item in items:
            name = item.css('div.biGQs._P.SewaP.OgHoE::text').get()
            price_text = item.css('div.ksfIO div.biGQs._P.VImYz.AWdfh::text').get()
            
            # Pulisci il prezzo (rimuovi € e converti in numero)
            price = None
            if price_text:
                price_clean = price_text.replace('€', '').replace(',', '.').strip()
                try:
                    price = float(price_clean)
                except ValueError:
                    price = None
            
            self.logger.info(f"DEBUG - Name: {name}, Price: {price}")
            
            if name:
                yield {
                    "dish_name": name,
                    "price": price,
                    "restaurant_url": response.url,
                }