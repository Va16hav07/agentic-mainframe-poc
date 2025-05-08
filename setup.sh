#!/bin/bash

echo "Setting up the Document Search Demo environment..."

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Ensure pip is up to date
echo "Upgrading pip..."
pip install --upgrade pip

# Install numpy explicitly first to ensure version compatibility
echo "Installing numpy..."
pip install numpy==1.24.3

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! You can now run the application with:"
echo "source venv/bin/activate"
echo "python -m uvicorn main:app --reload"
