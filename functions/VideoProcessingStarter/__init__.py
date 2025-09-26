import logging
import json
import azure.functions as func
from azure.durable_functions import DurableOrchestrationClient


async def main(event: func.EventGridEvent, starter: str) -> None:
    """
    Event Grid triggered function that starts the video processing orchestration.
    
    This function is triggered when a new video is uploaded to blob storage
    and initiates the durable function orchestration for video analysis.
    """
    logging.info(f"Event Grid trigger function processed a request: {event.get_json()}")
    
    try:
        # Parse the Event Grid event
        event_data = event.get_json()
        
        # Extract video information from the event
        video_info = {
            "blob_url": event_data.get("url"),
            "blob_name": event_data.get("subject", "").split("/")[-1] if event_data.get("subject") else None,
            "container_name": extract_container_name(event_data.get("subject", "")),
            "event_type": event_data.get("eventType"),
            "event_time": event_data.get("eventTime"),
            "content_type": event_data.get("data", {}).get("contentType", ""),
            "content_length": event_data.get("data", {}).get("contentLength", 0)
        }
        
        # Validate that this is a video file
        if not is_video_file(video_info["content_type"], video_info["blob_name"]):
            logging.info(f"Skipping non-video file: {video_info['blob_name']}")
            return
        
        # Create orchestration client
        client = DurableOrchestrationClient(starter)
        
        # Start the orchestration
        instance_id = await client.start_new(
            orchestration_function_name="VideoProcessingOrchestrator",
            client_input=video_info
        )
        
        logging.info(f"Started video processing orchestration with ID: {instance_id}")
        logging.info(f"Processing video: {video_info['blob_name']} from container: {video_info['container_name']}")
        
    except Exception as e:
        logging.error(f"Error starting video processing orchestration: {str(e)}")
        raise


def extract_container_name(subject: str) -> str:
    """Extract container name from Event Grid subject path."""
    # Subject format: /blobServices/default/containers/{container-name}/blobs/{blob-name}
    try:
        parts = subject.split("/")
        container_index = parts.index("containers") + 1
        return parts[container_index] if container_index < len(parts) else ""
    except (ValueError, IndexError):
        return ""


def is_video_file(content_type: str, blob_name: str) -> bool:
    """
    Check if the uploaded file is a video based on content type and extension.
    """
    # Check content type
    video_content_types = [
        "video/mp4", 
        "video/avi", 
        "video/mov", 
        "video/wmv", 
        "video/flv", 
        "video/webm",
        "video/quicktime",
        "video/x-msvideo"
    ]
    
    if content_type and content_type.lower() in video_content_types:
        return True
    
    # Fallback: check file extension
    if blob_name:
        video_extensions = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"]
        return any(blob_name.lower().endswith(ext) for ext in video_extensions)
    
    return False