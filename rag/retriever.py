import os
import json

class Retriever:
    """Retriever component for RAG system"""
    
    def __init__(self, config):
        self.db_type = config.get("type", "mock")
        self.db_path = config.get("path", "./vector_store")
        
        # For the POC, we'll use a simple mock knowledge base
        self.knowledge_base = self._load_mock_knowledge_base()
    
    def get_relevant_context(self, query, top_k=3):
        """
        Get relevant context for a query
        
        In a real implementation, this would query a vector database
        For the POC, we'll use simple keyword matching
        """
        if self.db_type == "mock":
            return self._mock_retrieval(query, top_k)
        else:
            # In a real implementation, this would use the actual vector DB
            print("Warning: Using mock retrieval since real vector DB not implemented")
            return self._mock_retrieval(query, top_k)
    
    def _mock_retrieval(self, query, top_k=3):
        """Simple mock retrieval using keyword matching"""
        query = query.lower()
        
        # Count keyword occurrences in knowledge entries
        scored_entries = []
        for entry in self.knowledge_base:
            score = 0
            content = entry["content"].lower()
            
            # Look for keywords from query in the content
            for word in query.split():
                if len(word) > 3 and word in content:  # Only consider words longer than 3 chars
                    score += 1
            
            # Also check for technical terms specific to mainframes
            mainframe_terms = ["cobol", "jcl", "cics", "vsam", "db2", "ims", "mvs", 
                             "transaction", "copybook", "mainframe", "zos"]
            for term in mainframe_terms:
                if term in content and term in query:
                    score += 3  # Give higher weight to technical terms
            
            if score > 0:
                scored_entries.append((score, entry))
        
        # Sort by score and take top_k
        scored_entries.sort(reverse=True, key=lambda x: x[0])
        
        # Extract just the content from the top entries
        results = [entry["content"] for _, entry in scored_entries[:top_k]]
        
        # Combine results into a single context string
        if results:
            return "\n\n---\n\n".join(results)
        else:
            return "No relevant context found."
    
    def _load_mock_knowledge_base(self):
        """Load a simple mock knowledge base for the POC"""
        # In a real implementation, this would be a vector database
        mock_kb_file = os.path.join(os.path.dirname(__file__), "mock_knowledge_base.json")
        
        try:
            with open(mock_kb_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create a basic knowledge base if file doesn't exist
            print("Creating mock knowledge base...")
            kb = [
                {
                    "id": "cobol-basics",
                    "content": """
COBOL (Common Business-Oriented Language) is a compiled English-like computer programming language designed for business use. It is imperative, procedural and, since 2002, object-oriented. COBOL is primarily used in business, finance, and administrative systems for companies and governments.

Key features of COBOL include:
- Division structure (IDENTIFICATION, ENVIRONMENT, DATA, PROCEDURE)
- Verbose English-like syntax
- Record-oriented file handling
- Strong data typing and specification
- Support for decimal arithmetic
                    """
                },
                {
                    "id": "mainframe-architecture",
                    "content": """
Mainframe computers or mainframes are computers used primarily by large organizations for critical applications, bulk data processing, enterprise resource planning, and transaction processing. They are larger and have more processing power than some other classes of computers.

IBM mainframes run z/OS, z/VM, z/VSE, z/TPF operating systems. Key components include:
- CICS - Customer Information Control System for transaction management
- IMS - Information Management System database
- DB2 - Relational database management system
- JCL - Job Control Language for batch processing
- TSO - Time Sharing Option for interactive computing
                    """
                },
                {
                    "id": "cobol-to-java",
                    "content": """
Converting COBOL programs to Java requires understanding several key mapping patterns:

1. COBOL divisions map to Java package and class structures
2. COBOL data items map to Java variables:
   - PIC X fields → String
   - PIC 9 fields → int, long, BigDecimal
   - GROUP items → Classes
3. COBOL paragraphs map to Java methods
4. COBOL PERFORM maps to method calls
5. COBOL file handling maps to Java I/O streams
6. COBOL string handling needs careful conversion
7. COBOL numeric operations must consider precision differences

Common challenges include handling COBOL's decimal arithmetic, managing EBCDIC vs ASCII encoding, and dealing with lack of pointers in COBOL.
                    """
                },
                {
                    "id": "jcl-basics",
                    "content": """
JCL (Job Control Language) is used to instruct the z/OS operating system on how to run batch jobs. It's a scripting language that defines the resources needed and the processing to be done.

Key components of JCL:
- JOB statement - Marks the beginning of a job and provides accounting information
- EXEC statement - Identifies the program or procedure to be executed
- DD statement - Defines datasets used by the program
- PROC - Defines a procedure that can be reused
- SET - Assigns values to symbolic parameters
- IF/THEN/ELSE - Provides conditional processing
- INCLUDE - Incorporates predefined JCL statements

JCL is often modernized to shell scripts, Jenkins pipelines, or other workflow automation tools.
                    """
                },
                {
                    "id": "vsam-basics",
                    "content": """
VSAM (Virtual Storage Access Method) is a file storage access method used in IBM mainframe operating systems. It provides high-performance access to data on direct access storage devices.

VSAM record types:
- KSDS (Key Sequenced Data Set) - Records are accessed by a key field
- ESDS (Entry Sequenced Data Set) - Records are accessed by their relative position
- RRDS (Relative Record Data Set) - Records are accessed by relative record number
- LDS (Linear Data Set) - Byte-addressable space with no record structure

In modern systems, VSAM is typically replaced by relational databases, object storage, or NoSQL databases, depending on the access patterns required.
                    """
                }
            ]
            
            # Save the mock knowledge base
            os.makedirs(os.path.dirname(mock_kb_file), exist_ok=True)
            with open(mock_kb_file, 'w') as f:
                json.dump(kb, f, indent=2)
            
            return kb
