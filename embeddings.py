import torch
from transformers import DistilBertTokenizer, DistilBertModel

class EmbeddingGenerator:
    def __init__(self, model_name="distilbert-base-uncased", max_length=512):
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_name)
        self.model = DistilBertModel.from_pretrained(model_name)
        self.max_length = max_length
        
        # Use CUDA if available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = self.model.to(self.device)
        
    def generate(self, text):
        """Generate embeddings for text using DistilBERT."""
        # Tokenize text
        encoded_input = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        # Move inputs to device
        encoded_input = {key: val.to(self.device) for key, val in encoded_input.items()}
        
        # Generate embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        
        # Use the [CLS] token embedding as the document embedding
        embedding = model_output.last_hidden_state[:, 0, :].cpu().numpy()[0]
        
        return embedding
    
    def __call__(self, texts):
        """Make the class callable for compatibility with Chroma."""
        return [self.generate(text) for text in texts]
