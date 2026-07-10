import csv
import os
import sqlite3
from datetime import datetime

def get_db_connection(db_path='database/tourism_platform.db'):
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def import_csv_to_table(csv_file, table_name, db_path='database/tourism_platform.db'):
    """Import CSV file into the specified table, skipping duplicates."""
    if not os.path.exists(csv_file):
        print(f"⚠️ CSV file not found: {csv_file}")
        return 0
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    
    if not rows:
        print(f"⚠️ No data in {csv_file}")
        return 0
    
    # Clear existing data (optional – we may want to keep it, but for seed we clear)
    # Comment out the line below if you want to append instead of replace
    cursor.execute(f"DELETE FROM {table_name}")
    
    # Prepare insert statement with IGNORE to skip duplicates
    placeholders = ', '.join(['?' for _ in columns])
    insert_sql = f"INSERT OR IGNORE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Insert data
    count = 0
    skipped = 0
    for row in rows:
        # Handle empty strings as NULL for numeric fields
        values = []
        for col in columns:
            val = row.get(col, '').strip()
            if val == '':
                val = None
            # Convert numeric strings
            if val is not None and col.lower() not in [
                'place_id', 'place_name', 'district', 'category', 'description', 
                'address', 'opening_time', 'closing_time', 'best_season', 
                'popularity_level', 'family_friendly', 'adventure_level', 
                'accessibility', 'parking_available', 'washroom_available', 
                'wheelchair_accessible', 'official_website', 'image_url', 
                'status', 'created_date', 'updated_date',
                'month_name', 'season', 'weather_condition', 'special_event', 
                'festival_season', 'remarks', 'reviewer_name', 'reviewer_type', 
                'age_group', 'gender', 'nationality', 'travel_month', 
                'travel_season', 'travel_mode', 'travel_group', 'visit_purpose', 
                'review_title', 'review_text', 'sentiment', 'verified_visitor', 
                'review_status', 'hotel_name', 'hotel_type', 'room_type', 
                'air_conditioning', 'free_wifi', 'parking', 'restaurant', 
                'room_service', 'swimming_pool', 'gym', 'spa', 'pet_friendly', 
                'family_friendly', 'wheelchair_accessible', 'airport_shuttle', 
                'breakfast_included', 'cancellation_policy', 'phone_number', 
                'email', 'restaurant_type', 'cuisine', 'indoor_seating', 
                'outdoor_seating', 'takeaway', 'home_delivery', 'online_booking', 
                'vegetarian', 'vegan', 'non_vegetarian', 'local_manipuri_food', 
                'payment_method', 'event_category', 'organizer', 'contact_person', 
                'registration_required', 'age_restriction', 'suitable_for', 
                'food_available', 'parking_available', 'emergency_medical_service', 
                'security_available', 'event_status', 'weather_id'
            ]:
                try:
                    val = float(val) if '.' in str(val) else int(val)
                except (ValueError, TypeError):
                    pass
            values.append(val)
        
        try:
            cursor.execute(insert_sql, values)
            if cursor.rowcount == 0:
                skipped += 1
            else:
                count += 1
        except sqlite3.IntegrityError as e:
            # If somehow a duplicate still slips through, skip it
            skipped += 1
            print(f"  ⚠️ Skipped duplicate row: {row.get('place_id', 'unknown')}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Imported {count} rows into {table_name} from {os.path.basename(csv_file)}")
    if skipped > 0:
        print(f"   ⏭️ Skipped {skipped} duplicate rows.")
    return count

def import_all_datasets(datasets_dir='datasets', db_path='database/tourism_platform.db'):
    """Import all datasets from the datasets directory."""
    table_mappings = {
        'tourist_places.csv': 'tourist_places',
        'visitor_statistics.csv': 'visitor_statistics',
        'reviews.csv': 'reviews',
        'hotels.csv': 'hotels',
        'restaurants.csv': 'restaurants',
        'events.csv': 'events',
        'weather.csv': 'weather'
    }
    
    total = 0
    for csv_file, table_name in table_mappings.items():
        file_path = os.path.join(datasets_dir, csv_file)
        if os.path.exists(file_path):
            count = import_csv_to_table(file_path, table_name, db_path)
            total += count
        else:
            print(f"⚠️ File not found: {file_path}")
    
    print(f"\n📊 Total records imported: {total}")
    return total

if __name__ == '__main__':
    import_all_datasets()