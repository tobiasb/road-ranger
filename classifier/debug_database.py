#!/usr/bin/env python3
"""
Debug script to test database connection and data retrieval
"""

import os
import sys
from database import ClassifierDB
import config

def debug_database():
    """Debug database connection and data retrieval"""
    print("🔍 Debugging Classifier Database Connection")
    print("=" * 50)

    # Check if database file exists
    db_path = os.path.abspath(config.DATABASE_PATH)
    print(f"Database path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")

    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return

    try:
        # Initialize database
        db = ClassifierDB()
        print("✅ Database connection successful")

        # Get statistics
        stats = db.get_statistics()
        print(f"\n📊 Statistics:")
        print(f"  Total clips: {stats.get('total_clips', 0)}")
        print(f"  With cars: {stats.get('with_cars', 0)}")
        print(f"  Without cars: {stats.get('without_cars', 0)}")
        print(f"  Distracted: {stats.get('distracted', 0)}")
        print(f"  Not distracted: {stats.get('not_distracted', 0)}")
        print(f"  Unanalyzed distraction: {stats.get('unanalyzed_distraction', 0)}")

        # Test different clip retrieval methods
        print(f"\n🔍 Testing clip retrieval methods:")

        # Test unclassified clips
        unclassified = db.get_unclassified_clips(3)
        print(f"\n📋 Unclassified clips (first 3):")
        for i, clip in enumerate(unclassified):
            print(f"  {i+1}. {clip.get('filename', 'Unknown')}")
            print(f"     processed_at: {clip.get('processed_at', 'None')}")
            print(f"     is_car: {clip.get('is_car', 'None')}")
            print(f"     is_distracted: {clip.get('is_distracted', 'None')}")

        # Test classified clips
        classified = db.get_classified_clips(3)
        print(f"\n📋 Classified clips (first 3):")
        for i, clip in enumerate(classified):
            print(f"  {i+1}. {clip.get('filename', 'Unknown')}")
            print(f"     processed_at: {clip.get('processed_at', 'None')}")
            print(f"     is_car: {clip.get('is_car', 'None')}")
            print(f"     is_distracted: {clip.get('is_distracted', 'None')}")

        # Test car clips
        car_clips = db.get_car_clips(3)
        print(f"\n📋 Car clips (first 3):")
        for i, clip in enumerate(car_clips):
            print(f"  {i+1}. {clip.get('filename', 'Unknown')}")
            print(f"     processed_at: {clip.get('processed_at', 'None')}")
            print(f"     is_car: {clip.get('is_car', 'None')}")
            print(f"     is_distracted: {clip.get('is_distracted', 'None')}")

        # Test direct database query
        print(f"\n🔍 Direct database query test:")
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filename, processed_at, is_car, is_distracted FROM video_analysis LIMIT 3")
            rows = cursor.fetchall()
            for i, row in enumerate(rows):
                print(f"  {i+1}. {row[0]} | processed_at: {row[1]} | is_car: {row[2]} | is_distracted: {row[3]}")

        print(f"\n✅ Debug complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database()