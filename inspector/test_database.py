#!/usr/bin/env python3
"""
Test script for database functionality
"""

import os
import tempfile
from database import CarDetectionDB
import config


def test_database():
    """Test database functionality"""
    print("Testing database functionality...")

    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        test_db_path = tmp_file.name

    try:
        # Initialize database
        db = CarDetectionDB(test_db_path)
        print("✅ Database initialized successfully")

        # Test saving analysis results
        test_analysis = {
            'video_path': '/path/to/test/video1.mp4',
            'has_cars': True,
            'total_frames': 100,
            'duration': 5.5,
            'frames_analyzed': 15,
            'frames_with_cars': 8,
            'car_ratio': 0.53,
            'total_car_detections': 12,
            'average_cars_per_frame': 0.8,
            'detection_method': 'yolov8x',
            'confidence_threshold': 0.5,
            'min_car_frames': 2
        }

        success = db.save_analysis_result(test_analysis)
        if success:
            print("✅ Analysis result saved successfully")
        else:
            print("❌ Failed to save analysis result")
            return False

        # Test saving another result
        test_analysis2 = {
            'video_path': '/path/to/test/video2.mp4',
            'has_cars': False,
            'total_frames': 80,
            'duration': 4.0,
            'frames_analyzed': 15,
            'frames_with_cars': 0,
            'car_ratio': 0.0,
            'total_car_detections': 0,
            'average_cars_per_frame': 0.0,
            'detection_method': 'yolov8x',
            'confidence_threshold': 0.5,
            'min_car_frames': 2
        }

        success = db.save_analysis_result(test_analysis2)
        if success:
            print("✅ Second analysis result saved successfully")
        else:
            print("❌ Failed to save second analysis result")
            return False

        # Test saving a result with distraction analysis
        test_analysis3 = {
            'video_path': '/path/to/test/video3.mp4',
            'has_cars': True,
            'is_distracted': True,
            'total_frames': 120,
            'duration': 6.0,
            'frames_analyzed': 15,
            'frames_with_cars': 12,
            'car_ratio': 0.8,
            'total_car_detections': 18,
            'average_cars_per_frame': 1.2,
            'detection_method': 'yolov8x',
            'confidence_threshold': 0.5,
            'min_car_frames': 2
        }

        success = db.save_analysis_result(test_analysis3)
        if success:
            print("✅ Third analysis result with distraction saved successfully")
        else:
            print("❌ Failed to save third analysis result")
            return False

        # Test statistics
        stats = db.get_statistics()
        expected_stats = {
            'total_clips': 3,
            'with_cars': 2,
            'without_cars': 1,
            'errors': 0,
            'distracted': 1,
            'not_distracted': 0,
            'unanalyzed_distraction': 1,
            'avg_car_ratio': 0.665,  # Average of 0.53 and 0.8
            'success_rate': 100.0,
            'distraction_analysis_rate': 50.0  # 1 out of 2 car clips analyzed
        }

        # Check if stats match (allowing for floating point precision)
        stats_match = True
        for key, expected_value in expected_stats.items():
            if key in ['avg_car_ratio']:
                if abs(stats[key] - expected_value) > 0.01:
                    stats_match = False
                    print(f"❌ Stats mismatch for {key}: expected {expected_value}, got {stats[key]}")
            elif stats[key] != expected_value:
                stats_match = False
                print(f"❌ Stats mismatch for {key}: expected {expected_value}, got {stats[key]}")

        if stats_match:
            print("✅ Statistics calculated correctly")
        else:
            print(f"❌ Statistics mismatch. Expected: {expected_stats}, Got: {stats}")
            return False

        # Test getting clips by category
        car_clips = db.get_car_clips()
        if len(car_clips) == 2:
            print("✅ Car clips retrieved correctly")
        else:
            print("❌ Car clips retrieval failed")
            return False

        no_car_clips = db.get_no_car_clips()
        if len(no_car_clips) == 1 and no_car_clips[0]['filename'] == 'video2.mp4':
            print("✅ No-car clips retrieved correctly")
        else:
            print("❌ No-car clips retrieval failed")
            return False

        distracted_clips = db.get_distracted_clips()
        if len(distracted_clips) == 1 and distracted_clips[0]['filename'] == 'video3.mp4':
            print("✅ Distracted clips retrieved correctly")
        else:
            print("❌ Distracted clips retrieval failed")
            return False

        unanalyzed_distraction_clips = db.get_unanalyzed_distraction_clips()
        if len(unanalyzed_distraction_clips) == 1 and unanalyzed_distraction_clips[0]['filename'] == 'video1.mp4':
            print("✅ Unanalyzed distraction clips retrieved correctly")
        else:
            print("❌ Unanalyzed distraction clips retrieval failed")
            return False

        # Test updating distraction analysis
        success = db.update_distraction_analysis('/path/to/test/video1.mp4', False)
        if success:
            print("✅ Distraction analysis update works correctly")
        else:
            print("❌ Distraction analysis update failed")
            return False

        # Test file processing check
        if db.is_file_processed('/path/to/test/video1.mp4'):
            print("✅ File processing check works correctly")
        else:
            print("❌ File processing check failed")
            return False

        # Test unprocessed files
        test_files = ['/path/to/test/video1.mp4', '/path/to/test/video2.mp4', '/path/to/test/video3.mp4', '/path/to/test/video4.mp4']
        unprocessed = db.get_unprocessed_files(test_files)
        if unprocessed == ['/path/to/test/video4.mp4']:
            print("✅ Unprocessed files detection works correctly")
        else:
            print("❌ Unprocessed files detection failed")
            return False

        print("\n🎉 All database tests passed!")
        return True

    finally:
        # Clean up temporary database
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_main_database():
    """Test the main database configuration"""
    print("\nTesting main database configuration...")

    try:
        db = CarDetectionDB(config.DATABASE_PATH)
        print(f"✅ Main database initialized: {config.DATABASE_PATH}")

        stats = db.get_statistics()
        print(f"✅ Database statistics: {stats}")

        return True
    except Exception as e:
        print(f"❌ Main database test failed: {e}")
        return False


def main():
    """Main test function"""
    print("Database Test Suite")
    print("==================")

    # Test database functionality
    if not test_database():
        print("❌ Database functionality tests failed")
        return False

    # Test main database
    if not test_main_database():
        print("❌ Main database test failed")
        return False

    print("\n✅ All tests passed!")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)