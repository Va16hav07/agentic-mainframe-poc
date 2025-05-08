from abc import ABC, abstractmethod
from llm.llm_service import LLMService
from rag.retriever import Retriever

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, config):
        self.config = config
        self.llm = LLMService(config["llm"])
        self.retriever = Retriever(config["vector_db"])
        
    @abstractmethod
    def process(self, source, output=None):
        """
        Process the input source and generate output
        
        Args:
            source: Source file or directory to process
            output: Optional output location
            
        Returns:
            Result of the processing
        """
        pass
    
    def _load_prompt_template(self, template_name):
        """Load a prompt template from file"""
        template_path = f"prompts/{template_name}"
        try:
            with open(template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt template {template_path} not found. Using default.")
            return "Analyze the following code: {code}"
