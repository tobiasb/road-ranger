# Road Ranger Classifier

The **Classifier** component is the third part of the Road Ranger system, providing a web-based interface for manually classifying video clips for driver distraction analysis.

## Overview

After the **Watcher** component records video clips and the **Inspector** component analyzes them for car detection, the **Classifier** component allows human reviewers to:

- View clips that contain cars but haven't been classified for driver distraction
- Play videos directly in the browser
- Classify each clip as:
  - **Yes** - Driver is distracted
  - **No** - Driver is not distracted
  - **Don't Know/Unsure** - Unable to determine (will appear again later)

## Features

### 🎥 Video Player
- Built-in HTML5 video player
- Supports MP4, AVI, MOV, and MKV formats
- Auto-play option (configurable)
- Keyboard shortcuts for quick classification

### 📊 Statistics Dashboard
- Real-time statistics showing:
  - Total clips processed
  - Clips with cars detected
  - Unclassified clips remaining
  - Previously classified clips

### 🔍 Classification Interface
- Clean, modern UI with Bootstrap 5
- Three classification buttons with clear visual indicators
- Smooth animations and feedback
- Keyboard shortcuts (1, 2, 3 keys)

### 📚 History & Review
- View all previously classified clips
- Filter by classification type
- Sort by various criteria
- Reclassify clips if needed

### ⚡ Performance
- Efficient database queries
- Pagination for large datasets
- Responsive design for mobile/tablet use

## Installation

1. **Prerequisites**: Make sure you have Python 3 and pipenv installed

2. **Setup**: Run the setup script:
   ```bash
   cd classifier
   ./setup.sh
   ```

3. **Dependencies**: The setup script will install:
   - Flask 2.3.3
   - Werkzeug 2.3.7

## Configuration

Edit `config.py` to customize the application:

```python
# Flask settings
FLASK_HOST = "0.0.0.0"  # Listen on all interfaces
FLASK_PORT = 5001       # Port number

# Database settings
DATABASE_PATH = "../inspector/car_detection.db"  # Path to inspector database

# Video settings
VIDEO_DIR = "../inspector/downloaded_clips"  # Path to video files
MAX_VIDEOS_PER_PAGE = 20  # Number of clips per page

# UI settings
AUTO_PLAY_VIDEOS = False  # Auto-play videos when loaded
```

## Usage

### Starting the Application

```bash
cd classifier
pipenv run start
```

Or alternatively:
```bash
pipenv run python app.py
```

The web interface will be available at: **http://localhost:5001**

### Useful Commands

```bash
pipenv run test-app      # Test Flask app import
pipenv run test-database # Test database connection
```

### Workflow

1. **Review Unclassified Clips**: The main page shows clips that need classification
2. **Watch & Classify**: Play each video and click the appropriate classification button
3. **Track Progress**: Monitor statistics to see how many clips remain
4. **Review History**: Use the history page to review and potentially reclassify clips

### Keyboard Shortcuts

- **1** - Classify as "Yes" (Distracted)
- **2** - Classify as "No" (Not Distracted)
- **3** - Classify as "Unknown/Unsure"

### API Endpoints

- `GET /` - Main classification interface
- `GET /history` - Classification history
- `POST /classify` - Submit classification
- `GET /video/<filename>` - Serve video files
- `GET /api/stats` - Get statistics
- `GET /api/unclassified` - Get unclassified clips

## Database Integration

The Classifier connects to the same SQLite database used by the Inspector component:

- **Table**: `video_analysis`
- **Key Column**: `is_distracted` (BOOLEAN, can be NULL)
- **Updates**: Classification results are stored immediately

### Database Schema

```sql
CREATE TABLE video_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    is_car BOOLEAN NOT NULL,
    is_distracted BOOLEAN DEFAULT NULL,  -- NULL = unclassified
    -- ... other columns
);
```

## File Structure

```
classifier/
├── __init__.py
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── database.py         # Database wrapper
├── Pipfile            # Python dependencies and scripts
├── setup.sh           # Setup script
├── README.md          # This file
└── templates/         # HTML templates
    ├── base.html      # Base template
    ├── index.html     # Main classification page
    ├── history.html   # History page
    └── error.html     # Error page
```

## Troubleshooting

### Common Issues

1. **Database not found**: Make sure the Inspector component has been run first
2. **Videos not loading**: Check that video files exist in the configured directory
3. **Port already in use**: Change the port in `config.py`
4. **pipenv not found**: Run `pip3 install --user pipenv` and add to PATH

### Logs

The application logs to the console. Check for error messages when starting up.

## Development

### Adding Features

1. **New Classification Types**: Modify `CLASSIFICATION_OPTIONS` in `config.py`
2. **Additional Filters**: Extend the database queries in `database.py`
3. **UI Improvements**: Update the Bootstrap templates in `templates/`

### Testing

Test the application by:
1. Running the Inspector on some sample clips
2. Starting the Classifier with `pipenv run start`
3. Classifying a few clips
4. Checking the history page

## Integration with Other Components

- **Watcher**: Records video clips → **Inspector**: Analyzes for cars → **Classifier**: Manual classification
- All components share the same database for seamless data flow
- Video files are served directly from the Inspector's download directory

## License

Part of the Road Ranger project - see main project README for license information.