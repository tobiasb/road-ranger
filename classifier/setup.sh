#!/bin/bash

echo "Setting up Road Ranger Classifier..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo "Installing pipenv..."
    pip3 install --user pipenv
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Python dependencies using pipenv
echo "Installing Python dependencies..."
pipenv install

# Check if inspector database exists
if [ ! -f "../inspector/car_detection.db" ]; then
    echo "Warning: Inspector database not found at ../inspector/car_detection.db"
    echo "Make sure the inspector component has been run first to create the database."
fi

# Check if video directory exists
if [ ! -d "../inspector/downloaded_clips" ]; then
    echo "Warning: Video directory not found at ../inspector/downloaded_clips"
    echo "Make sure the inspector component has downloaded some clips."
fi

echo "Setup complete!"
echo ""
echo "To start the classifier web app:"
echo "  cd classifier"
echo "  pipenv run start"
echo ""
echo "Or alternatively:"
echo "  pipenv run python app.py"
echo ""
echo "Then open your browser to: http://localhost:5001"
echo ""
echo "Useful commands:"
echo "  pipenv run test-app      # Test Flask app import"
echo "  pipenv run test-database # Test database connection"