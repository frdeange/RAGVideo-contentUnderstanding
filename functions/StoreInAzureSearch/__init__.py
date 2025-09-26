import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List
import azure.functions as func
import asyncio
import sys

# Add shared folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.clients.search_client import get_search_client


async def main(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store video analysis results and embeddings in Azure Cognitive Search.
    
    This activity function creates or updates a search document with all the
    video metadata, analysis results, and vector embeddings for semantic search.
    """
    video_info = input_data.get('video_info', {})
    metadata = input_data.get('metadata', {})
    analysis = input_data.get('analysis', {})
    embeddings = input_data.get('embeddings', {})
    
    logging.info(f"Storing search document for video: {video_info.get('blob_name')}")
    
    try:
        # Get Azure Search client
        search_client = get_search_client()
        
        # Check if we have proper configuration
        if not os.environ.get("AZURE_SEARCH_ENDPOINT"):
            # For development, return simulated storage result
            logging.info("No Search endpoint configured, returning simulated storage result")
            return simulate_search_storage(video_info, metadata, analysis, embeddings)
        
        # Prepare search document
        search_document = prepare_search_document(video_info, metadata, analysis, embeddings)
        
        # Store document using official client
        storage_result = search_client.upload_document(search_document)
        
        logging.info(f"Successfully stored search document for: {video_info.get('blob_name')}")
        return {
            "document_id": search_document.get("id"),
            "status": "success",
            "upload_result": storage_result
        }
        
    except Exception as e:
        logging.error(f"Error storing search document for video {video_info.get('blob_name')}: {str(e)}")
        raise Exception(f"Search storage failed: {str(e)}")


def prepare_search_document(
    video_info: Dict[str, Any], 
    metadata: Dict[str, Any], 
    analysis: Dict[str, Any], 
    embeddings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Prepare the document structure for Azure Cognitive Search.
    """
    # Generate unique document ID
    document_id = f"video_{video_info.get('blob_name', '').replace('.', '_').replace(' ', '_')}_{int(datetime.now(timezone.utc).timestamp())}"
    
    # Extract key information
    file_info = metadata.get('file_info', {})
    insights = analysis.get('insights', {})
    transcript = insights.get('transcript', {})
    
    # Prepare the search document
    document = {
        "id": document_id,
        "video_name": video_info.get('blob_name', ''),
        "container_name": video_info.get('container_name', ''),
        "blob_url": video_info.get('blob_url', ''),
        "file_size_mb": file_info.get('size_mb', 0),
        "content_type": file_info.get('content_type', ''),
        "upload_time": file_info.get('creation_time', datetime.now(timezone.utc).isoformat()),
        "last_modified": file_info.get('last_modified', datetime.now(timezone.utc).isoformat()),
        
        # Video properties
        "duration_seconds": metadata.get('video_properties', {}).get('duration_seconds', 0),
        "resolution": metadata.get('video_properties', {}).get('resolution', ''),
        "frame_rate": metadata.get('video_properties', {}).get('frame_rate', 0),
        
        # Transcript and language
        "transcript": transcript.get('text', ''),
        "language": transcript.get('language', ''),
        "transcript_confidence": transcript.get('confidence', 0),
        
        # Topics and labels for faceted search
        "topics": [topic.get('name', '') for topic in insights.get('topics', [])],
        "labels": [label.get('name', '') for label in insights.get('labels', [])],
        
        # Scene information
        "scenes": [
            {
                "description": scene.get('description', ''),
                "start_time": scene.get('start', 0),
                "end_time": scene.get('end', 0)
            }
            for scene in insights.get('scenes', [])
        ],
        
        # Keyframes for visual search
        "keyframes": [
            {
                "time": kf.get('time', 0),
                "description": kf.get('description', ''),
                "confidence": kf.get('confidence', 0)
            }
            for kf in insights.get('keyframes', [])
        ],
        
        # Faces detected
        "faces_detected": len(insights.get('faces', [])),
        "face_names": [face.get('name', '') for face in insights.get('faces', [])],
        
        # Processing metadata
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "analysis_id": analysis.get('analysis_id', ''),
        "processing_version": "1.0",
        
        # Vector embeddings for semantic search
        "transcript_vector": embeddings.get('embeddings', {}).get('combined_content', {}).get('vector', []),
        "topics_vector": embeddings.get('embeddings', {}).get('topics', {}).get('vector', []),
        "scenes_vector": embeddings.get('embeddings', {}).get('scenes', {}).get('vector', []),
        
        # Searchable combined text
        "searchable_content": f"{transcript.get('text', '')} {' '.join([topic.get('name', '') for topic in insights.get('topics', [])])} {' '.join([label.get('name', '') for label in insights.get('labels', [])])}".strip()
    }
    
    return document


async def store_in_azure_search(endpoint: str, index_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store the document in Azure Cognitive Search.
    """
    # This is a placeholder for the actual Azure Search API call
    # In a real implementation, you would:
    # 1. Use the Azure Search Python SDK
    # 2. Upload or merge the document into the search index
    # 3. Handle any indexing errors
    
    # For now, simulate the API call
    await asyncio.sleep(1)  # Simulate processing time
    
    return {
        "document_id": document.get('id'),
        "index_name": index_name,
        "operation": "upload",
        "status": "succeeded",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def simulate_search_storage(
    video_info: Dict[str, Any], 
    metadata: Dict[str, Any], 
    analysis: Dict[str, Any], 
    embeddings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Simulate Azure Search storage for development purposes.
    """
    document_id = f"video_{video_info.get('blob_name', 'sample').replace('.', '_')}_{int(datetime.now(timezone.utc).timestamp())}"
    
    return {
        "document_id": document_id,
        "index_name": "videos",
        "operation": "upload",
        "status": "succeeded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "document_size_kb": 25.6,
        "indexing_duration_ms": 450,
        "search_url": f"https://example-search.search.windows.net/indexes/videos/docs/{document_id}"
    }