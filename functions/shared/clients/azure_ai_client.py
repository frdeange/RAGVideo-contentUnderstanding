"""
Azure Content Understanding client wrapper.
Uses a local implementation of the Content Understanding client.
"""

import os
import logging
from typing import Dict, Any, Optional
from .content_understanding_client import AzureContentUnderstandingClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import uuid
import json
from datetime import datetime, timezone


class ContentUnderstandingClient:
    """Wrapper for Azure Content Understanding services using official Microsoft client."""
    
    def __init__(self):
        """Initialize the Content Understanding client."""
        self.endpoint = os.environ.get("AZURE_AI_SERVICE_ENDPOINT")
        self.api_version = os.environ.get("AZURE_AI_SERVICE_API_VERSION", "2024-12-01-preview")
        
        # Set up authentication
        self._setup_authentication()
        
        # Initialize the official client
        self._setup_client()
    
    def _setup_authentication(self):
        """Set up Azure authentication."""
        try:
            self.credential = DefaultAzureCredential()
            self.token_provider = get_bearer_token_provider(
                self.credential, 
                "https://cognitiveservices.azure.com/.default"
            )
            logging.info("Azure Content Understanding authentication configured")
        except Exception as e:
            logging.error(f"Failed to set up authentication: {e}")
            raise
    
    def _setup_client(self):
        """Initialize the official Azure Content Understanding client."""
        if not self.endpoint:
            raise ValueError("AZURE_AI_SERVICE_ENDPOINT not configured")
        
        try:
            self.client = AzureContentUnderstandingClient(
                endpoint=self.endpoint,
                api_version=self.api_version,
                token_provider=self.token_provider,
                x_ms_useragent="RAGVideo/1.0"
            )
            logging.info("Azure Content Understanding client initialized")
        except Exception as e:
            logging.error(f"Failed to initialize client: {e}")
            raise
    
    def analyze_video(self, video_url: str, video_name: str, analyzer_template_path: str, timeout_seconds: int = 3600) -> Dict[str, Any]:
        """
        Analyze a video using Azure Content Understanding.
        
        Args:
            video_url: URL to the video file or local path
            video_name: Name for the video
            analyzer_template_path: Path to analyzer configuration JSON
            timeout_seconds: Analysis timeout (default: 1 hour)
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Generate unique analyzer ID
            analyzer_id = f"video_analyzer_{video_name}_{uuid.uuid4()}"
            
            logging.info(f"Starting video analysis for: {video_name}")
            
            # Create analyzer with template
            logging.info(f"Creating analyzer with ID: {analyzer_id}")
            response = self.client.begin_create_analyzer(
                analyzer_id, 
                analyzer_template_path=analyzer_template_path
            )
            analyzer_result = self.client.poll_result(response)
            logging.info(f"Analyzer created successfully: {analyzer_result}")
            
            # Submit video for analysis
            logging.info(f"Submitting video for analysis: {video_url}")
            analysis_response = self.client.begin_analyze(
                analyzer_id, 
                file_location=video_url
            )
            
            # Wait for analysis completion
            logging.info("Waiting for analysis completion...")
            analysis_result = self.client.poll_result(
                analysis_response,
                timeout_seconds=timeout_seconds
            )
            
            # Clean up analyzer
            try:
                self.client.delete_analyzer(analyzer_id)
                logging.info(f"Analyzer {analyzer_id} deleted")
            except Exception as e:
                logging.warning(f"Failed to delete analyzer {analyzer_id}: {e}")
            
            logging.info(f"Video analysis completed for: {video_name}")
            return analysis_result
            
        except Exception as e:
            logging.error(f"Error analyzing video {video_name}: {e}")
            raise
    
    def extract_video_segments(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and process video segments from analysis results.
        
        Args:
            analysis_result: Raw analysis result from Content Understanding
            
        Returns:
            Processed segments with metadata
        """
        try:
            if not analysis_result or "result" not in analysis_result:
                raise ValueError("Invalid analysis result format")
            
            contents = analysis_result["result"].get("contents", [])
            
            # Process segments
            segments = []
            for i, segment in enumerate(contents):
                processed_segment = {
                    "segment_id": i + 1,
                    "content": segment,
                    "text_content": json.dumps(segment) if isinstance(segment, dict) else str(segment)
                }
                segments.append(processed_segment)
            
            result = {
                "total_segments": len(segments),
                "segments": segments,
                "analysis_metadata": {
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "original_result_keys": list(analysis_result.keys()) if isinstance(analysis_result, dict) else []
                }
            }
            
            logging.info(f"Extracted {len(segments)} video segments")
            return result
            
        except Exception as e:
            logging.error(f"Error extracting video segments: {e}")
            raise


# Singleton pattern for client reuse
_content_understanding_client = None

def get_content_understanding_client() -> ContentUnderstandingClient:
    """Get singleton instance of Content Understanding client."""
    global _content_understanding_client
    if _content_understanding_client is None:
        _content_understanding_client = ContentUnderstandingClient()
    return _content_understanding_client