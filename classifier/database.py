"""
Database wrapper for the classifier component
"""

import sys
import os
import importlib.util

# Get the path to the inspector's database module
inspector_db_path = os.path.join(os.path.dirname(__file__), '..', 'inspector', 'database.py')

# Load the inspector's database module
spec = importlib.util.spec_from_file_location("inspector_database", inspector_db_path)
inspector_database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector_database)

import config
import logging
from typing import List, Dict, Optional


class ClassifierDB:
    """
    Database wrapper for the classifier component
    """

    def __init__(self):
        """Initialize the database connection"""
        self.db = inspector_database.CarDetectionDB(config.DATABASE_PATH)
        self.logger = logging.getLogger(__name__)

    def get_unclassified_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get clips that haven't been classified for distraction yet

        Args:
            limit: Maximum number of clips to return

        Returns:
            List of clip dictionaries
        """
        return self.db.get_unanalyzed_distraction_clips(limit)

    def get_classified_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get clips that have been classified for distraction

        Args:
            limit: Maximum number of clips to return

        Returns:
            List of clip dictionaries sorted by processed_at DESC
        """
        # Get both distracted and not distracted clips without limit first
        distracted = self.db.get_distracted_clips(None)  # Get all
        not_distracted = self.db.get_not_distracted_clips(None)  # Get all

        # Combine and sort by processed_at
        all_clips = distracted + not_distracted
        all_clips.sort(key=lambda x: x.get('processed_at', ''), reverse=True)

        # Apply limit after sorting
        if limit:
            return all_clips[:limit]
        return all_clips

    def classify_clip(self, file_path: str, is_distracted: Optional[bool]) -> bool:
        """
        Classify a clip as distracted or not

        Args:
            file_path: Path to the video file
            is_distracted: True for distracted, False for not distracted, None for unknown

        Returns:
            True if classification was successful
        """
        return self.db.update_distraction_analysis(file_path, is_distracted)

    def get_clip_by_path(self, file_path: str) -> Optional[Dict]:
        """
        Get a specific clip by file path

        Args:
            file_path: Path to the video file

        Returns:
            Clip dictionary or None if not found
        """
        return self.db.get_analysis_by_path(file_path)

    def get_statistics(self) -> Dict:
        """
        Get classification statistics

        Returns:
            Dictionary with statistics
        """
        return self.db.get_statistics()

    def get_car_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all clips that contain cars
        """
        return self.db.get_car_clips(limit)

    def get_all_clips(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all clips in the database (regardless of car presence or classification)
        """
        return self.db.get_all_analyses(limit)

    def close(self):
        """Close the database connection"""
        self.db.close()