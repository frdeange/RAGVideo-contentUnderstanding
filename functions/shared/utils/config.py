"""
Configuration settings and utilities for the RAG Video processing system.
"""

import os
from typing import Dict, Any
import logging


class Config:
    """Configuration settings for the application."""
    
    # Azure AI Services
    AZURE_AI_SERVICE_ENDPOINT = os.environ.get("AZURE_AI_SERVICE_ENDPOINT", "")
    AZURE_AI_SERVICE_API_VERSION = os.environ.get("AZURE_AI_SERVICE_API_VERSION", "2024-12-01-preview")
    AZURE_AI_SERVICE_KEY = os.environ.get("AZURE_AI_SERVICE_KEY", "")
    
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "")
    AZURE_OPENAI_CHAT_API_VERSION = os.environ.get("AZURE_OPENAI_CHAT_API_VERSION", "2024-08-01-preview")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "")
    AZURE_OPENAI_EMBEDDING_API_VERSION = os.environ.get("AZURE_OPENAI_EMBEDDING_API_VERSION", "2023-05-15")
    AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "")
    
    # Azure Search
    AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
    AZURE_SEARCH_INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "videos")
    AZURE_SEARCH_API_VERSION = os.environ.get("AZURE_SEARCH_API_VERSION", "2024-07-01")
    AZURE_SEARCH_ADMIN_KEY = os.environ.get("AZURE_SEARCH_ADMIN_KEY", "")
    AZURE_SEARCH_QUERY_KEY = os.environ.get("AZURE_SEARCH_QUERY_KEY", "")
    
    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AzureWebJobsStorage", "")
    
    # Processing Settings
    MAX_VIDEO_SIZE_MB = int(os.environ.get("MAX_VIDEO_SIZE_MB", "500"))
    ORCHESTRATION_TIMEOUT_MINUTES = int(os.environ.get("ORCHESTRATION_TIMEOUT_MINUTES", "60"))
    EMBEDDING_BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "16"))
    
    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = [
        "video/mp4", "video/avi", "video/mov", "video/wmv", 
        "video/flv", "video/webm", "video/quicktime", "video/x-msvideo"
    ]
    
    SUPPORTED_VIDEO_EXTENSIONS = [
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"
    ]
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """
        Validate the current configuration and return status.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "services": {}
        }
        
        # Check Azure AI Services
        if not cls.AZURE_AI_SERVICE_ENDPOINT:
            results["warnings"].append("Azure AI Service endpoint not configured - will use simulation mode")
        results["services"]["azure_ai"] = bool(cls.AZURE_AI_SERVICE_ENDPOINT)
        
        # Check Azure OpenAI
        if not cls.AZURE_OPENAI_ENDPOINT:
            results["warnings"].append("Azure OpenAI endpoint not configured - will use simulation mode")
        results["services"]["azure_openai"] = bool(cls.AZURE_OPENAI_ENDPOINT)
        
        # Check Azure Search
        if not cls.AZURE_SEARCH_ENDPOINT:
            results["warnings"].append("Azure Search endpoint not configured - will use simulation mode")
        results["services"]["azure_search"] = bool(cls.AZURE_SEARCH_ENDPOINT)
        
        # Check storage
        if not cls.AZURE_STORAGE_CONNECTION_STRING or cls.AZURE_STORAGE_CONNECTION_STRING == "UseDevelopmentStorage=true":
            results["warnings"].append("Using development storage - not suitable for production")
        results["services"]["azure_storage"] = bool(cls.AZURE_STORAGE_CONNECTION_STRING)
        
        return results
    
    @classmethod
    def get_service_status(cls) -> Dict[str, str]:
        """Get the status of all configured services."""
        return {
            "azure_ai": "configured" if cls.AZURE_AI_SERVICE_ENDPOINT else "simulation",
            "azure_openai": "configured" if cls.AZURE_OPENAI_ENDPOINT else "simulation", 
            "azure_search": "configured" if cls.AZURE_SEARCH_ENDPOINT else "simulation",
            "azure_storage": "configured" if cls.AZURE_STORAGE_CONNECTION_STRING and cls.AZURE_STORAGE_CONNECTION_STRING != "UseDevelopmentStorage=true" else "development"
        }


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def is_video_file(content_type: str = None, filename: str = None) -> bool:
    """
    Check if a file is a supported video format.
    
    Args:
        content_type: MIME content type
        filename: File name with extension
        
    Returns:
        True if the file is a supported video format
    """
    if content_type and content_type.lower() in Config.SUPPORTED_VIDEO_FORMATS:
        return True
    
    if filename:
        return any(filename.lower().endswith(ext) for ext in Config.SUPPORTED_VIDEO_EXTENSIONS)
    
    return False


def get_file_size_category(size_mb: float) -> str:
    """
    Categorize file size for processing optimization.
    
    Args:
        size_mb: File size in MB
        
    Returns:
        Size category string
    """
    if size_mb < 10:
        return "small"
    elif size_mb < 100:
        return "medium" 
    elif size_mb < 500:
        return "large"
    else:
        return "extra_large"