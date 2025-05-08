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
    parser.add_argument('--mode', choices=['analyze', 'document', 'transform', 'plan', 'dependency'], 
                      help='Mode of operation')
    parser.add_argument('--source', help='Source file or directory')
    parser.add_argument('--output', help='Output file or directory')
    parser.add_argument('--config', default='config.yaml', help='Configuration file')
    parser.add_argument('--project', help='Project name for organizing multiple operations')
    parser.add_argument('--phase', choices=['discovery', 'design', 'transform', 'test', 'deploy'],
                      help='Modernization phase for planning operations')
    
    args = parser.parse_args()
    
    # Show help message if no arguments provided
    if len(sys.argv) == 1 or not args.mode or not args.source:
        print("Agentic Mainframe Modernization POC")
        print("===================================")
        print("\nAddressing key modernization challenges:")
        print("  - Generating missing application documentation")
        print("  - Creating comprehensive transformation plans")
        print("  - Automating code conversion with minimal iterations")
        print("  - Identifying technical and resource dependencies")
        print("  - Reducing dependency on original application teams")
        
        print("\nUsage examples:")
        print("  Analyze:     python main.py --mode analyze --source examples/sample.cbl --output analysis.json")
        print("  Document:    python main.py --mode document --source examples/sample.cbl --output docs")
        print("  Transform:   python main.py --mode transform --source examples/sample.cbl --output transformed/sample.java")
        print("  Plan:        python main.py --mode plan --source project_dir --phase discovery --output transformation_plan.md")
        print("  Dependency:  python main.py --mode dependency --source project_dir --output dependency_map.json")
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
        # For planning mode, provide phase information
        if args.mode == 'plan' and not args.phase:
            print("Error: --phase parameter is required for planning mode.")
            print("Available phases: discovery, design, transform, test, deploy")
            return
            
        agent = create_agent(args.mode, config)
        
        # Add extra context for certain agent types
        if args.mode == 'plan':
            result = agent.process(args.source, args.output, phase=args.phase)
        elif args.mode == 'dependency':
            result = agent.process(args.source, args.output, project=args.project or "main")
        else:
            result = agent.process(args.source, args.output)
        
        print(f"Agent completed task. Result: {result}")
        
        # Provide next steps guidance
        if args.mode == 'analyze':
            print("\nNext steps:")
            print("  1. Review analysis output to understand application structure")
            print(f"  2. Generate documentation: python main.py --mode document --source {args.source} --output docs")
            print(f"  3. Create transformation plan: python main.py --mode plan --source {args.source} --phase design --output transformation_plan.md")
        elif args.mode == 'document':
            print("\nNext steps:")
            print("  1. Review generated documentation for completeness")
            print(f"  2. Identify dependencies: python main.py --mode dependency --source {args.source} --output dependencies.json")
            print(f"  3. Begin transformation: python main.py --mode transform --source {args.source} --output transformed/")
        
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
