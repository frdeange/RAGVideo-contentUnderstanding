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
from shared.clients.openai_client import get_openai_client


async def main(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate embeddings for video content using Azure OpenAI.
    
    This activity function creates vector embeddings for the video transcript,
    topics, and other textual insights to enable semantic search.
    """
    video_info = input_data.get('video_info', {})
    analysis = input_data.get('analysis', {})
    metadata = input_data.get('metadata', {})
    
    logging.info(f"Generating embeddings for video: {video_info.get('blob_name')}")
    
    try:
        # Get Azure OpenAI client
        openai_client = get_openai_client()
        
        # Check if we have proper configuration
        if not os.environ.get("AZURE_OPENAI_ENDPOINT"):
            # For development, return simulated embeddings
            logging.info("No OpenAI endpoint configured, returning simulated embeddings")
            return simulate_embeddings_generation(video_info, analysis, metadata)
        
        # Prepare text content for embedding
        text_content = prepare_text_for_embedding(analysis)
        
        # Generate embeddings using official client
        embeddings_result = await openai_client.generate_embeddings(text_content)
        
        logging.info(f"Successfully generated embeddings for: {video_info.get('blob_name')}")
        return embeddings_result
        
    except Exception as e:
        logging.error(f"Error generating embeddings for video {video_info.get('blob_name')}: {str(e)}")
        raise Exception(f"Embeddings generation failed: {str(e)}")


def prepare_text_for_embedding(analysis: Dict[str, Any]) -> Dict[str, str]:
    """
    Prepare different types of text content from the video analysis for embedding.
    """
    insights = analysis.get('insights', {})
    
    # Combine transcript text
    transcript = insights.get('transcript', {})
    full_transcript = transcript.get('text', '')
    
    # Combine topics
    topics = insights.get('topics', [])
    topics_text = ' '.join([topic.get('name', '') for topic in topics])
    
    # Combine labels/tags
    labels = insights.get('labels', [])
    labels_text = ' '.join([label.get('name', '') for label in labels])
    
    # Combine scene descriptions
    scenes = insights.get('scenes', [])
    scenes_text = ' '.join([scene.get('description', '') for scene in scenes])
    
    # Combine keyframe descriptions
    keyframes = insights.get('keyframes', [])
    keyframes_text = ' '.join([kf.get('description', '') for kf in keyframes])
    
    return {
        "full_transcript": full_transcript,
        "topics": topics_text,
        "labels": labels_text,
        "scenes": scenes_text,
        "keyframes": keyframes_text,
        "combined_content": f"{full_transcript} {topics_text} {labels_text} {scenes_text} {keyframes_text}".strip()
    }


async def generate_openai_embeddings(endpoint: str, deployment: str, text_content: Dict[str, str]) -> Dict[str, Any]:
    """
    Generate embeddings using Azure OpenAI API.
    """
    # This is a placeholder for the actual Azure OpenAI API call
    # In a real implementation, you would:
    # 1. Use the Azure OpenAI Python SDK
    # 2. Call the embeddings endpoint for each text content
    # 3. Return the vector embeddings
    
    # For now, simulate the API call
    await asyncio.sleep(1)  # Simulate processing time
    
    return simulate_embeddings_generation({}, {}, {})


def simulate_embeddings_generation(video_info: Dict[str, Any], analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate embeddings generation for development purposes.
    """
    import random
    
    # Simulate 1536-dimensional embeddings (text-embedding-ada-002 standard)
    embedding_dimension = 1536
    
    def generate_mock_embedding() -> List[float]:
        return [random.uniform(-1, 1) for _ in range(embedding_dimension)]
    
    return {
        "embeddings": {
            "full_transcript": {
                "vector": generate_mock_embedding(),
                "dimension": embedding_dimension,
                "model": "text-embedding-ada-002"
            },
            "topics": {
                "vector": generate_mock_embedding(),
                "dimension": embedding_dimension,
                "model": "text-embedding-ada-002"
            },
            "labels": {
                "vector": generate_mock_embedding(),
                "dimension": embedding_dimension,
                "model": "text-embedding-ada-002"
            },
            "scenes": {
                "vector": generate_mock_embedding(),
                "dimension": embedding_dimension,
                "model": "text-embedding-ada-002"
            },
            "keyframes": {
                "vector": generate_mock_embedding(),
                "dimension": embedding_dimension,
                "model": "text-embedding-ada-002"
            },
            "combined_content": {
                "vector": generate_mock_embedding(),
                "dimension": embedding_dimension,
                "model": "text-embedding-ada-002"
            }
        },
        "text_content": {
            "full_transcript": "Bienvenidos a este vídeo tutorial sobre Azure Functions...",
            "topics": "Azure Functions Cloud Computing Video Processing Software Development",
            "labels": "azure functions cloud desarrollo tutorial",
            "scenes": "Introducción y presentación Explicación técnica Demostración práctica",
            "keyframes": "Pantalla de título Diagrama de arquitectura Código fuente",
            "combined_content": "Bienvenidos a este vídeo tutorial sobre Azure Functions... azure functions cloud desarrollo tutorial"
        },
        "processing_info": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "embedding_model": "text-embedding-ada-002",
            "total_embeddings": 6,
            "dimension": embedding_dimension,
            "status": "completed"
        }
    }