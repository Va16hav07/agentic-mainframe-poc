import numpy as np
import logging
import torch
from transformers import AutoTokenizer, AutoModel

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    A document embedding generator using Hugging Face transformer models.
    Supports both full model embedding and fallback to simpler approaches.
    """
    def __init__(self, model_name="distilbert-base-uncased", embedding_dim=768, use_model=True):
        logger.info(f"Initializing EmbeddingGenerator with model: {model_name}")
        self.embedding_dim = embedding_dim
        self.use_model = use_model
        
        # Initialize tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            logger.info(f"Tokenizer loaded: {model_name}")
            
            # Only load the model if we're using it
            if use_model:
                self.model = AutoModel.from_pretrained(model_name)
                # Use CPU for compatibility
                self.device = 'cpu'
                self.model = self.model.to(self.device)
                logger.info(f"Model loaded and moved to {self.device}")
            else:
                self.model = None
                logger.info("Using simplified embedding (no model)")
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            # Fall back to simplified approach
            self.use_model = False
            self.model = None
            
            # Try to initialize just the tokenizer for fallback mode
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            except:
                # If even tokenizer fails, we'll use basic text splitting
                self.tokenizer = None
    
    def _tokenize_text(self, text):
        """Tokenize text using the loaded tokenizer or fallback to simple splitting."""
        if self.tokenizer:
            return self.tokenizer.tokenize(text)
        else:
            # Simple fallback tokenization
            return text.split()
    
    def generate_with_model(self, text):
        """Generate embeddings using the transformer model."""
        try:
            # Tokenize and prepare input
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            ).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Use CLS token (first token) as the sentence embedding
            embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]
            
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error generating embedding with model: {str(e)}")
            return self.generate_simple(text)
    
    def generate_simple(self, text):
        """Generate embeddings using a simple hashing approach."""
        logger.info("Using simplified embedding generation")
        
        if not isinstance(text, str) or not text.strip():
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        try:
            # Simple tokenization
            tokens = self._tokenize_text(text[:10000])
            
            # Initialize embedding vector
            embedding = np.zeros(self.embedding_dim, dtype=np.float32)
            
            # Create embedding based on token positions
            for i, token in enumerate(tokens[:1000]):  # Limit to 1000 tokens
                # Hash the token to determine positions
                hash_val = hash(token) % self.embedding_dim
                # Add a value at that position (with diminishing weight)
                embedding[hash_val] += 1.0 / (i + 1)
            
            # Normalize the embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding
        except Exception as e:
            logger.error(f"Error in simple embedding: {str(e)}")
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def generate(self, text):
        """Generate embeddings for text using the best available method."""
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
            
        if not text.strip():
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        # Truncate text to a reasonable length
        text = text[:50000]
        
        if self.use_model and self.model:
            return self.generate_with_model(text)
        else:
            return self.generate_simple(text)
    
    def __call__(self, texts):
        """Process a batch of texts."""
        logger.info(f"Processing batch of {len(texts) if texts else 0} texts")
        
        if not texts:
            return [np.zeros(self.embedding_dim, dtype=np.float32)]
        
        # Process each text
        result = []
        for text in texts:
            try:
                if not isinstance(text, str):
                    text = str(text) if text is not None else ""
                embedding = self.generate(text)
                result.append(embedding)
            except Exception as e:
                logger.error(f"Error processing text: {str(e)}")
                result.append(np.zeros(self.embedding_dim, dtype=np.float32))
        
        return result
