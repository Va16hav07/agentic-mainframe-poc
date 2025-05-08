from agents.base_agent import BaseAgent
import os
import yaml
import re

class TransformationAgent(BaseAgent):
    """Agent for transforming mainframe code to modern alternatives"""
    
    def __init__(self, config):
        super().__init__(config)
        agent_config = config["agents"].get("transform", {})
        self.prompt_template = self._load_prompt_template(
            agent_config.get("prompt_template", "transform_template.txt")
        )
        self.rules_file = agent_config.get("rules_file", "transformation_rules.yaml")
        self.transformation_rules = self._load_transformation_rules()
    
    def process(self, source, output=None):
        """Transform mainframe code to modern alternatives"""
        if not os.path.exists(source):
            return {"error": f"Source file or directory not found: {source}"}
        
        # If output is not specified, create a directory next to source
        if not output:
            if os.path.isfile(source):
                output = f"{source}.transformed"
            else:
                output = f"{source}_transformed"
        
        # If source is a directory, create output directory
        if os.path.isdir(source):
            os.makedirs(output, exist_ok=True)
            transformed_files = self._transform_directory(source, output)
        else:
            # Transform a single file
            transformed_files = [self._transform_file(source, output)]
        
        return {
            "status": "success",
            "files_transformed": len(transformed_files),
            "transformed_files": transformed_files
        }
    
    def _transform_file(self, source_file, output_file):
        """Transform a single file"""
        # Read the source file
        with open(source_file, 'r') as f:
            code = f.read()
        
        # Apply simple rule-based transformations first
        for rule in self.transformation_rules.get("simple_rules", []):
            pattern = rule["pattern"]
            replacement = rule["replacement"]
            code = re.sub(pattern, replacement, code)
        
        # Get relevant context from the knowledge base
        context = self.retriever.get_relevant_context(code)
        
        # Prepare prompt with the code and context
        prompt = self.prompt_template.format(
            code=code,
            context=context,
            target_language=self.transformation_rules.get("target_language", "Java")
        )
        
        # Get transformed code from LLM
        transformed_code = self.llm.generate(prompt)
        
        # Write the transformed code to the output file
        with open(output_file, 'w') as f:
            f.write(transformed_code)
        
        return {
            "source": source_file,
            "output": output_file
        }
    
    def _transform_directory(self, source_dir, output_dir):
        """Transform all relevant files in a directory"""
        transformed_files = []
        
        # Get the file extension mappings from rules
        extension_map = self.transformation_rules.get("extension_map", {})
        
        for root, _, files in os.walk(source_dir):
            for file in files:
                # Check if this is a file we should transform
                _, ext = os.path.splitext(file)
                if ext.lower() not in extension_map:
                    continue
                
                # Determine the output file path and extension
                rel_path = os.path.relpath(os.path.join(root, file), source_dir)
                new_ext = extension_map.get(ext.lower(), ext)
                output_file = os.path.join(
                    output_dir,
                    os.path.splitext(rel_path)[0] + new_ext
                )
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
                # Transform the file
                result = self._transform_file(os.path.join(root, file), output_file)
                transformed_files.append(result)
        
        return transformed_files
    
    def _load_transformation_rules(self):
        """Load transformation rules from YAML file"""
        try:
            with open(self.rules_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Transformation rules file {self.rules_file} not found. Using default rules.")
            return {
                "target_language": "Java",
                "extension_map": {
                    ".cbl": ".java",
                    ".cob": ".java",
                    ".jcl": ".sh",
                    ".pli": ".java"
                },
                "simple_rules": [
                    {
                        "pattern": r"PERFORM\s+(\w+)",
                        "replacement": r"// TRANSFORMED: Call \1()"
                    },
                    {
                        "pattern": r"MOVE\s+(\w+)\s+TO\s+(\w+)",
                        "replacement": r"// TRANSFORMED: \2 = \1"
                    }
                ]
            }
