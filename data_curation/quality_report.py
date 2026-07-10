import pandas as pd
from .detect_duplicates import detect_duplicates
from .handle_missing import handle_missing_values
from .validate import validate_data

def generate_quality_report(df, name='Dataset', place_df=None):
    """
    Generate a comprehensive quality report for a dataset.
    
    Returns:
        dict with quality metrics
    """
    report = {
        'dataset_name': name,
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': df.columns.tolist(),
        'dtypes': df.dtypes.to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
        'duplicate_info': detect_duplicates(df),
        'validation': validate_data(df, place_df),
        'unique_counts': {col: df[col].nunique() for col in df.columns},
        'sample_rows': df.head(5).to_dict('records')
    }
    
    # Summary statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numeric_cols) > 0:
        report['numeric_summary'] = df[numeric_cols].describe().to_dict()
    
    # Summary statistics for categorical columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        report['categorical_summary'] = {}
        for col in categorical_cols[:10]:  # Limit to 10 columns
            report['categorical_summary'][col] = df[col].value_counts().head(10).to_dict()
    
    # Calculate overall quality score (0-100)
    score = 100
    
    # Deduct for missing values
    missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    if missing_pct > 5:
        score -= min(20, missing_pct)
    
    # Deduct for duplicates
    dup_count = report['duplicate_info']['exact_duplicate_count']
    if dup_count > 0:
        score -= min(30, dup_count / len(df) * 100)
    
    # Deduct for validation errors
    if report['validation']['errors']:
        score -= len(report['validation']['errors']) * 10
    
    report['quality_score'] = max(0, min(100, round(score, 1)))
    
    # Quality grade
    if report['quality_score'] >= 90:
        report['quality_grade'] = 'A - Excellent'
    elif report['quality_score'] >= 75:
        report['quality_grade'] = 'B - Good'
    elif report['quality_score'] >= 60:
        report['quality_grade'] = 'C - Fair'
    else:
        report['quality_grade'] = 'D - Poor'
    
    return report