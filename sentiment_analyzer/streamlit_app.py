#!/usr/bin/env python3
"""
Streamlit Sentiment Analyzer - Milestone 3
Interactive web interface for sentiment analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import re
import joblib
import os

# Set page config
st.set_page_config(
    page_title="Sentiment Analyzer - AI Learning Journey",
    page_icon="😊",
    layout="centered"
)

# Text cleaning function
def clean_text(text):
    """Text preprocessing"""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove non-alphabetic characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    return text

# Load or train model
@st.cache_resource
def load_model():
    """Load or train the sentiment analysis model"""
    model_dir = 'model'
    model_path = f'{model_dir}/sentiment_classifier.pkl'
    vectorizer_path = f'{model_dir}/vectorizer.pkl'
    
    # Sample movie review dataset for training if model doesn't exist
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
    
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        # Load existing model
        classifier = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
    else:
        # Train new model
        texts = [clean_text(review) for review, _ in SAMPLE_REVIEWS]
        labels = [sentiment for _, sentiment in SAMPLE_REVIEWS]
        
        vectorizer = CountVectorizer(stop_words='english')
        X_vec = vectorizer.fit_transform(texts)
        
        classifier = MultinomialNB()
        classifier.fit(X_vec, labels)
        
        # Save model
        os.makedirs(model_dir, exist_ok=True)
        joblib.dump(classifier, model_path)
        joblib.dump(vectorizer, vectorizer_path)
    
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

# Main app
def main():
    """Main Streamlit application"""
    # Title and description
    st.title("😊 Sentiment Analyzer")
    st.markdown("### AI Learning Journey Project")
    st.markdown("""
    This app demonstrates my progression in AI/ML learning:
    - **Milestone 1**: Rule-based approach (word counting)
    - **Milestone 2**: Machine learning (Naive Bayes classifier)
    - **Milestone 3**: Web interface (Streamlit app)
    """)
    
    # Load model
    classifier, vectorizer = load_model()
    
    # Text input
    st.subheader("Analyze Your Text")
    user_input = st.text_area(
        "Enter text to analyze sentiment:",
        placeholder="Type your movie review, tweet, or any text here...",
        height=100
    )
    
    # Analyze button
    if st.button("Analyze Sentiment", type="primary"):
        if user_input.strip():
            # Get prediction
            sentiment, confidence, probabilities = predict_sentiment(user_input, classifier, vectorizer)
            
            # Display result with color coding
            if sentiment == "positive":
                st.success(f"**Sentiment**: {sentiment} 😊")
            elif sentiment == "negative":
                st.error(f"**Sentiment**: {sentiment} 😞")
            else:
                st.info(f"**Sentiment**: {sentiment} 😐")
            
            st.write(f"**Confidence**: {confidence:.2f}")
            
            # Show probabilities
            st.subheader("Probability Breakdown")
            prob_df = pd.DataFrame(list(probabilities.items()), columns=['Sentiment', 'Probability'])
            prob_df['Probability'] = prob_df['Probability'].apply(lambda x: f"{x:.2f}")
            st.dataframe(prob_df, hide_index=True)
            
        else:
            st.warning("Please enter some text to analyze.")
    
    # Sidebar with information
    with st.sidebar:
        st.header("About This Project")
        st.markdown("""
        **Learning Milestones:**
        1. **Rule-Based**: Simple positive/negative word counting
        2. **ML Approach**: Naive Bayes classifier on movie reviews
        3. **Web App**: Interactive Streamlit interface
        
        **Technologies Used:**
        - Python, Streamlit
        - Scikit-learn for ML
        - Git for version control
        
        **Purpose:** 
        Demonstrate progression from basic concepts to applied ML.
        """)
        
        st.header("Try These Examples")
        examples = [
            "This movie was fantastic! I loved it.",
            "Terrible film, waste of time.",
            "The movie was okay, nothing special."
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}"):
                st.session_state.user_input = example
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("*Built as part of AI learning journey • GitHub: @mishaisha*")

if __name__ == "__main__":
    main()