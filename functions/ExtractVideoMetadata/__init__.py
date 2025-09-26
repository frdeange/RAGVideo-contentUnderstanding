import logging
import json
from datetime import datetime, timezone
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
from typing import Dict, Any


async def main(video_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract basic metadata from the uploaded video file.
    
    This activity function retrieves basic information about the video
    such as file size, upload time, and basic properties.
    """
    logging.info(f"Extracting metadata for video: {video_info.get('blob_name')}")
    
    try:
        # Get blob service client
        storage_connection_string = os.environ.get("AzureWebJobsStorage")
        if not storage_connection_string or storage_connection_string == "UseDevelopmentStorage=true":
            # For local development, we'll simulate metadata extraction
            return simulate_metadata_extraction(video_info)
        
        blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
        
        # Get blob client
        container_name = video_info.get('container_name', 'videos')
        blob_name = video_info.get('blob_name')
        
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        # Get blob properties
        blob_properties = blob_client.get_blob_properties()
        
        # Extract metadata
        metadata = {
            "file_info": {
                "blob_name": blob_name,
                "container_name": container_name,
                "blob_url": video_info.get('blob_url'),
                "size_bytes": blob_properties.size,
                "size_mb": round(blob_properties.size / (1024 * 1024), 2),
                "content_type": blob_properties.content_settings.content_type,
                "creation_time": blob_properties.creation_time.isoformat() if blob_properties.creation_time else None,
                "last_modified": blob_properties.last_modified.isoformat() if blob_properties.last_modified else None,
                "etag": blob_properties.etag,
            },
            "processing_info": {
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "extraction_status": "completed"
            },
            "video_properties": {
                # These would normally be extracted using a media processing library
                # For now, we'll set placeholder values that can be updated by the AI analysis
                "duration_seconds": None,
                "resolution": None,
                "frame_rate": None,
                "codec": None,
                "bitrate": None
            }
        }
        
        logging.info(f"Successfully extracted metadata for {blob_name}: {metadata['file_info']['size_mb']} MB")
        return metadata
        
    except Exception as e:
        logging.error(f"Error extracting metadata for video {video_info.get('blob_name')}: {str(e)}")
        raise Exception(f"Metadata extraction failed: {str(e)}")


def simulate_metadata_extraction(video_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate metadata extraction for local development.
    """
    return {
        "file_info": {
            "blob_name": video_info.get('blob_name', 'sample_video.mp4'),
            "container_name": video_info.get('container_name', 'videos'),
            "blob_url": video_info.get('blob_url', 'https://example.com/sample_video.mp4'),
            "size_bytes": video_info.get('content_length', 10485760),  # 10MB default
            "size_mb": round(video_info.get('content_length', 10485760) / (1024 * 1024), 2),
            "content_type": video_info.get('content_type', 'video/mp4'),
            "creation_time": datetime.now(timezone.utc).isoformat(),
            "last_modified": datetime.now(timezone.utc).isoformat(),
            "etag": "mock-etag-12345",
        },
        "processing_info": {
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "extraction_status": "completed"
        },
        "video_properties": {
            "duration_seconds": 120,  # 2 minutes default
            "resolution": "1920x1080",
            "frame_rate": 30,
            "codec": "h264",
            "bitrate": 2000
        }
    }