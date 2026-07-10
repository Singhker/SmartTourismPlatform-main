import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import sqlite3
import pickle
import os

MODEL_PATH = 'models/visitor_prediction_model.pkl'

def train_visitor_prediction_model():
    """Train a model to predict visitor counts."""
    conn = sqlite3.connect('database/tourism_platform.db')
    
    # Explicitly select columns with aliases to avoid duplicate names
    query = """
    SELECT 
        v.place_id,
        v.year,
        v.month_number,
        v.season,
        v.total_visitors,
        v.special_event,
        v.festival_season,
        w.weather_condition AS weather_condition_weather,
        w.average_temperature_c,
        w.rainfall_mm
    FROM visitor_statistics v
    LEFT JOIN weather w 
        ON v.place_id = w.place_id AND v.year = w.year AND v.month_number = w.month_number
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("⚠️ No visitor data available for training")
        return None
    
    # Fill missing weather data with average values (or we could drop rows)
    df['weather_condition_weather'] = df['weather_condition_weather'].fillna('Unknown')
    df['average_temperature_c'] = df['average_temperature_c'].fillna(df['average_temperature_c'].mean())
    df['rainfall_mm'] = df['rainfall_mm'].fillna(0)
    df['total_visitors'] = df['total_visitors'].fillna(0)
    df['special_event'] = df['special_event'].fillna('No')
    df['festival_season'] = df['festival_season'].fillna('No')
    
    # Prepare features
    # Season (encode)
    le_season = LabelEncoder()
    season_encoded = le_season.fit_transform(df['season'].fillna('Unknown'))
    
    # Weather condition (encode)
    le_weather = LabelEncoder()
    weather_encoded = le_weather.fit_transform(df['weather_condition_weather'])
    
    # Month (cyclic encoding for seasonality)
    month_sin = np.sin(2 * np.pi * df['month_number'] / 12)
    month_cos = np.cos(2 * np.pi * df['month_number'] / 12)
    
    # Place (encode)
    le_place = LabelEncoder()
    place_encoded = le_place.fit_transform(df['place_id'])
    
    # Special event and festival (binary)
    special_event_bin = df['special_event'].map({'Yes': 1, 'No': 0}).fillna(0)
    festival_bin = df['festival_season'].map({'Yes': 1, 'No': 0}).fillna(0)
    
    # Build feature matrix
    X = np.column_stack([
        month_sin,
        month_cos,
        season_encoded,
        weather_encoded,
        df['average_temperature_c'].values,
        df['rainfall_mm'].values,
        place_encoded,
        special_event_bin,
        festival_bin
    ])
    
    y = df['total_visitors'].values
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Save model
    os.makedirs('models', exist_ok=True)
    model_data = {
        'model': model,
        'le_season': le_season,
        'le_weather': le_weather,
        'le_place': le_place,
        'feature_names': ['month_sin', 'month_cos', 'season', 'weather', 'temperature', 'rainfall', 'place', 'special_event', 'festival']
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)
    
    print("✅ Visitor prediction model trained successfully")
    return model_data

def load_prediction_model():
    """Load the prediction model."""
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

def predict_visitors(place_id, month, year, weather_condition='Clear', temperature=25, rainfall=50, special_event=False, festival=False):
    """Predict visitor count for a specific place and month."""
    model_data = load_prediction_model()
    if model_data is None:
        model_data = train_visitor_prediction_model()
        if model_data is None:
            return None
    
    # Encode inputs
    try:
        season = 'Winter' if month in [1,2,12] else 'Summer' if month in [5,6] else 'Monsoon' if month in [7,8,9] else 'Autumn' if month in [10,11] else 'Spring'
        season_encoded = model_data['le_season'].transform([season])[0]
        weather_encoded = model_data['le_weather'].transform([weather_condition])[0]
        place_encoded = model_data['le_place'].transform([place_id])[0]
    except ValueError:
        # If unseen label, use 0
        season_encoded = 0
        weather_encoded = 0
        try:
            place_encoded = model_data['le_place'].transform([place_id])[0]
        except:
            place_encoded = 0
    
    month_sin = np.sin(2 * np.pi * month / 12)
    month_cos = np.cos(2 * np.pi * month / 12)
    
    # Feature vector
    features = np.array([[
        month_sin,
        month_cos,
        season_encoded,
        weather_encoded,
        temperature,
        rainfall,
        place_encoded,
        1 if special_event else 0,
        1 if festival else 0
    ]])
    
    prediction = model_data['model'].predict(features)[0]
    return max(0, int(prediction))

def get_forecast(place_id, months=6):
    """Get forecast for the next N months."""
    import datetime
    
    forecasts = []
    current_date = datetime.datetime.now()
    
    for i in range(months):
        month = ((current_date.month - 1 + i) % 12) + 1
        year = current_date.year + (current_date.month + i - 1) // 12
        
        # Simple weather estimation
        weather = 'Clear'
        temp = 25
        rainfall = 50
        if month in [6,7,8,9]:
            weather = 'Rainy'
            temp = 28
            rainfall = 200
        elif month in [12,1,2]:
            weather = 'Clear'
            temp = 15
            rainfall = 10
        
        predicted = predict_visitors(place_id, month, year, weather, temp, rainfall)
        
        forecasts.append({
            'month': month,
            'year': year,
            'predicted_visitors': predicted,
            'weather': weather,
            'temperature': temp
        })
    
    return forecasts