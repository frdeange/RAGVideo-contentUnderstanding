# RAG Video V2 - Azure Durable Functions Video Processing Pipeline

This project implements a complete video processing system using **Azure Durable Functions** to create a robust and scalable workflow that analyzes videos with AI and makes them searchable through RAG (Retrieval-Augmented Generation).

## 🏗️ Durable Functions Architecture

```
[Video Upload] → [Event Grid] → [Starter Function] → [Orchestrator] → [Activity Functions] → [Search Index]
                                      ↓
                            [Status API] ← [Monitor Progress]
```

### Implemented Components:
- ✅ **VideoProcessingStarter** - Event Grid trigger
- ✅ **VideoProcessingOrchestrator** - Workflow coordinator  
- ✅ **ExtractVideoMetadata** - Metadata extraction
- ✅ **AnalyzeVideoContent** - AI video analysis
- ✅ **GenerateEmbeddings** - Vector embeddings
- ✅ **StoreInAzureSearch** - Search indexing
- ✅ **GenerateVideoInsights** - Final insights
- ✅ **VideoProcessingStatus** - Status monitoring API

## Features

- ✅ **Automated Video Processing**: Triggered by blob uploads via Event Grid
- ✅ **Azure Content Understanding**: AI-powered video analysis (transcript, scenes, objects)
- ✅ **Semantic Search**: Vector embeddings with Azure OpenAI integration
- ✅ **Duplicate Detection**: Hybrid approach (filename+size → content hash)
- ✅ **Azure AI Search**: Full-text and vector search indexing
- ✅ **Durable Functions**: Reliable workflow orchestration with built-in retry logic
- ✅ **Official Microsoft SDKs**: No LangChain dependencies - pure Microsoft libraries
- ✅ **Structured Logging**: Comprehensive monitoring and telemetry
- ✅ **DevContainer**: Complete development environment

## Technology Stack

### Core Azure Services
- **Azure Durable Functions**: Workflow orchestration and state management
- **Azure Content Understanding**: Video analysis and AI insights
- **Azure OpenAI**: Embeddings generation and chat completions
- **Azure AI Search**: Document indexing and semantic search
- **Azure Blob Storage**: Video file storage and Event Grid triggers
- **Azure Application Insights**: Logging and performance monitoring

### Official Microsoft Libraries
- `azure-functions` & `azure-durable-functions`: Function runtime and orchestration
- `azure-search-documents`: Official Azure AI Search SDK  
- `openai`: Official OpenAI Python SDK with Azure support
- `azure-identity`: Unified authentication with DefaultAzureCredential
- `azure-core`: Common Azure SDK functionality
- `aiohttp`: HTTP client for Azure Content Understanding API calls

> **Note**: The `python-content-understanding-client` is not yet publicly available. The implementation uses direct API calls with proper authentication through `DefaultAzureCredential`.

## Development Setup

### Prerequisites

- Docker Desktop
- VS Code with Dev Containers extension
- Azure subscription with required services

### Quick Start

1. **Open in DevContainer**
   ```bash
   # VS Code will prompt to reopen in container
   # Or use Command Palette: "Dev Containers: Reopen in Container"
   ```

2. **Configure Environment**
   ```bash
   # Copy and fill local.settings.json
   cp functions/local.settings.json functions/local.settings.json.local
   # Edit with your Azure service endpoints and keys
   ```

3. **Install Dependencies**
   ```bash
   cd functions
   pip install -r requirements.txt
   ```

4. **Verify Configuration**
   ```bash
   # Optional: Test configuration
   python -c "from shared.utils.config import Config; print(Config.validate_configuration())"
   ```

5. **Run Functions Locally**
   ```bash
   cd functions
   func start
   ```

### Architecture Benefits

✅ **No LangChain Dependencies**: Eliminates complex dependency management and potential version conflicts

✅ **Official SDK Reliability**: Microsoft-maintained libraries with built-in retry logic, error handling, and performance optimizations

✅ **Unified Authentication**: Uses `DefaultAzureCredential` for seamless authentication across all Azure services

✅ **Better Error Handling**: Official SDKs provide detailed error messages and proper exception hierarchy

✅ **Future-Proof**: Guaranteed compatibility with Azure service updates and new features

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_AI_SERVICE_ENDPOINT` | Content Understanding endpoint | `https://your-cu.cognitiveservices.azure.com/` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://your-openai.openai.azure.com/` |
| `AZURE_SEARCH_ENDPOINT` | AI Search service endpoint | `https://your-search.search.windows.net/` |
| `STORAGE_CONNECTION_STRING` | Storage account connection string | `DefaultEndpointsProtocol=https;...` |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_VIDEO_SIZE_MB` | `500` | Maximum video file size |
| `PROCESSING_TIMEOUT_MINUTES` | `30` | Video processing timeout |
| `ENABLE_DUPLICATE_DETECTION` | `true` | Enable duplicate video detection |

## Azure Functions

### Durable Functions Workflow

#### 1. VideoProcessingStarter
- **Trigger**: Event Grid (blob created) or HTTP request
- **Purpose**: Initiates video processing orchestration
- **Output**: Starts durable orchestration

#### 2. VideoProcessingOrchestrator  
- **Type**: Orchestrator Function
- **Purpose**: Coordinates the complete video processing workflow
- **Activities**: Manages all processing steps and error handling

#### 3. ExtractVideoMetadata
- **Type**: Activity Function
- **Purpose**: Extracts basic video metadata (duration, format, size)
- **Output**: Video metadata object

#### 4. AnalyzeVideoContent
- **Type**: Activity Function
- **Purpose**: Calls Azure Content Understanding API for video analysis
- **Output**: AI insights (transcript, scenes, objects, etc.)

#### 5. GenerateEmbeddings
- **Type**: Activity Function 
- **Purpose**: Creates vector embeddings using Azure OpenAI
- **Output**: Embedding vectors for semantic search

#### 6. StoreInAzureSearch
- **Type**: Activity Function
- **Purpose**: Indexes processed content in Azure AI Search
- **Output**: Search document with embeddings

#### 7. GenerateVideoInsights
- **Type**: Activity Function
- **Purpose**: Creates intelligent summaries using Azure OpenAI
- **Output**: Final insights and recommendations

#### 8. VideoProcessingStatus
- **Trigger**: HTTP GET
- **Purpose**: Provides real-time processing status
- **Output**: Current orchestration status

## Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests (requires Azure resources)
python -m pytest tests/integration/
```

## Deployment

```bash
# Deploy to Azure (requires Azure CLI login)
func azure functionapp publish <your-function-app-name>
```

## Monitoring

- **Application Insights**: Structured logging and telemetry
- **Azure Monitor**: Performance metrics and alerts
- **Storage Queues**: Processing status and dead letter handling

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Verify Azure CLI login
   az login
   # Or set environment variables for service principal
   export AZURE_CLIENT_ID="your-client-id"
   export AZURE_CLIENT_SECRET="your-client-secret"  
   export AZURE_TENANT_ID="your-tenant-id"
   ```

2. **Content Understanding API Issues**
   - Check video file size and format (max 500MB by default)
   - Verify `AZURE_AI_SERVICE_ENDPOINT` configuration
   - Ensure proper authentication credentials
   - Monitor API rate limits and quotas

3. **Azure OpenAI Connection Issues**
   ```bash
   # Verify deployment names match configuration
   export AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="text-embedding-ada-002"
   export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-35-turbo"
   ```

4. **Search Indexing Failures**
   - Verify AI Search service capacity and pricing tier
   - Check embedding model deployment status in Azure OpenAI
   - Review index schema compatibility
   - Monitor search service quotas

5. **Durable Functions Issues**
   - Check `DURABLE_FUNCTION_HUB_NAME` uniqueness
   - Verify storage account connection string
   - Monitor orchestration status through status API
   - Review Application Insights for detailed error logs

### SDK-Specific Troubleshooting

**Azure Search SDK**:
```python
# Enable detailed logging
import logging
logging.getLogger("azure.search").setLevel(logging.DEBUG)
```

**OpenAI SDK**:
```python  
# Enable detailed logging
import logging
logging.getLogger("openai").setLevel(logging.DEBUG)
```

**Azure Identity**:
```python
# Test credential chain
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default")
print("Authentication successful")
```

## Migration from LangChain

This project has been refactored to eliminate LangChain dependencies in favor of official Microsoft SDKs. Key changes include:

### Before (LangChain-based)
```python
# Old approach with LangChain
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import AzureSearch

embeddings = AzureOpenAIEmbeddings(...)
vector_store = AzureSearch(...)
```

### After (Official SDKs)  
```python
# New approach with official SDKs
from openai import AzureOpenAI
from azure.search.documents import SearchClient

client = AzureOpenAI(...)
search_client = SearchClient(...)
```

### Benefits of Migration
- **Reduced Dependencies**: Eliminates 15+ LangChain packages
- **Better Performance**: Direct SDK calls without abstraction overhead
- **Enhanced Reliability**: Official SDKs have better error handling and retry logic
- **Simplified Debugging**: Direct error messages from Azure services
- **Future-Proof**: Guaranteed compatibility with Azure service updates

## Support

For issues and questions:
1. Check the logs in Application Insights for detailed error information
2. Review the troubleshooting section above
3. Verify all Azure service configurations and quotas
4. Create an issue in the repository with relevant logs and configuration details