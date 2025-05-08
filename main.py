#!/usr/bin/env python3

import argparse
import os
import sys
from agents.agent_factory import create_agent
from utils.config import load_config

def main():
    """
    Main entry point for the Agentic Mainframe Modernization POC.
    """
    parser = argparse.ArgumentParser(description='Agentic Mainframe Modernization POC')
    parser.add_argument('--mode', choices=['analyze', 'document', 'transform'], 
                      help='Mode of operation')
    parser.add_argument('--source', help='Source file or directory')
    parser.add_argument('--output', help='Output file or directory')
    parser.add_argument('--config', default='config.yaml', help='Configuration file')
    
    args = parser.parse_args()
    
    # Show help message if no arguments provided
    if len(sys.argv) == 1 or not args.mode or not args.source:
        print("Agentic Mainframe Modernization POC")
        print("===================================")
        print("\nUsage examples:")
        print("  Analyze:   python main.py --mode analyze --source examples/sample.cbl --output analysis.json")
        print("  Document:  python main.py --mode document --source examples/sample.cbl --output docs")
        print("  Transform: python main.py --mode transform --source examples/sample.cbl --output transformed/sample.java")
        print("\nFor detailed instructions, see GETTING_STARTED.md")
        return
    
    config = load_config(args.config)
    
    # Add warning about free tier usage - with safer access
    if config.get("llm", {}).get("api_key") and config.get("llm", {}).get("rate_limit", False):
        print("\n  NOTICE: Running with free tier OpenAI API key.")
        print("    Expect potential rate limiting and reduced capabilities.")
        print("    For better performance, consider using a paid API key.\n")
    
    # Make sure output directory exists if we're writing to a file in a new directory
    if args.output and os.path.dirname(args.output) and not os.path.exists(os.path.dirname(args.output)):
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Create and run the appropriate agent
    try:
        agent = create_agent(args.mode, config)
        result = agent.process(args.source, args.output)
        
        print(f"Agent completed task. Result: {result}")
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
