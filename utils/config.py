import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config(config_file):
    """
    Load configuration from YAML file
    """
    if not os.path.exists(config_file):
        print(f"Configuration file {config_file} not found. Using default configuration.")
        return default_config()
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Start with default config to ensure all fields are present
    default = default_config()
    
    # Update with values from config file
    if "llm" in config:
        default["llm"].update(config.get("llm", {}))
    if "vector_db" in config:
        default["vector_db"].update(config.get("vector_db", {}))
    if "agents" in config:
        for agent_type, agent_config in config.get("agents", {}).items():
            if agent_type in default["agents"]:
                default["agents"][agent_type].update(agent_config)
    
    # Ensure API key from .env overrides the one in config file
    env_api_key = os.environ.get("OPENAI_API_KEY")
    if env_api_key:
        default["llm"]["api_key"] = env_api_key
        print("Using API key from environment variables.")
    
    return default

def default_config():
    """
    Default configuration if no config file is provided
    """
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        print("Using API key from environment variables (free tier)")
        # For free tier, use appropriate model and conservative settings
        model = "gpt-3.5-turbo"
        # Lower temperature for more deterministic outputs
        temperature = 0.1
        # Add rate limiting for free tier
        rate_limit = True
    else:
        print("Warning: No OpenAI API key found in environment variables.")
        model = "gpt-3.5-turbo"
        temperature = 0.1
        rate_limit = False
    
    return {
        "llm": {
            "provider": "openai",
            "model": model,
            "api_key": api_key,
            "temperature": temperature,
            "rate_limit": rate_limit,
            "max_tokens": 1000,  
            "retry_attempts": 3,  
            "retry_delay": 5      
        },
        "vector_db": {
            "type": "chroma",
            "path": "./vector_store"
        },
        "agents": {
            "analyze": {
                "prompt_template": "analyze_template.txt",
                "model": "gpt-3.5-turbo",
            },
            "document": {
                "prompt_template": "document_template.txt",
                "model": "gpt-3.5-turbo",
            },
            "transform": {
                "prompt_template": "transform_template.txt",
                "model": "gpt-3.5-turbo",
                "rules_file": "transformation_rules.yaml"
            }
        }
    }
