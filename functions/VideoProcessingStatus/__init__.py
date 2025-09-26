import logging
import json
from typing import Dict, Any, Optional
import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """
    HTTP triggered function to check the status of video processing orchestrations.
    
    This function allows clients to query the status of video processing workflows,
    retrieve results, and get progress updates.
    
    Endpoints:
    - GET /api/VideoProcessingStatus/{instanceId} - Get status of specific orchestration
    - GET /api/VideoProcessingStatus?video_name={name} - Get status by video name
    - GET /api/VideoProcessingStatus - List all recent orchestrations
    """
    logging.info("Video processing status function processed a request.")
    
    try:
        # Get query parameters and route data
        instance_id = req.route_params.get('instanceId')
        video_name = req.params.get('video_name')
        include_history = req.params.get('include_history', 'false').lower() == 'true'
        
        # Create orchestration client
        client = DurableOrchestrationClient(starter)
        
        if instance_id:
            # Get status for specific orchestration instance
            status_result = await get_orchestration_status(client, instance_id, include_history)
        elif video_name:
            # Find orchestration by video name
            status_result = await find_orchestration_by_video_name(client, video_name, include_history)
        else:
            # List recent orchestrations
            status_result = await list_recent_orchestrations(client)
        
        return func.HttpResponse(
            json.dumps(status_result, indent=2, default=str),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    
    except ValueError as e:
        logging.error(f"Bad request: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Bad Request", "message": str(e)}),
            status_code=400,
            headers={"Content-Type": "application/json"}
        )
    
    except Exception as e:
        logging.error(f"Error processing status request: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Internal Server Error", "message": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )


async def get_orchestration_status(
    client: DurableOrchestrationClient, 
    instance_id: str, 
    include_history: bool = False
) -> Dict[str, Any]:
    """
    Get the status of a specific orchestration instance.
    
    Args:
        client: Durable orchestration client
        instance_id: Orchestration instance ID
        include_history: Whether to include execution history
        
    Returns:
        Orchestration status information
    """
    try:
        # Get orchestration status
        status = await client.get_status(instance_id, show_history=include_history, show_history_output=include_history)
        
        if not status:
            raise ValueError(f"Orchestration instance '{instance_id}' not found")
        
        # Extract video information from input if available
        video_info = {}
        if status.input_:
            try:
                input_data = json.loads(status.input_) if isinstance(status.input_, str) else status.input_
                video_info = {
                    "video_name": input_data.get("blob_name", "Unknown"),
                    "container_name": input_data.get("container_name", "Unknown"),
                    "blob_url": input_data.get("blob_url", "")
                }
            except (json.JSONDecodeError, AttributeError):
                video_info = {"video_name": "Unable to parse"}
        
        # Parse output if available
        output_data = {}
        if status.output:
            try:
                output_data = json.loads(status.output) if isinstance(status.output, str) else status.output
            except (json.JSONDecodeError, AttributeError):
                output_data = {"raw_output": str(status.output)}
        
        # Calculate processing duration if completed
        processing_duration = None
        if status.created_time and status.last_updated_time:
            duration_seconds = (status.last_updated_time - status.created_time).total_seconds()
            processing_duration = f"{duration_seconds:.1f} seconds"
        
        result = {
            "instance_id": instance_id,
            "runtime_status": status.runtime_status.name if status.runtime_status else "Unknown",
            "created_time": status.created_time.isoformat() if status.created_time else None,
            "last_updated_time": status.last_updated_time.isoformat() if status.last_updated_time else None,
            "processing_duration": processing_duration,
            "video_info": video_info,
            "output": output_data,
            "custom_status": status.custom_status
        }
        
        # Add execution history if requested
        if include_history and hasattr(status, 'history_events') and status.history_events:
            result["execution_history"] = [
                {
                    "name": event.name if hasattr(event, 'name') else str(event),
                    "timestamp": event.timestamp.isoformat() if hasattr(event, 'timestamp') and event.timestamp else None,
                    "event_type": event.event_type.name if hasattr(event, 'event_type') else "Unknown"
                }
                for event in status.history_events
            ]
        
        # Add management URLs
        result["management_urls"] = {
            "status_query": f"/api/VideoProcessingStatus/{instance_id}",
            "status_with_history": f"/api/VideoProcessingStatus/{instance_id}?include_history=true"
        }
        
        return result
    
    except Exception as e:
        logging.error(f"Error getting orchestration status for {instance_id}: {e}")
        raise


async def find_orchestration_by_video_name(
    client: DurableOrchestrationClient, 
    video_name: str, 
    include_history: bool = False
) -> Dict[str, Any]:
    """
    Find orchestration instance by video name.
    
    Args:
        client: Durable orchestration client
        video_name: Name of the video file
        include_history: Whether to include execution history
        
    Returns:
        Orchestration status information or error if not found
    """
    try:
        # This is a simplified implementation
        # In a production system, you might want to store instance IDs with metadata
        # or use a more sophisticated tracking mechanism
        
        # For now, return a message indicating the limitation
        return {
            "message": f"Search by video name '{video_name}' not yet implemented",
            "suggestion": "Use the instance ID returned when the video processing started",
            "alternative": "Use the list endpoint to see all recent orchestrations"
        }
    
    except Exception as e:
        logging.error(f"Error finding orchestration for video {video_name}: {e}")
        raise


async def list_recent_orchestrations(client: DurableOrchestrationClient) -> Dict[str, Any]:
    """
    List recent orchestration instances.
    
    Args:
        client: Durable orchestration client
        
    Returns:
        List of recent orchestrations
    """
    try:
        # This is a placeholder implementation
        # The actual Durable Functions client might have different methods for listing instances
        
        return {
            "message": "Listing recent orchestrations not yet fully implemented",
            "note": "This feature requires additional configuration in the Durable Functions setup",
            "recommendation": "Store instance IDs when starting orchestrations for better tracking"
        }
    
    except Exception as e:
        logging.error(f"Error listing orchestrations: {e}")
        raise


def format_runtime_status(status: str) -> Dict[str, str]:
    """
    Format runtime status with human-readable descriptions.
    
    Args:
        status: Runtime status string
        
    Returns:
        Formatted status information
    """
    status_descriptions = {
        "Running": {
            "description": "Video processing is currently in progress",
            "expected_actions": "Please wait for completion"
        },
        "Completed": {
            "description": "Video processing completed successfully", 
            "expected_actions": "Results are available in the output"
        },
        "Failed": {
            "description": "Video processing failed",
            "expected_actions": "Check error details and retry if needed"
        },
        "Canceled": {
            "description": "Video processing was canceled",
            "expected_actions": "Restart processing if needed"
        },
        "Terminated": {
            "description": "Video processing was terminated",
            "expected_actions": "Check logs and restart if needed"
        },
        "Pending": {
            "description": "Video processing is queued and will start soon",
            "expected_actions": "Please wait for processing to begin"
        }
    }
    
    return status_descriptions.get(status, {
        "description": f"Unknown status: {status}",
        "expected_actions": "Contact support if this persists"
    })