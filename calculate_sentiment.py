import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from restaurant_scraper.database.connection import engine
from restaurant_scraper.database.models import Review
from sqlalchemy.orm import sessionmaker

# Your word lists
positive = ["great", "excellent", "amazing", "delicious", "wonderful", "perfect", "love"]
negative = ["bad", "terrible", "awful", "poor", "disappointing", "worst", "horrible"]

def calculate_sentiment(review_text):
    if review_text is None or not review_text:
        return 0.5 
    
    review_text = review_text.lower()
    
    positive_count = 0
    negative_count = 0
    
    words = review_text.split()
    for word in words:
        if word in positive:
            positive_count += 1
        if word in negative:
            negative_count += 1
            
    if positive_count + negative_count == 0:
        return 0.5 
    
    score = positive_count / (positive_count + negative_count)
    return score
# Test with sample texts first
print("=== Testing Function ===")
test_reviews = [
    "This restaurant is amazing and delicious!",
    "Terrible food, awful service, very disappointing.",
    "It was okay, nothing special.",
    "I love this place! Perfect and excellent!",
]

for test in test_reviews:
    score = calculate_sentiment(test)
    print(f"Review: {test[:50]}")
    print(f"Score: {score}\n")

# Then test with real database reviews
print("\n=== Testing with Database ===")
Session = sessionmaker(bind=engine)
session = Session()

# Get first 5 reviews
reviews = session.query(Review).limit(5).all()

for review in reviews:
    if review.review_text:
        score = calculate_sentiment(review.review_text)
        print(f"Review ID: {review.id}")
        print(f"Text: {review.review_text[:80]}...")
        print(f"Score: {score}\n")

session.close()