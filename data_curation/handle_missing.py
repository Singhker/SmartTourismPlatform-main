import pandas as pd

def handle_missing_values(df, strategy='fill', fill_value=None):
    """
    Handle missing values in a DataFrame.
    
    Args:
        df: pandas DataFrame
        strategy: 'drop', 'fill', or 'flag'
        fill_value: value to fill (for 'fill' strategy)
    
    Returns:
        DataFrame with missing values handled
    """
    missing_counts = df.isnull().sum()
    total_missing = missing_counts.sum()
    
    print(f"📊 Total missing values: {total_missing}")
    print(f"   Missing per column: {missing_counts[missing_counts > 0].to_dict()}")
    
    if strategy == 'drop':
        df_cleaned = df.dropna()
        print(f"✅ Dropped {len(df) - len(df_cleaned)} rows with missing values")
        return df_cleaned
    
    elif strategy == 'fill':
        df_filled = df.copy()
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # Numeric columns
                if fill_value is not None:
                    df_filled[col] = df[col].fillna(fill_value)
                else:
                    df_filled[col] = df[col].fillna(df[col].median() if df[col].nunique() > 1 else 0)
            else:
                # String columns
                if fill_value is not None:
                    df_filled[col] = df[col].fillna(fill_value)
                else:
                    df_filled[col] = df[col].fillna('Unknown')
        print("✅ Filled missing values")
        return df_filled
    
    elif strategy == 'flag':
        df_flagged = df.copy()
        for col in df.columns:
            df_flagged[f'{col}_missing'] = df[col].isnull().astype(int)
            if df[col].dtype in ['int64', 'float64']:
                df_flagged[col] = df[col].fillna(0)
            else:
                df_flagged[col] = df[col].fillna('Missing')
        print("✅ Flagged missing values")
        return df_flagged
    
    else:
        print(f"⚠️ Unknown strategy: {strategy}")
        return df