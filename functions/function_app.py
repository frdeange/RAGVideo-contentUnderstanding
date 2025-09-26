import azure.functions as func
import logging
import json
import os
from datetime import datetime, timezone

app = func.FunctionApp()

@app.function_name("health_check")
@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Function to verify that the system is working correctly."""
    logging.info("Health check function triggered")
    
    try:
        # Test imports
        from shared.clients.content_understanding_client import AzureContentUnderstandingClient
        from shared.clients.azure_ai_client import ContentUnderstandingClient
        from azure.identity import DefaultAzureCredential
        
        # Test configuration
        config_status = {
            "azure_ai_endpoint": bool(os.environ.get("AZURE_AI_SERVICE_ENDPOINT")),
            "azure_openai_endpoint": bool(os.environ.get("AZURE_OPENAI_ENDPOINT")),
            "azure_search_endpoint": bool(os.environ.get("AZURE_SEARCH_ENDPOINT")),
            "storage_account": bool(os.environ.get("STORAGE_ACCOUNT_NAME")),
        }
        
        response_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "RAG Video v2 system is operational",
            "components": {
                "azure_functions": "✅ working",
                "content_understanding_client": "✅ available", 
                "azure_ai_client": "✅ available",
                "azure_identity": "✅ available"
            },
            "configuration": config_status,
            "authentication": "entra_id_enabled"
        }
        
        logging.info("Health check completed successfully")
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        
        error_response = {
            "status": "unhealthy", 
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "components": {
                "azure_functions": "✅ working",
                "imports": "❌ failed"
            }
        }
        
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )

@app.function_name("test_content_understanding")
@app.route(route="test/content-understanding", methods=["GET"])
def test_content_understanding(req: func.HttpRequest) -> func.HttpResponse:
    """Test the Content Understanding client configuration."""
    logging.info("Content Understanding test function triggered")
    
    try:
        from shared.clients.content_understanding_client import AzureContentUnderstandingClient
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        
        # Get configuration
        endpoint = os.environ.get("AZURE_AI_SERVICE_ENDPOINT")
        api_version = os.environ.get("AZURE_AI_SERVICE_API_VERSION", "2024-12-01-preview")
        
        if not endpoint:
            raise ValueError("AZURE_AI_SERVICE_ENDPOINT not configured")
        
        # Test credential setup
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(
            credential, 
            "https://cognitiveservices.azure.com/.default"
        )
        
        # Test client initialization
        client = AzureContentUnderstandingClient(
            endpoint=endpoint,
            api_version=api_version,
            token_provider=token_provider
        )
        
        response_data = {
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Content Understanding client configured correctly",
            "configuration": {
                "endpoint": endpoint,
                "api_version": api_version,
                "authentication": "entra_id",
                "client_initialized": True
            },
            "note": "Client is ready for use with proper Azure permissions"
        }
        
        logging.info("Content Understanding test completed successfully")
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logging.error(f"Content Understanding test failed: {e}")
        
        error_response = {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "configuration": {
                "endpoint": os.environ.get("AZURE_AI_SERVICE_ENDPOINT", "not_configured"),
                "api_version": os.environ.get("AZURE_AI_SERVICE_API_VERSION", "not_configured"),
            }
        }
        
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )