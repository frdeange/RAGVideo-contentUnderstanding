"""
Shared client modules for Azure services.
Provides centralized access to Azure AI, OpenAI, and Search services.
"""

from .azure_ai_client import ContentUnderstandingClient, get_content_understanding_client
from .openai_client import AzureOpenAIClient, get_openai_client
from .search_client import AzureSearchClient, get_search_client

__all__ = [
    "ContentUnderstandingClient",
    "get_content_understanding_client", 
    "AzureOpenAIClient",
    "get_openai_client",
    "AzureSearchClient", 
    "get_search_client"
]