from .prediction import train_visitor_prediction_model
from .recommendation import build_recommendation_model
import pandas as pd
import sqlite3

def train_all_models():
    """Train all ML models."""
    print("🚀 Training ML models...")
    
    # Train visitor prediction model
    print("📊 Training visitor prediction model...")
    train_visitor_prediction_model()
    
    # Build recommendation model
    print("📊 Building recommendation model...")
    conn = sqlite3.connect('database/tourism_platform.db')
    places_df = pd.read_sql_query("SELECT * FROM tourist_places", conn)
    conn.close()
    
    if not places_df.empty:
        build_recommendation_model(places_df)
        print("✅ Recommendation model built successfully")
    else:
        print("⚠️ No place data available for recommendation model")
    
    print("✅ All models trained successfully!")

if __name__ == '__main__':
    train_all_models()