import pandas as pd
import hashlib

def detect_duplicates(df, key_columns=None):
    """
    Detect duplicate rows in a DataFrame.
    
    Args:
        df: pandas DataFrame
        key_columns: list of columns to check for duplicates (None = all columns)
    
    Returns:
        dict with duplicate information
    """
    if key_columns is None:
        # Use all columns except IDs
        key_columns = [col for col in df.columns if col.lower() not in ['place_id', 'hotel_id', 'restaurant_id', 'event_id', 'review_id', 'record_id', 'weather_id']]
    
    # Check for exact duplicates on all columns
    exact_duplicates = df[df.duplicated(subset=key_columns, keep=False)]
    
    # Check for duplicates on specific key fields
    if 'place_name' in df.columns:
        name_duplicates = df[df.duplicated(subset=['place_name'], keep=False)]
    else:
        name_duplicates = pd.DataFrame()
    
    return {
        'total_rows': len(df),
        'exact_duplicate_count': len(exact_duplicates),
        'name_duplicate_count': len(name_duplicates) if not name_duplicates.empty else 0,
        'exact_duplicates': exact_duplicates,
        'name_duplicates': name_duplicates
    }

def remove_duplicates(df, key_columns=None, keep='first'):
    """
    Remove duplicate rows from a DataFrame.
    
    Args:
        df: pandas DataFrame
        key_columns: list of columns to check for duplicates
        keep: 'first', 'last', or False
    
    Returns:
        DataFrame with duplicates removed
    """
    if key_columns is None:
        key_columns = [col for col in df.columns if col.lower() not in ['place_id', 'hotel_id', 'restaurant_id', 'event_id', 'review_id', 'record_id', 'weather_id']]
    
    df_cleaned = df.drop_duplicates(subset=key_columns, keep=keep)
    
    removed_count = len(df) - len(df_cleaned)
    print(f"✅ Removed {removed_count} duplicate rows")
    
    return df_cleaned