# admin.py
from flask import Blueprint, render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Note: You need to create these models first
# If you want to use Flask-Admin, you'll need to define models

# Simple admin dashboard without Flask-Admin (works immediately)


@admin_bp.route('/')
def dashboard():
    from database.import_csv import get_db_connection
    conn = get_db_connection()
    tables = ['tourist_places', 'visitor_statistics',
              'reviews', 'hotels', 'restaurants', 'events', 'weather']
    stats = {}
    for table in tables:
        cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
        stats[table] = cursor.fetchone()[0]
    conn.close()
    return render_template('admin.html', stats=stats)
