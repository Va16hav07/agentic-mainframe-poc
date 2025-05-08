from agents.base_agent import BaseAgent
import os
import json
import re
import networkx as nx
import matplotlib.pyplot as plt

class DependencyAgent(BaseAgent):
    """Agent for identifying technical and resource dependencies"""
    
    def __init__(self, config):
        super().__init__(config)
        agent_config = config["agents"].get("dependency", {})
        self.prompt_template = self._load_prompt_template(
            agent_config.get("prompt_template", "dependency_template.txt")
        )
    
    def process(self, source, output=None, **kwargs):
        """Analyze dependencies in mainframe code"""
        if not os.path.exists(source):
            return {"error": f"Source file or directory not found: {source}"}
        
        project = kwargs.get('project', 'main')
        
        # Gather all relevant files
        code_files = self._gather_files(source)
        
        # Extract initial dependencies through static analysis
        static_dependencies = self._extract_static_dependencies(code_files)
        
        # Process each file to find dependencies
        all_dependencies = []
        processed_files = 0
        
        for file_path in code_files:
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Get relevant context from the knowledge base
            context = self.retriever.get_relevant_context(code)
            
            # Add static analysis insights
            file_deps = static_dependencies.get(file_path, [])
            static_deps_str = "\n".join([f"- {d['type']}: {d['name']}" for d in file_deps])
            
            # Prepare prompt with the code and context
            prompt = self.prompt_template.format(
                code=code,
                context=context,
                static_dependencies=static_deps_str,
                file_path=file_path
            )
            
            # Get dependency analysis from LLM
            dependency_analysis = self.llm.generate(prompt)
            
            # Parse the dependency analysis
            try:
                # The LLM should return JSON, but sometimes it might include markdown
                # Try to extract JSON from the response
                json_match = re.search(r'```json\n(.*?)\n```', dependency_analysis, re.DOTALL)
                if json_match:
                    dependency_data = json.loads(json_match.group(1))
                else:
                    dependency_data = json.loads(dependency_analysis)
                
                all_dependencies.append({
                    "file": file_path,
                    "dependencies": dependency_data
                })
            except json.JSONDecodeError as e:
                return {"error": f"Failed to parse JSON: {str(e)}"}
            
            processed_files += 1
        
        return {
            "project": project,
            "processed_files": processed_files,
            "dependencies": all_dependencies
        }