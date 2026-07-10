import pandas as pd

def validate_data(df, place_df=None):
    """
    Validate data for quality issues.
    
    Returns:
        dict with validation results
    """
    results = {
        'total_rows': len(df),
        'errors': [],
        'warnings': [],
        'valid_rows': 0
    }
    
    # Check for required columns
    required_columns = ['place_id']
    missing_required = [col for col in required_columns if col not in df.columns]
    if missing_required:
        results['errors'].append(f"Missing required columns: {missing_required}")
        return results
    
    # Validate place_id references
    if place_df is not None:
        valid_place_ids = set(place_df['place_id'].tolist())
        invalid_place_ids = df[~df['place_id'].isin(valid_place_ids)]
        if not invalid_place_ids.empty:
            results['errors'].append(f"Found {len(invalid_place_ids)} invalid place_id references")
    
    # Check for numeric ranges
    numeric_checks = {
        'latitude': (-90, 90),
        'longitude': (-180, 180),
        'average_rating': (1, 5),
        'overall_rating': (1, 5),
        'entry_fee_inr': (0, None),
        'price_per_night_inr': (0, None)
    }
    
    for col, (min_val, max_val) in numeric_checks.items():
        if col in df.columns:
            invalid = df[df[col].notnull() & ~df[col].between(min_val, max_val if max_val else float('inf'))]
            if not invalid.empty:
                results['warnings'].append(f"Column '{col}' has {len(invalid)} out-of-range values")
    
    # Check for common text issues
    text_columns = ['place_name', 'district', 'category', 'gender', 'sentiment']
    for col in text_columns:
        if col in df.columns:
            # Check for trailing spaces
            trailing = df[df[col].astype(str).str.endswith(' ')]
            if not trailing.empty:
                results['warnings'].append(f"Column '{col}' has {len(trailing)} entries with trailing spaces")
            
            # Check for inconsistent case (very common)
            if df[col].dtype == 'object':
                unique_vals = df[col].dropna().unique()
                if len(unique_vals) > 0 and all(isinstance(v, str) for v in unique_vals):
                    # Check if there are mixed case versions of same values
                    lower_vals = set(v.lower() for v in unique_vals if isinstance(v, str))
                    if len(lower_vals) < len(unique_vals):
                        results['warnings'].append(f"Column '{col}' has mixed case values")
    
    results['valid_rows'] = len(df) - len(df[df.isnull().any(axis=1)])
    
    return results