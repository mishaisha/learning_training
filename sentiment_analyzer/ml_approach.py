#!/usr/bin/env python3
"""
ML-based Sentiment Analyzer - Milestone 2
Naive Bayes classifier approach
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import re
import joblib
import os

# Sample movie review dataset (in practice, you'd load a larger dataset)
SAMPLE_REVIEWS = [
    ("This movie was absolutely fantastic and wonderful!", "positive"),
    ("I loved every minute of this film. Brilliant acting!", "positive"),
    ("What a great movie! Highly recommended.", "positive"),
    ("Excellent story and superb direction.", "positive"),
    ("Amazing film with great performances.", "positive"),
    ("This was a terrible movie. I hated it.", "negative"),
    ("Awful film. Waste of time and money.", "negative"),
    ("Horrible acting and boring plot.", "negative"),
    ("Worst movie I've ever seen.", "negative"),
    ("Disappointing and poorly executed.", "negative"),
    ("The movie was okay, nothing special.", "neutral"),
    ("It was an average film.", "neutral"),
    ("Not great, not terrible. Just okay.", "neutral"),
    ("Mediocre at best.", "neutral"),
    ("I've seen better, I've seen worse.", "neutral")
]

def clean_text(text):
    """Text preprocessing"""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove non-alphabetic characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    return text

def prepare_data():
    """Prepare training data"""
    texts = [clean_text(review) for review, _ in SAMPLE_REVIEWS]
    labels = [sentiment for _, sentiment in SAMPLE_REVIEWS]
    return texts, labels

def train_model():
    """Train and evaluate the sentiment classifier"""
    print("=== ML-Based Sentiment Analyzer (Milestone 2) ===")
    print("Preparing data...")
    
    texts, labels = prepare_data()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    
    # Vectorize text
    vectorizer = CountVectorizer(stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Train Naive Bayes classifier
    print("Training Naive Bayes classifier...")
    classifier = MultinomialNB()
    classifier.fit(X_train_vec, y_train)
    
    # Evaluate
    y_pred = classifier.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model and vectorizer
    model_dir = 'model'
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(classifier, f'{model_dir}/sentiment_classifier.pkl')
    joblib.dump(vectorizer, f'{model_dir}/vectorizer.pkl')
    
    print(f"\nModel saved to {model_dir}/")
    
    return classifier, vectorizer

def predict_sentiment(text, classifier, vectorizer):
    """Predict sentiment for given text"""
    cleaned_text = clean_text(text)
    text_vec = vectorizer.transform([cleaned_text])
    prediction = classifier.predict(text_vec)[0]
    probability = classifier.predict_proba(text_vec)[0]
    
    # Get confidence score
    classes = classifier.classes_
    confidence = max(probability)
    
    return prediction, confidence, dict(zip(classes, probability))

def interactive_mode(classifier, vectorizer):
    """Interactive mode for testing the model"""
    print("\n=== Interactive Sentiment Analysis ===")
    print("Enter text to analyze (type 'quit' to exit):")
    
    while True:
        user_input = input("\n> ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not user_input.strip():
            print("Please enter some text.")
            continue
            
        sentiment, confidence, probabilities = predict_sentiment(user_input, classifier, vectorizer)
        print(f"Sentiment: {sentiment}")
        print(f"Confidence: {confidence:.2f}")
        print("Probabilities:", {k: f"{v:.2f}" for k, v in probabilities.items()})

def main():
    """Main function"""
    # Check if model exists, otherwise train
    model_path = 'model/sentiment_classifier.pkl'
    vectorizer_path = 'model/vectorizer.pkl'
    
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        print("Loading existing model...")
        classifier = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
    else:
        classifier, vectorizer = train_model()
    
    interactive_mode(classifier, vectorizer)

if __name__ == "__main__":
    main()