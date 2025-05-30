# Agentic Mainframe Modernization POC

This proof of concept demonstrates how AI agents can assist in mainframe modernization efforts through:

1. **Code Analysis** - Understanding and documenting legacy mainframe code
2. **Documentation Generation** - Creating comprehensive documentation from code analysis
3. **Code Transformation** - Converting mainframe code to modern alternatives
4. **Dependency Analysis** - Identifying technical and resource dependencies
5. **Modernization Planning** - Creating detailed plans for each modernization phase

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY=your-api-key
   ```
   Or add it to `config.yaml`

## Usage

The POC provides five main capabilities:

### 1. Analyze Mainframe Code

```bash
python main.py --mode analyze --source /path/to/cobol/file.cbl --output analysis_report.json
```

This will generate an analysis report of the mainframe code, identifying key components, dependencies, and modernization considerations.

### 2. Generate Documentation

```bash
python main.py --mode document --source /path/to/cobol/file.cbl --output documentation
```

This will generate comprehensive documentation in Markdown and HTML formats, explaining the purpose and functionality of the code.

### 3. Transform Code

```bash
python main.py --mode transform --source /path/to/cobol/file.cbl --output /path/to/output/file.java
```

This will transform the mainframe code to a modern language (default: Java), applying transformation rules and preserving business logic.

### 4. Identify Dependencies

```bash
python main.py --mode dependency --source /path/to/cobol/file.cbl --output dependencies.json
```

This will analyze the code to identify technical dependencies (copybooks, programs, databases) and required resources (expertise, tools), generating both JSON data and a visual dependency graph.

### 5. Create Modernization Plans

```bash
python main.py --mode plan --source /path/to/cobol/file.cbl --phase discovery --output plan.md
```

This will create a detailed plan for the specified modernization phase (discovery, design, transform, test, deploy), outlining activities, resources, and deliverables.

## Example

To try with the included example COBOL file:

```bash
# Analyze
python main.py --mode analyze --source examples/sample.cbl --output analysis.json

# Document
python main.py --mode document --source examples/sample.cbl --output docs

# Identify Dependencies
python main.py --mode dependency --source examples/sample.cbl --output dependencies.json

# Create Modernization Plan (Discovery Phase)
python main.py --mode plan --source examples/sample.cbl --phase discovery --output discovery_plan.md

# Transform
python main.py --mode transform --source examples/sample.cbl --output transformed/sample.java
```

## Architecture

The POC uses a modular architecture with:

- Specialized agents for different modernization tasks
- RAG (Retrieval-Augmented Generation) for relevant context
- Configurable LLM backends
- Transformation rules for common patterns
- Dependency analysis with visual graph generation
- Phase-based modernization planning

## Extending the POC

To extend this POC for production use, consider:

1. Implementing a proper vector database for RAG
2. Adding more specialized agents for different mainframe technologies
3. Expanding the transformation rules for different target languages
4. Adding integration with CI/CD pipelines
5. Implementing feedback loops to improve agent performance
