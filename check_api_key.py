#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

def check_api_key():
    """Check if the OpenAI API key is properly configured"""
    # Load from .env file
    load_dotenv()
    
    # Try to get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not api_key:
        print("ERROR: OpenAI API key not found in environment variables or .env file.")
        print("Please check your .env file and ensure it contains:")
        print("OPENAI_API_KEY=your-api-key-here")
        return False
    
    print(f"API Key found: {api_key[:8]}...{api_key[-4:]}")
    return True

if __name__ == "__main__":
    print("Checking OpenAI API Key Configuration:")
    if check_api_key():
        print("Success! API key is properly configured.")
    else:
        print("Failed! API key is not properly configured.")
        sys.exit(1)
