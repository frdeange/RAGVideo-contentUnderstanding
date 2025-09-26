"""
Azure OpenAI client using the official OpenAI library.
Handles embeddings and chat completions with Azure OpenAI services.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
from datetime import datetime, timezone


class AzureOpenAIClient:
    """Client for Azure OpenAI services using official OpenAI library."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.chat_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        self.embedding_deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
        self.api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        
        # Setup authentication and client
        self._setup_client()
    
    def _setup_client(self):
        """Set up Azure OpenAI client with proper authentication."""
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not configured")
        
        try:
            if self.api_key:
                # Use API key authentication
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version="2024-08-01-preview"
                )
                logging.info("Azure OpenAI client configured with API key")
            else:
                # Use managed identity authentication  
                credential = DefaultAzureCredential()
                token_provider = get_bearer_token_provider(
                    credential, 
                    "https://cognitiveservices.azure.com/.default"
                )
                
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    azure_ad_token_provider=token_provider,
                    api_version="2024-08-01-preview"
                )
                logging.info("Azure OpenAI client configured with managed identity")
                
        except Exception as e:
            logging.error(f"Failed to setup Azure OpenAI client: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str], deployment_name: Optional[str] = None) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            deployment_name: Optional deployment name override
            
        Returns:
            List of embedding vectors
        """
        deployment = deployment_name or self.embedding_deployment
        if not deployment:
            raise ValueError("Embedding deployment name not configured")
        
        try:
            embeddings = []
            
            # Process texts in batches to respect rate limits
            batch_size = 16
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = self.client.embeddings.create(
                    model=deployment,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                logging.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            return embeddings
            
        except Exception as e:
            logging.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_single_embedding(self, text: str, deployment_name: Optional[str] = None) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            deployment_name: Optional deployment name override
            
        Returns:
            Embedding vector
        """
        embeddings = self.generate_embeddings([text], deployment_name)
        return embeddings[0] if embeddings else []
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        deployment_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate chat completion using Azure OpenAI.
        
        Args:
            messages: List of chat messages
            deployment_name: Optional deployment name override
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        deployment = deployment_name or self.chat_deployment
        if not deployment:
            raise ValueError("Chat deployment name not configured")
        
        try:
            response = self.client.chat.completions.create(
                model=deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error generating chat completion: {e}")
            raise
    
    def generate_video_insights(
        self, 
        video_context: Dict[str, Any], 
        deployment_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights for video content.
        
        Args:
            video_context: Context information about the video
            deployment_name: Optional deployment name override
            
        Returns:
            Structured insights dictionary
        """
        # Create structured prompt for video analysis in English
        system_message = """You are an expert video content analyst. Your task is to generate useful and actionable insights 
        based on automatic video analysis. Provide a structured analysis that includes:

        1. Executive summary of the content
        2. Key points and takeaways
        3. Target audience analysis
        4. Expected engagement metrics
        5. Optimization recommendations
        6. Search keywords

        Respond in valid JSON format with the specified structure."""
        
        user_message = f"""Analyze this video and provide detailed insights:

        Video Information:
        - Name: {video_context.get('video_name', 'N/A')}
        - Duration: {video_context.get('duration_minutes', 0)} minutes
        - Size: {video_context.get('file_size_mb', 0)} MB
        - Language: {video_context.get('language', 'N/A')}

        Transcript:
        {video_context.get('transcript', 'Not available')[:2000]}...

        Main Topics:
        {', '.join(video_context.get('topics', []))}

        Detected Labels:
        {', '.join(video_context.get('labels', []))}

        Additional Information:
        - Scenes: {video_context.get('scenes_count', 0)}
        - Faces detected: {video_context.get('faces_detected', 0)}
        - Keyframes: {video_context.get('keyframes_count', 0)}
        """
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.chat_completion(messages, deployment_name, temperature=0.3, max_tokens=2000)
            
            # Try to parse as JSON, fallback to structured text if needed
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "raw_response": response,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "status": "completed_with_fallback"
                }
        
        except Exception as e:
            logging.error(f"Error generating video insights: {e}")
            raise


# Global instance for reuse
_openai_client_instance = None

def get_openai_client() -> AzureOpenAIClient:
    """Get a singleton instance of the Azure OpenAI client."""
    global _openai_client_instance
    if _openai_client_instance is None:
        _openai_client_instance = AzureOpenAIClient()
    return _openai_client_instance