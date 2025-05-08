from agents.base_agent import BaseAgent
import os
import json
import yaml
import markdown

class PlanningAgent(BaseAgent):
    """Agent for creating modernization plans for different phases"""
    
    def __init__(self, config):
        super().__init__(config)
        agent_config = config["agents"].get("plan", {})
        self.prompt_template = self._load_prompt_template(
            agent_config.get("prompt_template", "plan_template.txt")
        )
    
    def process(self, source, output=None, **kwargs):
        """Generate a modernization plan for the specified phase"""
        if not os.path.exists(source):
            return {"error": f"Source file or directory not found: {source}"}
        
        phase = kwargs.get('phase', 'discovery')
        
        # Analyze the codebase to understand what we're planning for
        code_files = self._gather_files(source)
        code_samples = self._extract_code_samples(code_files)
        
        # Get analysis information if available
        analysis_data = self._get_analysis_data(source)
        
        # Get relevant context from the knowledge base
        context_query = f"mainframe modernization {phase} phase planning"
        context = self.retriever.get_relevant_context(context_query)
        
        # Prepare prompt with the code samples, analysis and context
        prompt = self.prompt_template.format(
            code_samples=code_samples,
            analysis=analysis_data,
            context=context,
            phase=phase,
            source_path=source
        )
        
        # Generate plan from LLM
        plan_markdown = self.llm.generate(prompt)
        
        # Save plan if output is specified
        if output:
            # Save as markdown
            with open(output, 'w') as f:
                f.write(plan_markdown)
                
            # If output is .md, also generate HTML version
            if output.endswith('.md'):
                html_output = output[:-3] + '.html'
                html_content = markdown.markdown(plan_markdown)
                with open(html_output, 'w') as f:
                    f.write(f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Modernization Plan - {phase.capitalize()} Phase</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                            pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
                            h1 {{ color: #333; }}
                            .phase {{ color: #0066cc; font-weight: bold; }}
                            .task {{ margin-bottom: 20px; border-left: 3px solid #ccc; padding-left: 15px; }}
                            .priority-high {{ border-color: #ff6b6b; }}
                            .priority-medium {{ border-color: #feca57; }}
                            .priority-low {{ border-color: #1dd1a1; }}
                        </style>
                    </head>
                    <body>
                        {html_content}
                    </body>
                    </html>
                    """)
        
        return {
            "status": "success",
            "phase": phase,
            "files_analyzed": len(code_files),
            "plan_output": output if output else "Plan not saved to file"
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
    
    def _extract_code_samples(self, files, max_files=3, max_lines=50):
        """Extract representative code samples from the files"""
        samples = []
        
        for file in files[:max_files]:
            with open(file, 'r') as f:
                content = f.readlines()
                
            # Get a representative sample (beginning of the file)
            sample = ''.join(content[:max_lines])
            if len(content) > max_lines:
                sample += f"\n... (file continues with {len(content) - max_lines} more lines) ..."
                
            samples.append({
                "file": os.path.basename(file),
                "sample": sample
            })
        
        if len(files) > max_files:
            samples.append({
                "file": "summary",
                "sample": f"... and {len(files) - max_files} more files not shown here."
            })
            
        return samples
    
    def _get_analysis_data(self, source):
        """Look for existing analysis data for this source"""
        potential_paths = [
            os.path.join(os.path.dirname(source), "analysis.json"),
            source + ".analysis.json",
            "analysis.json"
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        return json.load(f)
                except:
                    pass
        
        return "No existing analysis data found."
