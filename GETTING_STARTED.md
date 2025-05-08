# Getting Started with Agentic Mainframe Modernization POC

Follow these steps to set up and run the POC:

## 1. Setup Environment

### Install Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### Environment Configuration
The `.env` file already contains your OpenAI API key, so you're all set with credentials.

## 2. Running the Application

The application can be run in three different modes:

### Analyze Mode
Analyze mainframe code to identify key components and potential modernization challenges:

```bash
python main.py --mode analyze --source examples/sample.cbl --output analysis_results.json
```

### Document Mode
Generate comprehensive documentation from mainframe code:

```bash
python main.py --mode document --source examples/sample.cbl --output documentation/
```

### Transform Mode
Convert mainframe code to a modern language (e.g., Java):

```bash
python main.py --mode transform --source examples/sample.cbl --output transformed/sample.java
```

## 3. Example Workflow

Here's a complete workflow example:

```bash
# Step 1: Analyze the code
python main.py --mode analyze --source examples/sample.cbl --output analysis.json

# Step 2: Generate documentation
python main.py --mode document --source examples/sample.cbl --output docs

# Step 3: Transform the code
python main.py --mode transform --source examples/sample.cbl --output transformed/sample.java
```

## 4. Extending the POC

To add your own COBOL files for processing:

1. Place your .cbl or .cob files in the examples directory
2. Run the commands above, replacing "sample.cbl" with your filename

## 5. Troubleshooting

Common issues:

- **API Key Issues**: Ensure your OpenAI API key in `.env` is correct and has sufficient credits
- **File Not Found**: Make sure the path to your source files is correct
- **Module Not Found**: Check that you've installed all dependencies with `pip install -r requirements.txt`
