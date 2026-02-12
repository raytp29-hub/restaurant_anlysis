


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
