"""
SQLAlchemy ORM models for restaurant scraper database
Each class represents a table in PostgreSQL
"""
from sqlalchemy import Column, Float, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    name = Column(String(255), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    
    latitude = Column(Numeric(10,8))
    longitude = Column(Numeric(11,8))
    
    phone = Column(String(50))
    website = Column(Text)
    
    
    
    cuisine_type = Column(String(100))
    price_range = Column(String(20))
    rating_avg = Column(Numeric(3,2))
    total_reviews = Column(Integer, default=0)
    
    
    source = Column(String(50))
    source_url = Column(Text)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    
    
    cuisines = relationship("CuisineType", secondary="restaurant_cuisines", back_populates="restaurants")
    
    
    
    # Relationships (one to many)
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="restaurant", cascade="all, delete-orphan")
    scrape_logs = relationship("ScrapeMetadata", back_populates="restaurant", cascade="all, delete-orphan")
    
    
    
    
    
    
    def __repr__(self):
        return f"<Restaurant(id={self.id}, name='{self.name}', city='{self.city}')>"
    
    
    
    
class CuisineType(Base):
    
    __tablename__ = 'cuisine_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())    
    
    # relationship
    restaurants = relationship("Restaurant", secondary="restaurant_cuisines", back_populates="cuisines")
    
    def __repr__(self):
        return f"<CuisineType(id{self.id} name='{self.name}')>"
    
    
    
class RestaurantCuisine(Base):
    __tablename__ = 'restaurant_cuisines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    cuisine_type_id = Column(Integer, ForeignKey('cuisine_types.id', ondelete='CASCADE'), nullable=False)
    
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
    def __repr__(self):
        return f"<RestaurantCuisine(restaurant_id={self.restaurant_id}, cuisine_id={self.cuisine_type_id})>"    
    
    
    
    
    
    
class MenuItem(Base):
    __tablename__ = 'menu_items'
    
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    # Menu Item Info
    dish_name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2))  # 10.50, 25.99
    category = Column(String(100))  # 'antipasti', 'primi', 'secondi', 'dessert'
    is_available = Column(Boolean, default=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    
    # Relationship (many-to-one)
    restaurant = relationship("Restaurant", back_populates="menu_items")
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, dish='{self.dish_name}', price={self.price})>"


class Review(Base):
    """
    Reviews table - stores customer reviews and ratings
    """
    __tablename__ = 'reviews'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    
    # Review Info
    review_text = Column(Text)
    rating = Column(Integer)  # 1 to 5
    review_date = Column(Date)
    reviewer_name = Column(String(255))
    sentiment_score = Column(Float, nullable=True)
    source = Column(String(50))  # 'tripadvisor', 'thefork'
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    
    # Relationship (many-to-one)
    restaurant = relationship("Restaurant", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, restaurant_id={self.restaurant_id}, rating={self.rating})>"


class ScrapeMetadata(Base):
    """
    Scraping metadata - tracks scraping runs and success/failure
    """
    __tablename__ = 'scrape_metadata'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    
    # Scrape Info
    scrape_date = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String(50))
    status = Column(String(50))  # 'success', 'partial', 'failed'
    restaurants_scraped = Column(Integer, default=0)
    items_scraped = Column(Integer, default=0)
    reviews_scraped = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    errors = Column(Text)
    
    # Relationship (many-to-one)
    restaurant = relationship("Restaurant", back_populates="scrape_logs")
    
    def __repr__(self):
        return f"<ScrapeMetadata(id={self.id}, status='{self.status}', date={self.scrape_date})>"