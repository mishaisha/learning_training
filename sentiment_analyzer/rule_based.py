#!/usr/bin/env python3
"""
Rule-based Sentiment Analyzer - Milestone 1
Simple word counting approach
"""

import re

# Basic positive and negative word lists
POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 
    'like', 'happy', 'joy', 'best', 'better', 'awesome', 'brilliant', 'perfect',
    'super', 'nice', 'fine', 'okay', 'cool', 'sweet', 'fantastic', 'terrific'
}

NEGATIVE_WORDS = {
    'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'dislike', 'sad',
    'angry', 'upset', 'disappointed', 'poor', 'boring', 'annoying', 'nasty',
    'ugly', 'wrong', 'fail', 'failed', 'failure', 'hurt', 'pain', 'broken'
}

def clean_text(text):
    """Simple text cleaning"""
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return text

def analyze_sentiment_rule_based(text):
    """Analyze sentiment using rule-based approach"""
    cleaned_text = clean_text(text)
    words = cleaned_text.split()
    
    positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
    negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    
    if positive_count > negative_count:
        return "Positive", positive_count, negative_count
    elif negative_count > positive_count:
        return "Negative", positive_count, negative_count
    else:
        return "Neutral", positive_count, negative_count

def main():
    """Main function for rule-based sentiment analyzer"""
    print("=== Rule-Based Sentiment Analyzer (Milestone 1) ===")
    print("Enter text to analyze (type 'quit' to exit):")
    
    while True:
        user_input = input("\n> ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not user_input.strip():
            print("Please enter some text.")
            continue
            
        sentiment, pos_count, neg_count = analyze_sentiment_rule_based(user_input)
        print(f"Sentiment: {sentiment}")
        print(f"Positive indicators: {pos_count}")
        print(f"Negative indicators: {neg_count}")

if __name__ == "__main__":
    main()