from agents.base_agent import BaseAgent
import os
import markdown

class DocumentationAgent(BaseAgent):
    """Agent for generating documentation from mainframe code"""
    
    def __init__(self, config):
        super().__init__(config)
        agent_config = config["agents"].get("document", {})
        self.prompt_template = self._load_prompt_template(
            agent_config.get("prompt_template", "document_template.txt")
        )
    
    def process(self, source, output=None):
        """Generate documentation from mainframe code"""
        if not os.path.exists(source):
            return {"error": f"Source file or directory not found: {source}"}
        
        code_files = self._gather_files(source)
        
        if not output:
            output = os.path.join(os.path.dirname(source), "documentation")
        
        os.makedirs(output, exist_ok=True)
        
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
            
            # Get documentation from LLM
            documentation_md = self.llm.generate(prompt)
            
            # Save documentation as markdown
            rel_path = os.path.relpath(file_path, start=os.path.dirname(source))
            doc_filename = os.path.join(output, f"{rel_path}.md")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(doc_filename), exist_ok=True)
            
            with open(doc_filename, 'w') as f:
                f.write(documentation_md)
            
            # Also generate HTML for easier viewing
            html_filename = os.path.join(output, f"{rel_path}.html")
            html_content = markdown.markdown(documentation_md)
            with open(html_filename, 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Documentation for {os.path.basename(file_path)}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
                        h1 {{ color: #333; }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """)
        
        return {
            "status": "success",
            "files_documented": len(code_files),
            "output_directory": output
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
