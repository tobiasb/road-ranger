"""
Database module for storing car detection analysis results
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class CarDetectionDB:
    """
    SQLite database for storing car detection analysis results
    """

    def __init__(self, db_path: str = "car_detection.db"):
        """
        Initialize the database

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create video_analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS video_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL UNIQUE,
                    is_car BOOLEAN NOT NULL,
                    is_distracted BOOLEAN DEFAULT NULL,
                    total_frames INTEGER,
                    duration REAL,
                    frames_analyzed INTEGER,
                    frames_with_cars INTEGER,
                    car_ratio REAL,
                    total_car_detections INTEGER,
                    average_cars_per_frame REAL,
                    detection_method TEXT,
                    confidence_threshold REAL,
                    min_car_frames INTEGER,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error_message TEXT,
                    UNIQUE(file_path)
                )
            """)

            # Check if is_distracted column exists, add it if it doesn't
            cursor.execute("PRAGMA table_info(video_analysis)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'is_distracted' not in columns:
                cursor.execute("""
                    ALTER TABLE video_analysis
                    ADD COLUMN is_distracted BOOLEAN DEFAULT NULL
                """)
                self.logger.info("Added is_distracted column to video_analysis table")

            # Create index on filename for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_filename
                ON video_analysis(filename)
            """)

            # Create index on is_car for filtering
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_is_car
                ON video_analysis(is_car)
            """)

            # Create index on is_distracted for filtering
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_is_distracted
                ON video_analysis(is_distracted)
            """)

            conn.commit()
            self.logger.info(f"Database initialized: {self.db_path}")

    def save_analysis_result(self, analysis_result: Dict) -> bool:
        """
        Save analysis result to database

        Args:
            analysis_result: Dictionary containing analysis results

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if file already exists
                cursor.execute(
                    "SELECT id FROM video_analysis WHERE file_path = ?",
                    (analysis_result.get('video_path', ''),)
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing record
                    cursor.execute("""
                        UPDATE video_analysis SET
                            is_car = ?,
                            is_distracted = ?,
                            total_frames = ?,
                            duration = ?,
                            frames_analyzed = ?,
                            frames_with_cars = ?,
                            car_ratio = ?,
                            total_car_detections = ?,
                            average_cars_per_frame = ?,
                            detection_method = ?,
                            confidence_threshold = ?,
                            min_car_frames = ?,
                            processed_at = CURRENT_TIMESTAMP,
                            error_message = ?
                        WHERE file_path = ?
                    """, (
                        analysis_result.get('has_cars', False),
                        analysis_result.get('is_distracted'),
                        analysis_result.get('total_frames'),
                        analysis_result.get('duration'),
                        analysis_result.get('frames_analyzed'),
                        analysis_result.get('frames_with_cars'),
                        analysis_result.get('car_ratio'),
                        analysis_result.get('total_car_detections'),
                        analysis_result.get('average_cars_per_frame'),
                        analysis_result.get('detection_method'),
                        analysis_result.get('confidence_threshold'),
                        analysis_result.get('min_car_frames'),
                        analysis_result.get('error'),
                        analysis_result.get('video_path', '')
                    ))
                    self.logger.debug(f"Updated analysis for: {analysis_result.get('video_path')}")
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO video_analysis (
                            filename, file_path, is_car, is_distracted, total_frames, duration,
                            frames_analyzed, frames_with_cars, car_ratio,
                            total_car_detections, average_cars_per_frame,
                            detection_method, confidence_threshold, min_car_frames,
                            error_message
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        os.path.basename(analysis_result.get('video_path', 'unknown')),
                        analysis_result.get('video_path', ''),
                        analysis_result.get('has_cars', False),
                        analysis_result.get('is_distracted'),
                        analysis_result.get('total_frames'),
                        analysis_result.get('duration'),
                        analysis_result.get('frames_analyzed'),
                        analysis_result.get('frames_with_cars'),
                        analysis_result.get('car_ratio'),
                        analysis_result.get('total_car_detections'),
                        analysis_result.get('average_cars_per_frame'),
                        analysis_result.get('detection_method'),
                        analysis_result.get('confidence_threshold'),
                        analysis_result.get('min_car_frames'),
                        analysis_result.get('error')
                    ))
                    self.logger.debug(f"Saved analysis for: {analysis_result.get('video_path')}")

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error saving analysis result: {e}")
            return False

    def get_analysis_by_filename(self, filename: str) -> Optional[Dict]:
        """
        Get analysis result by filename

        Args:
            filename: Name of the video file

        Returns:
            Analysis result dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM video_analysis WHERE filename = ?
                """, (filename,))

                row = cursor.fetchone()
                if row:
                    return self._row_to_dict(row)
                return None

        except Exception as e:
            self.logger.error(f"Error getting analysis by filename: {e}")
            return None

    def get_analysis_by_path(self, file_path: str) -> Optional[Dict]:
        """
        Get analysis result by file path

        Args:
            file_path: Full path to the video file

        Returns:
            Analysis result dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM video_analysis WHERE file_path = ?
                """, (file_path,))

                row = cursor.fetchone()
                if row:
                    return self._row_to_dict(row)
                return None

        except Exception as e:
            self.logger.error(f"Error getting analysis by path: {e}")
            return None

    def get_all_analyses(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all analysis results

        Args:
            limit: Maximum number of results to return

        Returns:
            List of analysis result dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM video_analysis ORDER BY processed_at DESC"
                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query)
                rows = cursor.fetchall()

                return [self._row_to_dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting all analyses: {e}")
            return []

    def get_car_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all clips that contain cars

        Args:
            limit: Maximum number of results to return

        Returns:
            List of analysis result dictionaries for clips with cars
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM video_analysis WHERE is_car = 1 ORDER BY processed_at DESC"
                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query)
                rows = cursor.fetchall()

                return [self._row_to_dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting car clips: {e}")
            return []

    def get_no_car_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all clips that don't contain cars

        Args:
            limit: Maximum number of results to return

        Returns:
            List of analysis result dictionaries for clips without cars
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM video_analysis WHERE is_car = 0 ORDER BY processed_at DESC"
                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query)
                rows = cursor.fetchall()

                return [self._row_to_dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting no-car clips: {e}")
            return []

    def get_distracted_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all clips where driver is distracted

        Args:
            limit: Maximum number of results to return

        Returns:
            List of analysis result dictionaries for clips with distracted drivers
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM video_analysis WHERE is_distracted = 1 ORDER BY processed_at DESC"
                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query)
                rows = cursor.fetchall()

                return [self._row_to_dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting distracted clips: {e}")
            return []

    def get_not_distracted_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all clips where driver is not distracted

        Args:
            limit: Maximum number of results to return

        Returns:
            List of analysis result dictionaries for clips with non-distracted drivers
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM video_analysis WHERE is_distracted = 0 ORDER BY processed_at DESC"
                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query)
                rows = cursor.fetchall()

                return [self._row_to_dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting not-distracted clips: {e}")
            return []

    def get_unanalyzed_distraction_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all clips that have cars but haven't been analyzed for distraction yet

        Args:
            limit: Maximum number of results to return

        Returns:
            List of analysis result dictionaries for clips needing distraction analysis
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM video_analysis WHERE is_car = 1 AND is_distracted IS NULL ORDER BY processed_at DESC"
                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query)
                rows = cursor.fetchall()

                return [self._row_to_dict(row) for row in rows]

        except Exception as e:
            self.logger.error(f"Error getting unanalyzed distraction clips: {e}")
            return []

    def update_distraction_analysis(self, file_path: str, is_distracted: bool) -> bool:
        """
        Update the distraction analysis for a specific file

        Args:
            file_path: Path to the video file
            is_distracted: Whether the driver is distracted

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE video_analysis
                    SET is_distracted = ?, processed_at = CURRENT_TIMESTAMP
                    WHERE file_path = ?
                """, (is_distracted, file_path))

                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.debug(f"Updated distraction analysis for: {file_path}")
                    return True
                else:
                    self.logger.warning(f"No record found for: {file_path}")
                    return False

        except Exception as e:
            self.logger.error(f"Error updating distraction analysis: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        Get overall statistics about the analysis

        Returns:
            Dictionary with statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get total counts
                cursor.execute("SELECT COUNT(*) FROM video_analysis")
                total_clips = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM video_analysis WHERE is_car = 1")
                with_cars = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM video_analysis WHERE is_car = 0")
                without_cars = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM video_analysis WHERE error_message IS NOT NULL")
                errors = cursor.fetchone()[0]

                # Get distraction statistics
                cursor.execute("SELECT COUNT(*) FROM video_analysis WHERE is_distracted = 1")
                distracted = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM video_analysis WHERE is_distracted = 0")
                not_distracted = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM video_analysis WHERE is_car = 1 AND is_distracted IS NULL")
                unanalyzed_distraction = cursor.fetchone()[0]

                # Get average car ratio
                cursor.execute("SELECT AVG(car_ratio) FROM video_analysis WHERE is_car = 1")
                avg_car_ratio = cursor.fetchone()[0] or 0

                return {
                    'total_clips': total_clips,
                    'with_cars': with_cars,
                    'without_cars': without_cars,
                    'errors': errors,
                    'distracted': distracted,
                    'not_distracted': not_distracted,
                    'unanalyzed_distraction': unanalyzed_distraction,
                    'avg_car_ratio': avg_car_ratio,
                    'success_rate': ((with_cars + without_cars) / total_clips * 100) if total_clips > 0 else 0,
                    'distraction_analysis_rate': ((distracted + not_distracted) / with_cars * 100) if with_cars > 0 else 0
                }

        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {
                'total_clips': 0,
                'with_cars': 0,
                'without_cars': 0,
                'errors': 0,
                'distracted': 0,
                'not_distracted': 0,
                'unanalyzed_distraction': 0,
                'avg_car_ratio': 0,
                'success_rate': 0,
                'distraction_analysis_rate': 0
            }

    def is_file_processed(self, file_path: str) -> bool:
        """
        Check if a file has already been processed

        Args:
            file_path: Path to the video file

        Returns:
            True if file has been processed, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM video_analysis WHERE file_path = ?
                """, (file_path,))

                return cursor.fetchone() is not None

        except Exception as e:
            self.logger.error(f"Error checking if file processed: {e}")
            return False

    def get_unprocessed_files(self, file_paths: List[str]) -> List[str]:
        """
        Get list of files that haven't been processed yet

        Args:
            file_paths: List of file paths to check

        Returns:
            List of file paths that haven't been processed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Create placeholders for the IN clause
                placeholders = ','.join(['?' for _ in file_paths])
                cursor.execute(f"""
                    SELECT file_path FROM video_analysis
                    WHERE file_path IN ({placeholders})
                """, file_paths)

                processed_paths = {row[0] for row in cursor.fetchall()}
                return [path for path in file_paths if path not in processed_paths]

        except Exception as e:
            self.logger.error(f"Error getting unprocessed files: {e}")
            return file_paths

    def _row_to_dict(self, row: Tuple) -> Dict:
        """
        Convert database row to dictionary

        Args:
            row: Database row tuple

        Returns:
            Dictionary representation of the row
        """
        columns = [
            'id', 'filename', 'file_path', 'is_car', 'total_frames', 'duration',
            'frames_analyzed', 'frames_with_cars', 'car_ratio', 'total_car_detections',
            'average_cars_per_frame', 'detection_method', 'confidence_threshold',
            'min_car_frames', 'processed_at', 'error_message', 'is_distracted'
        ]

        return dict(zip(columns, row))

    def clear_database(self):
        """Clear all data from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM video_analysis")
                conn.commit()
                self.logger.info("Database cleared")
        except Exception as e:
            self.logger.error(f"Error clearing database: {e}")

    def close(self):
        """Close database connection"""
        # SQLite connections are automatically closed when using context managers
        pass