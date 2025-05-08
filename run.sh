#!/bin/bash

# Script to easily run the Agentic Mainframe Modernization POC

# Make script executable
if [ ! -x "$0" ]; then
    chmod +x "$0"
    echo "Made script executable."
    exec "$0" "$@"  # Re-execute with the new permissions
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run the main script with all arguments
python main.py "$@"
