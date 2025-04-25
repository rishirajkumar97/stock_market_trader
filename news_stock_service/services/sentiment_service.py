import google.generativeai as genai
import os
from typing import List, Tuple, Dict, Any, Optional
import asyncio
import json

class SentimentAnalyzer:
    """Sentiment Analyzer using Google's Gemini API"""

    def __init__(self, api_key: Optional[str] = "AIzaSyAzod_JHzYcBBrXeAMZ6dHg7r8QHcpzAgQ"):
        """Initialize the Gemini API client
        
        Args:
            api_key: Gemini API key, if None will try to get from environment variable
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it to the constructor.")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Get the model
        self.model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
        
        # Set up the prompt template
        self.prompt_template = """
        Assume you are a Financial Analyst, analysing the news for stock market indicators.
        I want you to analyze the sentiment of the following news text excerpt. The text data is scraped from the web.
        Please clean the data with step by step thinking and take only the news info related to the financial stock market of London. If the cleaned data is not related then give it a neutral score.
        Return a sentiment classification as "Positive", "Neutral", or "Negative".
        The text may contain HTML tags or irrelevant information - please focus on the main content.
        
        Respond with a JSON object only with the following format:
        {{"sentiment": "Positive/Neutral/Negative", "score": 0.X}}
        
        Where score is a number between -1 and 1, representing the confidence or intensity of the sentiment.
        - For Positive sentiment: score closer to 1 means strongly positive
        - For Neutral sentiment: score closer to 0 means strongly neutral
        - For Negative sentiment: score closer to -1 means strongly negative
        
        Here's the text to analyze:
        
        {text}
        """

    async def _analyze_single_text_async(self, text: str) -> Dict[str, Any]:
        """Analyze a single text using Gemini API asynchronously"""
        prompt = self.prompt_template.format(text=text)
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            response_text = response.text
            try:
                # Parse the JSON response
                result = json.loads(response_text)
                # Validate the response format
                if "sentiment" not in result or "score" not in result:
                    raise ValueError("Invalid response format from Gemini API")
                
                return result
            except json.JSONDecodeError:
                # If response is not valid JSON, try to extract JSON from the text
                import re
                json_match = re.search(r'{.*}', response_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                        if "sentiment" not in result or "score" not in result:
                            raise ValueError("Invalid response format from Gemini API")
                        return result
                    except json.JSONDecodeError:
                        pass
                
                # If all else fails, make a best effort interpretation
                sentiment = "Neutral"
                score = 0
                if "positive" in response_text.lower():
                    sentiment = "Positive"
                    score = 0.75
                elif "negative" in response_text.lower():
                    sentiment = "Negative"
                    score = -0.5
                
                return {"sentiment": sentiment, "score": score}
                
        except Exception as e:
            # Handle API errors
            print(f"Error analyzing text with Gemini API: {str(e)}")
            # Return neutral as default for errors
            return {"sentiment": "Neutral", "score": 0.5}

    async def analyze_sentiment_async(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Batch process sentiment analysis using Gemini API asynchronously"""
        if not texts:
            return []
        
        # Process texts concurrently
        tasks = [self._analyze_single_text_async(text) for text in texts]
        results = await asyncio.gather(*tasks)
        
        return results
    
    def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Synchronous wrapper for sentiment analysis"""
        return asyncio.run(self.analyze_sentiment_async(texts))

# Singleton instance for efficiency
sentiment_analyzer = SentimentAnalyzer()