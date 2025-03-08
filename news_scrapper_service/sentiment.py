import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

class SentimentAnalyzer:
    """Optimized FinBERT Sentiment Analyzer for Batch Processing"""

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        self.model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
        self.model.to(self.device)
        self.model.eval()  # Set model to evaluation mode

    def analyze_sentiment(self, texts):
        """Batch process sentiment analysis efficiently"""
        if not texts:
            return []

        # Tokenize texts efficiently (batching improves speed)
        inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probabilities = F.softmax(logits, dim=-1)

        labels = ["Negative", "Neutral", "Positive"]
        results = [
            (probabilities[i].tolist(), labels[probabilities[i].argmax().item()])
            for i in range(len(texts))
        ]

        return results

# Singleton instance for efficiency
sentiment_analyzer = SentimentAnalyzer()