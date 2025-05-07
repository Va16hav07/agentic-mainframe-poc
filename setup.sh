#!/bin/bash

echo "Setting up the Document Search Demo environment..."

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! You can now run the application with:"
echo "source venv/bin/activate"
echo "python -m uvicorn main:app --reload"
