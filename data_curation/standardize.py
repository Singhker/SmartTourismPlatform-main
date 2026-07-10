import pandas as pd

def standardize_text_columns(df):
    """Standardize text columns: strip whitespace, capitalize, etc."""
    df_standardized = df.copy()
    
    for col in df.select_dtypes(include=['object']).columns:
        # Strip whitespace
        df_standardized[col] = df_standardized[col].astype(str).str.strip()
        
        # Standardize common categories
        if col.lower() == 'district':
            df_standardized[col] = df_standardized[col].str.title()
        
        if col.lower() == 'category':
            df_standardized[col] = df_standardized[col].str.title()
        
        if col.lower() == 'gender':
            df_standardized[col] = df_standardized[col].str.capitalize()
            df_standardized[col] = df_standardized[col].replace({'Male': 'Male', 'Female': 'Female', 'Other': 'Other'})
        
        if col.lower() == 'season':
            df_standardized[col] = df_standardized[col].str.capitalize()
            df_standardized[col] = df_standardized[col].replace({
                'Spring': 'Spring', 'Summer': 'Summer', 'Autumn': 'Autumn', 
                'Winter': 'Winter', 'Monsoon': 'Monsoon'
            })
    
    return df_standardized

def standardize_numeric_columns(df):
    """Convert numeric columns to proper types."""
    df_standardized = df.copy()
    
    numeric_columns = [
        'latitude', 'longitude', 'entry_fee_inr', 'visit_duration_hours',
        'price_per_night_inr', 'average_cost_for_two_inr', 'average_rating',
        'overall_rating', 'total_visitors', 'revenue_inr', 'growth_percentage'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df_standardized[col] = pd.to_numeric(df_standardized[col], errors='coerce')
    
    return df_standardized

def standardize_data(df):
    """Apply all standardization functions."""
    df_standardized = df.copy()
    df_standardized = standardize_text_columns(df_standardized)
    df_standardized = standardize_numeric_columns(df_standardized)
    
    # Remove rows with all null values
    df_standardized = df_standardized.dropna(how='all')
    
    print("✅ Data standardization complete")
    return df_standardized