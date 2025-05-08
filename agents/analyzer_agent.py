from agents.base_agent import BaseAgent
import os
import json

class AnalyzerAgent(BaseAgent):
    """Agent for analyzing mainframe code and applications"""
    
    def __init__(self, config):
        super().__init__(config)
        agent_config = config["agents"].get("analyze", {})
        self.prompt_template = self._load_prompt_template(
            agent_config.get("prompt_template", "analyze_template.txt")
        )
    
    def process(self, source, output=None):
        """Analyze mainframe code and produce an analysis report"""
        if not os.path.exists(source):
            return {"error": f"Source file or directory not found: {source}"}
        
        code_files = self._gather_files(source)
        analysis_results = []
        
        for file_path in code_files:
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Get relevant context from the knowledge base
            context = self.retriever.get_relevant_context(code)
            
            # Prepare prompt with the code and context
            prompt = self.prompt_template.format(
                code=code,
                context=context
            )
            
            # Get analysis from LLM
            analysis = self.llm.generate(prompt)
            
            analysis_results.append({
                "file": file_path,
                "analysis": analysis
            })
        
        # Save results if output is specified
        if output:
            with open(output, 'w') as f:
                json.dump(analysis_results, f, indent=2)
        
        return {
            "status": "success",
            "files_analyzed": len(analysis_results),
            "output": output if output else "Results not saved to file"
        }
    
    def _gather_files(self, source):
        """Gather all relevant files from the source path"""
        if os.path.isfile(source):
            return [source]
        
        relevant_extensions = ['.cbl', '.cob', '.jcl', '.asm', '.pli', '.cobol']
        result = []
        
        for root, _, files in os.walk(source):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in relevant_extensions:
                    result.append(os.path.join(root, file))
        
        return result
