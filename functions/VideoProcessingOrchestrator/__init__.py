import logging
import json
from datetime import datetime, timedelta
import azure.functions as func
import azure.durable_functions as df
from typing import Dict, Any, List


def orchestrator_function(context: df.DurableOrchestrationContext) -> Dict[str, Any]:
    """
    Orchestrates the complete video processing workflow.
    
    This function coordinates all the steps needed to process a video:
    1. Extract video metadata and basic information
    2. Analyze video content using Azure AI Video Indexer
    3. Generate embeddings for search
    4. Store results in Azure Cognitive Search
    5. Update processing status
    """
    
    # Get the input video information
    video_info = context.get_input()
    logging.info(f"Starting orchestration for video: {video_info.get('blob_name')}")
    
    # Initialize result tracking
    orchestration_result = {
        "video_info": video_info,
        "start_time": context.current_utc_datetime.isoformat(),
        "status": "processing",
        "steps": {},
        "errors": []
    }
    
    try:
        # Step 1: Extract Video Metadata
        logging.info("Step 1: Extracting video metadata...")
        metadata_result = yield context.call_activity(
            "ExtractVideoMetadata", 
            video_info
        )
        orchestration_result["steps"]["metadata"] = {
            "status": "completed",
            "result": metadata_result,
            "timestamp": context.current_utc_datetime.isoformat()
        }
        
        # Step 2: Analyze Video Content with Azure AI
        logging.info("Step 2: Analyzing video content with Azure AI...")
        analysis_result = yield context.call_activity(
            "AnalyzeVideoContent", 
            {
                "video_info": video_info,
                "metadata": metadata_result
            }
        )
        orchestration_result["steps"]["analysis"] = {
            "status": "completed", 
            "result": analysis_result,
            "timestamp": context.current_utc_datetime.isoformat()
        }
        
        # Step 3: Generate Embeddings for Search
        logging.info("Step 3: Generating embeddings...")
        embeddings_result = yield context.call_activity(
            "GenerateEmbeddings",
            {
                "video_info": video_info,
                "analysis": analysis_result,
                "metadata": metadata_result
            }
        )
        orchestration_result["steps"]["embeddings"] = {
            "status": "completed",
            "result": embeddings_result,
            "timestamp": context.current_utc_datetime.isoformat()
        }
        
        # Step 4: Store in Azure Cognitive Search
        logging.info("Step 4: Storing in Azure Search...")
        search_result = yield context.call_activity(
            "StoreInAzureSearch",
            {
                "video_info": video_info,
                "metadata": metadata_result,
                "analysis": analysis_result,
                "embeddings": embeddings_result
            }
        )
        orchestration_result["steps"]["search_storage"] = {
            "status": "completed",
            "result": search_result,
            "timestamp": context.current_utc_datetime.isoformat()
        }
        
        # Step 5: Generate Final Summary and Insights
        logging.info("Step 5: Generating final insights...")
        insights_result = yield context.call_activity(
            "GenerateVideoInsights",
            {
                "video_info": video_info,
                "metadata": metadata_result,
                "analysis": analysis_result,
                "search_document_id": search_result.get("document_id")
            }
        )
        orchestration_result["steps"]["insights"] = {
            "status": "completed",
            "result": insights_result,
            "timestamp": context.current_utc_datetime.isoformat()
        }
        
        # Mark as completed
        orchestration_result["status"] = "completed"
        orchestration_result["end_time"] = context.current_utc_datetime.isoformat()
        
        # Calculate processing duration
        start_time = datetime.fromisoformat(orchestration_result["start_time"].replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(orchestration_result["end_time"].replace("Z", "+00:00"))
        orchestration_result["processing_duration_seconds"] = (end_time - start_time).total_seconds()
        
        logging.info(f"Video processing completed successfully for: {video_info.get('blob_name')}")
        
    except Exception as e:
        # Handle orchestration errors
        error_info = {
            "error": str(e),
            "timestamp": context.current_utc_datetime.isoformat(),
            "step": "orchestration"
        }
        orchestration_result["errors"].append(error_info)
        orchestration_result["status"] = "failed"
        orchestration_result["end_time"] = context.current_utc_datetime.isoformat()
        
        logging.error(f"Orchestration failed for video {video_info.get('blob_name')}: {str(e)}")
        
        # Optionally, implement retry logic here
        # For now, we'll just fail the orchestration
    
    return orchestration_result


# Register the orchestrator function
main = df.Orchestrator.create(orchestrator_function)