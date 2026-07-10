import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import pickle
import os

MODEL_PATH = 'models/recommendation_model.pkl'

def build_recommendation_model(places_df):
    """Build a content-based recommendation model."""
    # Create feature combinations for each place
    features = []
    for _, row in places_df.iterrows():
        # Combine categorical and text features
        feature_text = ' '.join([
            str(row.get('category', '')),
            str(row.get('district', '')),
            str(row.get('best_season', '')),
            str(row.get('popularity_level', '')),
            str(row.get('adventure_level', '')),
            str(row.get('description', '')),
            str(row.get('place_name', ''))
        ])
        features.append(feature_text.lower())
    
    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(features)
    
    # Compute similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Save model
    os.makedirs('models', exist_ok=True)
    model_data = {
        'vectorizer': vectorizer,
        'similarity_matrix': similarity_matrix,
        'place_ids': places_df['place_id'].tolist(),
        'place_names': places_df['place_name'].tolist()
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)
    
    return model_data

def load_recommendation_model():
    """Load the recommendation model."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

def get_similar_places(place_id, n_recommendations=5):
    """Get similar places based on content."""
    # Load model
    model = load_recommendation_model()
    if model is None:
        # Build model from database
        conn = sqlite3.connect('database/tourism_platform.db')
        places_df = pd.read_sql_query("SELECT * FROM tourist_places", conn)
        conn.close()
        model = build_recommendation_model(places_df)
    
    try:
        idx = model['place_ids'].index(place_id)
    except ValueError:
        return []
    
    similarity_scores = list(enumerate(model['similarity_matrix'][idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    # Get top similar places (excluding itself)
    recommendations = []
    for i, score in similarity_scores[1:n_recommendations+1]:
        if score > 0.1:  # Only include if similarity is meaningful
            recommendations.append({
                'place_id': model['place_ids'][i],
                'place_name': model['place_names'][i],
                'similarity_score': round(score, 3)
            })
    
    return recommendations

def get_recommendations(place_id, place_df=None, n_recommendations=5):
    """Get recommendations for a place."""
    return get_similar_places(place_id, n_recommendations)