from agents.analyzer_agent import AnalyzerAgent
from agents.documentation_agent import DocumentationAgent
from agents.transformation_agent import TransformationAgent

def create_agent(agent_type, config):
    """
    Factory function to create the appropriate agent based on type
    """
    if agent_type == 'analyze':
        return AnalyzerAgent(config)
    elif agent_type == 'document':
        return DocumentationAgent(config)
    elif agent_type == 'transform':
        return TransformationAgent(config)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
