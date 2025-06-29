"""
Flask web application for manual clip classification
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, abort
import os
import logging
from database import ClassifierDB
import config
from werkzeug.utils import safe_join
import re
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize database
db = ClassifierDB()


def extract_datetime_from_filename(filename):
    """Extract datetime from filename like motion_20250626_124450_6s.mp4 -> 2025-06-26 12:44:50"""
    match = re.search(r'(\d{8})_(\d{6})', filename)
    if match:
        date_str, time_str = match.groups()
        try:
            dt = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
            return dt
        except Exception:
            return None
    return None


@app.route('/')
def index():
    """Main page showing unclassified clips or filtered clips"""
    try:
        filter_type = request.args.get('filter', 'unclassified')
        if filter_type == 'with_cars':
            clips = db.get_car_clips(config.MAX_VIDEOS_PER_PAGE)
        elif filter_type == 'classified':
            clips = db.get_classified_clips(config.MAX_VIDEOS_PER_PAGE)
        elif filter_type == 'unclassified':
            clips = db.get_unclassified_clips(config.MAX_VIDEOS_PER_PAGE)
        elif filter_type == 'all':
            clips = db.get_all_clips(config.MAX_VIDEOS_PER_PAGE)
            print("DEBUG: All clips being sent to template:")
            for clip in clips:
                print(f"  {clip.get('filename')} | is_car={clip.get('is_car')} | file_path={clip.get('file_path')}")
        else:
            clips = db.get_unclassified_clips(config.MAX_VIDEOS_PER_PAGE)

        # Compute relative path for each clip (now just the filename)
        for clip in clips:
            clip['video_rel_path'] = clip['filename']

        # Get statistics
        stats = db.get_statistics()

        # Debug print for processed_at
        print("DEBUG CLIPS:", [{k: v for k, v in clip.items() if k in ('filename', 'processed_at')} for clip in clips[:3]])

        # Add recorded_at and recorded_date from filename
        for clip in clips:
            dt = extract_datetime_from_filename(clip.get('filename', ''))
            if dt:
                clip['recorded_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                clip['recorded_date'] = dt.strftime('%Y-%m-%d')
            else:
                clip['recorded_at'] = None
                clip['recorded_date'] = None

        # Sort by recorded_at descending (newest first)
        clips.sort(key=lambda c: c.get('recorded_at', ''), reverse=True)

        return render_template('index.html',
                             clips=clips,
                             stats=stats,
                             config=config,
                             filter_type=filter_type)
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        return render_template('error.html', error=str(e))


@app.route('/history')
def history():
    """Page showing classified clips history"""
    try:
        # Get classified clips
        classified = db.get_classified_clips(config.MAX_VIDEOS_PER_PAGE)

        # Add recorded_at and recorded_date from filename
        for clip in classified:
            dt = extract_datetime_from_filename(clip.get('filename', ''))
            if dt:
                clip['recorded_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                clip['recorded_date'] = dt.strftime('%Y-%m-%d')
            else:
                clip['recorded_at'] = None
                clip['recorded_date'] = None

        # Sort by recorded_at descending (newest first)
        classified.sort(key=lambda c: c.get('recorded_at', ''), reverse=True)

        return render_template('history.html',
                             clips=classified,
                             config=config)
    except Exception as e:
        logger.error(f"Error loading history: {e}")
        return render_template('error.html', error=str(e))


@app.route('/classify', methods=['POST'])
def classify_clip():
    """API endpoint to classify a clip"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        classification = data.get('classification')  # 'yes', 'no', or 'unknown'

        if not file_path or classification not in config.CLASSIFICATION_OPTIONS:
            return jsonify({'success': False, 'error': 'Invalid parameters'}), 400

        # Convert classification string to boolean/None
        is_distracted = config.CLASSIFICATION_OPTIONS[classification]

        # Update database
        success = db.classify_clip(file_path, is_distracted)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Database update failed'}), 500

    except Exception as e:
        logger.error(f"Error classifying clip: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/video/<path:filename>')
def serve_video(filename):
    """Serve video files from VIDEO_DIR, including subfolders, safely"""
    try:
        video_dir = os.path.abspath(config.VIDEO_DIR)
        # Prevent directory traversal
        safe_path = safe_join(video_dir, filename)
        if not safe_path or not os.path.isfile(safe_path) or not safe_path.startswith(video_dir):
            abort(404)
        return send_from_directory(video_dir, filename)
    except Exception as e:
        logger.error(f"Error serving video {filename}: {e}")
        return jsonify({'error': 'Video not found'}), 404


@app.route('/api/stats')
def get_stats():
    """API endpoint to get statistics"""
    try:
        stats = db.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/unclassified')
def get_unclassified():
    """API endpoint to get unclassified clips"""
    try:
        clips = db.get_unclassified_clips(config.MAX_VIDEOS_PER_PAGE)

        # Add recorded_at and recorded_date from filename
        for clip in clips:
            dt = extract_datetime_from_filename(clip.get('filename', ''))
            if dt:
                clip['recorded_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                clip['recorded_date'] = dt.strftime('%Y-%m-%d')
            else:
                clip['recorded_at'] = None
                clip['recorded_date'] = None

        # Sort by recorded_at descending (newest first)
        clips.sort(key=lambda c: c.get('recorded_at', ''), reverse=True)

        return jsonify(clips)
    except Exception as e:
        logger.error(f"Error getting unclassified clips: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info(f"Starting Classifier web app on {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG)