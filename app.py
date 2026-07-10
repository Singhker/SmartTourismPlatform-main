from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime, timedelta
import plotly
import plotly.express as px
import plotly.utils

from config import Config
from database.import_csv import import_all_datasets, get_db_connection
from data_curation import detect_duplicates, handle_missing_values, standardize_data, validate_data, generate_quality_report
from ml import get_recommendations, predict_visitors, get_forecast

app = Flask(__name__)
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('models', exist_ok=True)

# =============================================================================
# Helper Functions
# =============================================================================


def safe_int(value):
    """Safely convert to int, returning 0 if None or invalid."""
    try:
        return int(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0


def safe_float(value):
    """Safely convert to float, returning 0.0 if None or invalid."""
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0


def get_db_data(query, params=None):
    """Execute query and return DataFrame."""
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_place_by_id(place_id):
    """Get place details by ID."""
    query = "SELECT * FROM tourist_places WHERE place_id = ?"
    conn = get_db_connection()
    result = conn.execute(query, (place_id,)).fetchone()
    conn.close()
    return dict(result) if result else None


def get_visitor_data(place_id=None):
    """Get visitor statistics data."""
    query = "SELECT * FROM visitor_statistics"
    if place_id:
        query += f" WHERE place_id = '{place_id}'"
    return get_db_data(query)


def get_review_data(place_id=None):
    """Get review data."""
    query = "SELECT * FROM reviews"
    if place_id:
        query += f" WHERE place_id = '{place_id}'"
    return get_db_data(query)


def get_hotel_data(place_id=None):
    """Get hotel data."""
    query = "SELECT * FROM hotels"
    if place_id:
        query += f" WHERE place_id = '{place_id}'"
    return get_db_data(query)


def get_restaurant_data(place_id=None):
    """Get restaurant data."""
    query = "SELECT * FROM restaurants"
    if place_id:
        query += f" WHERE place_id = '{place_id}'"
    return get_db_data(query)


def get_event_data(place_id=None):
    """Get event data."""
    query = "SELECT * FROM events"
    if place_id:
        query += f" WHERE place_id = '{place_id}'"
    return get_db_data(query)


def get_weather_data(place_id=None):
    """Get weather data."""
    query = "SELECT * FROM weather"
    if place_id:
        query += f" WHERE place_id = '{place_id}'"
    return get_db_data(query)

# =============================================================================
# Admin Authentication
# =============================================================================


# Admin password (change this to something secure)
ADMIN_PASSWORD = "admin123"


def admin_required():
    """Check if admin is logged in."""
    if not session.get('admin_logged_in'):
        return False
    return True


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid password. Please try again.")
    return render_template('admin_login.html', error=None)


@app.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# =============================================================================
# Admin Routes (Protected)
# =============================================================================


@app.route('/admin')
def admin_dashboard():
    """Simple admin dashboard."""
    if not admin_required():
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    tables = ['tourist_places', 'visitor_statistics',
              'reviews', 'hotels', 'restaurants', 'events', 'weather']
    stats = {}
    for table in tables:
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
        stats[table] = cursor.fetchone()[0]
    conn.close()
    return render_template('admin.html', stats=stats)


@app.route('/admin/view/<table_name>')
def admin_view_table(table_name):
    """View data from a specific table."""
    if not admin_required():
        return redirect(url_for('admin_login'))

    # Validate table name to prevent SQL injection
    allowed_tables = ['tourist_places', 'visitor_statistics',
                      'reviews', 'hotels', 'restaurants', 'events', 'weather']
    if table_name not in allowed_tables:
        return "Invalid table name", 400

    df = get_db_data(f"SELECT * FROM {table_name} LIMIT 100")
    return render_template('admin_table.html',
                           table_name=table_name,
                           columns=df.columns.tolist() if not df.empty else [],
                           rows=df.to_dict('records') if not df.empty else []
                           )


@app.route('/admin/delete/<table_name>/<id_column>/<id_value>')
def admin_delete_row(table_name, id_column, id_value):
    """Delete a row from a table."""
    if not admin_required():
        return redirect(url_for('admin_login'))

    allowed_tables = ['tourist_places', 'visitor_statistics',
                      'reviews', 'hotels', 'restaurants', 'events', 'weather']
    if table_name not in allowed_tables:
        return "Invalid table name", 400

    conn = get_db_connection()
    try:
        conn.execute(
            f"DELETE FROM {table_name} WHERE {id_column} = ?", (id_value,))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_view_table', table_name=table_name))
    except Exception as e:
        conn.close()
        return f"Error deleting: {str(e)}", 500

# =============================================================================
# Main Routes
# =============================================================================


@app.route('/')
def index():
    """Home page."""
    # Get summary statistics
    places_df = get_db_data("SELECT COUNT(*) as count FROM tourist_places")
    visitors_df = get_db_data(
        "SELECT SUM(total_visitors) as total FROM visitor_statistics")
    reviews_df = get_db_data("SELECT COUNT(*) as count FROM reviews")

    total_places = safe_int(
        places_df.iloc[0]['count']) if not places_df.empty else 0
    total_visitors = safe_int(
        visitors_df.iloc[0]['total']) if not visitors_df.empty else 0
    total_reviews = safe_int(
        reviews_df.iloc[0]['count']) if not reviews_df.empty else 0

    # Get popular places with district
    popular_df = get_db_data("""
        SELECT p.place_id, p.place_name, p.district, p.image_url, 
               AVG(v.visitor_satisfaction) as avg_satisfaction,
               SUM(v.total_visitors) as total_visitors
        FROM tourist_places p
        JOIN visitor_statistics v ON p.place_id = v.place_id
        GROUP BY p.place_id
        ORDER BY total_visitors DESC
        LIMIT 6
    """)

    # Get recent reviews
    recent_reviews = get_db_data("""
        SELECT r.*, p.place_name
        FROM reviews r
        JOIN tourist_places p ON r.place_id = p.place_id
        ORDER BY r.created_date DESC
        LIMIT 5
    """)

    # Get upcoming events
    upcoming_events = get_db_data("""
        SELECT e.*, p.place_name
        FROM events e
        JOIN tourist_places p ON e.place_id = p.place_id
        WHERE e.start_date >= date('now')
        ORDER BY e.start_date
        LIMIT 5
    """)

    # Create visitor trend chart
    visitor_trend = get_db_data("""
        SELECT year, month_name, SUM(total_visitors) as total_visitors
        FROM visitor_statistics
        GROUP BY year, month_number
        ORDER BY year, month_number
    """)

    visitor_chart = None
    if not visitor_trend.empty:
        visitor_trend['total_visitors'] = visitor_trend['total_visitors'].fillna(
            0).astype(int)
        fig = px.line(visitor_trend, x='month_name', y='total_visitors',
                      color='year', title='Visitor Trends')
        visitor_chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html',
                           total_places=total_places,
                           total_visitors=total_visitors,
                           total_reviews=total_reviews,
                           popular_places=popular_df.to_dict(
                               'records') if not popular_df.empty else [],
                           recent_reviews=recent_reviews.to_dict(
                               'records') if not recent_reviews.empty else [],
                           upcoming_events=upcoming_events.to_dict(
                               'records') if not upcoming_events.empty else [],
                           visitor_chart=visitor_chart
                           )


@app.route('/places')
def places():
    """Tourist places list."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = app.config['ITEMS_PER_PAGE']
        search = request.args.get('search', '')
        district = request.args.get('district', '')
        category = request.args.get('category', '')

        query = "SELECT * FROM tourist_places WHERE 1=1"
        params = []

        if search:
            query += " AND place_name LIKE ?"
            params.append(f"%{search}%")

        if district:
            query += " AND district = ?"
            params.append(district)

        if category:
            query += " AND category = ?"
            params.append(category)

        # Get total count for pagination
        count_query = query.replace("SELECT *", "SELECT COUNT(*) as count")
        conn = get_db_connection()
        total = conn.execute(count_query, params).fetchone()['count']
        conn.close()

        # Get paginated results
        query += " ORDER BY popularity_level DESC, place_name LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        places_df = get_db_data(query, tuple(params))

        # Get districts for filter
        districts_df = get_db_data(
            "SELECT DISTINCT district FROM tourist_places ORDER BY district")
        categories_df = get_db_data(
            "SELECT DISTINCT category FROM tourist_places ORDER BY category")

        return render_template('places.html',
                               places=places_df.to_dict(
                                   'records') if not places_df.empty else [],
                               total=total,
                               page=page,
                               pages=(total + per_page - 1) // per_page,
                               search=search,
                               district=district,
                               category=category,
                               districts=districts_df['district'].tolist(
                               ) if not districts_df.empty else [],
                               categories=categories_df['category'].tolist(
                               ) if not categories_df.empty else []
                               )
    except Exception as e:
        import traceback
        return f"<pre>{traceback.format_exc()}</pre>", 500


@app.route('/place/<place_id>')
def place_detail(place_id):
    """Place detail page."""
    place = get_place_by_id(place_id)
    if not place:
        return "Place not found", 404

    # Get visitor statistics
    visitors = get_visitor_data(place_id)

    # Get reviews
    reviews = get_review_data(place_id)

    # Get nearby hotels
    hotels = get_hotel_data(place_id)

    # Get nearby restaurants
    restaurants = get_restaurant_data(place_id)

    # Get events
    events = get_event_data(place_id)

    # Get weather
    weather = get_weather_data(place_id)

    # Get recommendations
    recommendations = get_recommendations(place_id)

    # Create visitor chart
    visitor_chart = None
    if not visitors.empty:
        visitors['total_visitors'] = visitors['total_visitors'].fillna(
            0).astype(int)
        fig = px.line(visitors, x='month_name', y='total_visitors',
                      title=f'Monthly Visitors - {place["place_name"]}')
        visitor_chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Create satisfaction chart
    satisfaction_chart = None
    if not visitors.empty and 'visitor_satisfaction' in visitors.columns:
        visitors['visitor_satisfaction'] = visitors['visitor_satisfaction'].fillna(
            0)
        fig = px.bar(visitors, x='month_name', y='visitor_satisfaction',
                     title='Visitor Satisfaction Trends')
        satisfaction_chart = json.dumps(
            fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('place_detail.html',
                           place=place,
                           visitors=visitors.to_dict(
                               'records') if not visitors.empty else [],
                           reviews=reviews.to_dict(
                               'records') if not reviews.empty else [],
                           hotels=hotels.to_dict(
                               'records') if not hotels.empty else [],
                           restaurants=restaurants.to_dict(
                               'records') if not restaurants.empty else [],
                           events=events.to_dict(
                               'records') if not events.empty else [],
                           weather=weather.to_dict(
                               'records') if not weather.empty else [],
                           recommendations=recommendations,
                           visitor_chart=visitor_chart,
                           satisfaction_chart=satisfaction_chart
                           )


@app.route('/analytics')
def analytics():
    """Analytics dashboard."""
    # Get all data
    visitors = get_visitor_data()
    places = get_db_data("SELECT * FROM tourist_places")
    reviews = get_review_data()

    # Seasonal analysis
    seasonal = get_db_data("""
        SELECT season, SUM(total_visitors) as total_visitors,
               AVG(visitor_satisfaction) as avg_satisfaction
        FROM visitor_statistics
        GROUP BY season
        ORDER BY total_visitors DESC
    """)

    # Category analysis
    category_analysis = get_db_data("""
        SELECT p.category, 
               COUNT(DISTINCT p.place_id) as place_count,
               AVG(v.total_visitors) as avg_visitors,
               AVG(v.visitor_satisfaction) as avg_satisfaction
        FROM tourist_places p
        LEFT JOIN visitor_statistics v ON p.place_id = v.place_id
        GROUP BY p.category
        ORDER BY avg_visitors DESC
    """)

    # District analysis
    district_analysis = get_db_data("""
        SELECT p.district,
               COUNT(DISTINCT p.place_id) as place_count,
               SUM(v.total_visitors) as total_visitors,
               AVG(r.overall_rating) as avg_rating
        FROM tourist_places p
        LEFT JOIN visitor_statistics v ON p.place_id = v.place_id
        LEFT JOIN reviews r ON p.place_id = r.place_id
        GROUP BY p.district
        ORDER BY total_visitors DESC
    """)

    # Create charts
    charts = {}

    if not seasonal.empty:
        seasonal['total_visitors'] = seasonal['total_visitors'].fillna(
            0).astype(int)
        fig = px.bar(seasonal, x='season', y='total_visitors',
                     title='Visitors by Season')
        charts['seasonal'] = json.dumps(
            fig, cls=plotly.utils.PlotlyJSONEncoder)

    if not category_analysis.empty:
        category_analysis['avg_visitors'] = category_analysis['avg_visitors'].fillna(
            0).astype(int)
        fig = px.bar(category_analysis, x='category', y='avg_visitors',
                     title='Average Visitors by Category')
        charts['category'] = json.dumps(
            fig, cls=plotly.utils.PlotlyJSONEncoder)

    if not district_analysis.empty:
        district_analysis['total_visitors'] = district_analysis['total_visitors'].fillna(
            0).astype(int)
        fig = px.bar(district_analysis, x='district', y='total_visitors',
                     title='Total Visitors by District')
        charts['district'] = json.dumps(
            fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('analytics.html',
                           seasonal=seasonal.to_dict(
                               'records') if not seasonal.empty else [],
                           category_analysis=category_analysis.to_dict(
                               'records') if not category_analysis.empty else [],
                           district_analysis=district_analysis.to_dict(
                               'records') if not district_analysis.empty else [],
                           charts=charts
                           )


@app.route('/recommendations')
def recommendations():
    """Recommendation page."""
    place_id = request.args.get('place_id')
    n = request.args.get('n', 5, type=int)

    if place_id:
        recs = get_recommendations(place_id, n_recommendations=n)
    else:
        recs = []

    # Get all places for dropdown
    places = get_db_data(
        "SELECT place_id, place_name FROM tourist_places ORDER BY place_name")

    return render_template('recommendations.html',
                           places=places.to_dict(
                               'records') if not places.empty else [],
                           selected_place=place_id,
                           recommendations=recs
                           )


@app.route('/prediction')
def visitor_prediction():
    """Visitor prediction page."""
    place_id = request.args.get('place_id')
    months = request.args.get('months', 6, type=int)

    forecasts = None
    if place_id:
        forecasts = get_forecast(place_id, months)

    # Get all places for dropdown
    places = get_db_data(
        "SELECT place_id, place_name FROM tourist_places ORDER BY place_name")

    # Create forecast chart
    forecast_chart = None
    if forecasts:
        df = pd.DataFrame(forecasts)
        df['predicted_visitors'] = df['predicted_visitors'].fillna(
            0).astype(int)
        fig = px.line(df, x='month', y='predicted_visitors',
                      title=f'Visitor Forecast',
                      labels={'month': 'Month', 'predicted_visitors': 'Predicted Visitors'})
        forecast_chart = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('visitor_prediction.html',
                           places=places.to_dict(
                               'records') if not places.empty else [],
                           selected_place=place_id,
                           forecasts=forecasts,
                           forecast_chart=forecast_chart
                           )


@app.route('/curation')
def curation():
    """Data curation dashboard."""
    dataset = request.args.get('dataset', 'tourist_places')

    dataset_mapping = {
        'tourist_places': 'tourist_places',
        'visitor_statistics': 'visitor_statistics',
        'reviews': 'reviews',
        'hotels': 'hotels',
        'restaurants': 'restaurants',
        'events': 'events',
        'weather': 'weather'
    }

    table_name = dataset_mapping.get(dataset, 'tourist_places')
    df = get_db_data(f"SELECT * FROM {table_name}")

    if df.empty:
        return render_template('curation.html',
                               datasets=dataset_mapping.keys(),
                               selected=dataset,
                               report=None,
                               error="No data found in this dataset"
                               )

    # Generate quality report
    report = generate_quality_report(df, dataset)

    return render_template('curation.html',
                           datasets=list(dataset_mapping.keys()),
                           selected=dataset,
                           report=report
                           )


@app.route('/curation/fix', methods=['POST'])
def curation_fix():
    """Apply data curation fixes."""
    dataset = request.form.get('dataset', 'tourist_places')
    operation = request.form.get('operation', '')

    dataset_mapping = {
        'tourist_places': 'tourist_places',
        'visitor_statistics': 'visitor_statistics',
        'reviews': 'reviews',
        'hotels': 'hotels',
        'restaurants': 'restaurants',
        'events': 'events',
        'weather': 'weather'
    }

    table_name = dataset_mapping.get(dataset, 'tourist_places')
    df = get_db_data(f"SELECT * FROM {table_name}")

    if df.empty:
        return redirect(url_for('curation', dataset=dataset))

    if operation == 'remove_duplicates':
        from data_curation import remove_duplicates
        df_cleaned = remove_duplicates(df)
    elif operation == 'handle_missing':
        df_cleaned = handle_missing_values(df, 'fill')
    elif operation == 'standardize':
        df_cleaned = standardize_data(df)
    else:
        df_cleaned = df

    # Save cleaned data back to database
    conn = get_db_connection()
    df_cleaned.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()

    return redirect(url_for('curation', dataset=dataset))


@app.route('/quality-report')
def quality_report():
    """Generate and display quality report."""
    dataset = request.args.get('dataset', 'tourist_places')

    dataset_mapping = {
        'tourist_places': 'tourist_places',
        'visitor_statistics': 'visitor_statistics',
        'reviews': 'reviews',
        'hotels': 'hotels',
        'restaurants': 'restaurants',
        'events': 'events',
        'weather': 'weather'
    }

    table_name = dataset_mapping.get(dataset, 'tourist_places')
    df = get_db_data(f"SELECT * FROM {table_name}")

    report = generate_quality_report(df, dataset)

    return render_template('quality_report.html',
                           report=report,
                           dataset=dataset
                           )

# =============================================================================
# API Routes
# =============================================================================


@app.route('/api/places')
def api_places():
    """API endpoint for places."""
    limit = request.args.get('limit', 100, type=int)
    df = get_db_data(f"SELECT * FROM tourist_places LIMIT {limit}")
    return jsonify(df.to_dict('records'))


@app.route('/api/visitors')
def api_visitors():
    """API endpoint for visitor statistics."""
    place_id = request.args.get('place_id')
    df = get_visitor_data(place_id)
    return jsonify(df.to_dict('records'))


@app.route('/api/reviews')
def api_reviews():
    """API endpoint for reviews."""
    place_id = request.args.get('place_id')
    df = get_review_data(place_id)
    return jsonify(df.to_dict('records'))

# =============================================================================
# Error Handlers
# =============================================================================


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

# =============================================================================
# Main
# =============================================================================


if __name__ == '__main__':
    # Initialize database if needed
    if not os.path.exists('database/tourism_platform.db'):
        from database.seed import init_database
        init_database()
        from ml.train_model import train_all_models
        train_all_models()

    app.run(debug=True, host='0.0.0.0', port=5000)
