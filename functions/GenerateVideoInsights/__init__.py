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
    Generate final insights and summary for the processed video.
    
    This activity function creates intelligent summaries, key takeaways,
    and actionable insights from the video analysis using Azure OpenAI.
    """
    video_info = input_data.get('video_info', {})
    metadata = input_data.get('metadata', {})
    analysis = input_data.get('analysis', {})
    search_document_id = input_data.get('search_document_id', '')
    
    logging.info(f"Generating final insights for video: {video_info.get('blob_name')}")
    
    try:
        # Get Azure OpenAI client
        openai_client = get_openai_client()
        
        # Check if we have proper configuration
        if not os.environ.get("AZURE_OPENAI_ENDPOINT"):
            # For development, return simulated insights
            logging.info("No OpenAI chat endpoint configured, returning simulated insights")
            return simulate_insights_generation(video_info, metadata, analysis, search_document_id)
        
        # Prepare context for insights generation
        insights_context = prepare_insights_context(video_info, metadata, analysis)
        
        # Generate insights using official OpenAI client
        insights_result = await openai_client.generate_video_insights(insights_context)
        
        logging.info(f"Successfully generated insights for: {video_info.get('blob_name')}")
        return {
            "video_info": video_info,
            "search_document_id": search_document_id,
            "insights": insights_result,
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error generating insights for video {video_info.get('blob_name')}: {str(e)}")
        raise Exception(f"Insights generation failed: {str(e)}")


def prepare_insights_context(video_info: Dict[str, Any], metadata: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare context information for AI insights generation.
    """
    insights = analysis.get('insights', {})
    
    return {
        "video_name": video_info.get('blob_name', ''),
        "duration_minutes": round(metadata.get('video_properties', {}).get('duration_seconds', 0) / 60, 1),
        "file_size_mb": metadata.get('file_info', {}).get('size_mb', 0),
        "transcript": insights.get('transcript', {}).get('text', ''),
        "topics": [topic.get('name', '') for topic in insights.get('topics', [])[:10]],  # Top 10 topics
        "labels": [label.get('name', '') for label in insights.get('labels', [])[:15]],  # Top 15 labels
        "scenes_count": len(insights.get('scenes', [])),
        "faces_detected": len(insights.get('faces', [])),
        "keyframes_count": len(insights.get('keyframes', [])),
        "language": insights.get('transcript', {}).get('language', 'Unknown')
    }


async def generate_ai_insights(endpoint: str, deployment: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights using Azure OpenAI Chat API.
    """
    # This is a placeholder for the actual Azure OpenAI API call
    # In a real implementation, you would:
    # 1. Use the Azure OpenAI Python SDK
    # 2. Create a chat completion request with context
    # 3. Parse and structure the AI response
    
    # For now, simulate the API call
    await asyncio.sleep(2)  # Simulate processing time
    
    return simulate_insights_generation({}, {}, {}, "mock_document_id")


def simulate_insights_generation(
    video_info: Dict[str, Any], 
    metadata: Dict[str, Any], 
    analysis: Dict[str, Any], 
    search_document_id: str
) -> Dict[str, Any]:
    """
    Simulate AI insights generation for development purposes.
    """
    return {
        "summary": {
            "title": "Tutorial de Azure Functions y Procesamiento de Vídeo",
            "short_description": "Un tutorial completo sobre cómo implementar soluciones de procesamiento de vídeo usando Azure Functions y servicios de IA.",
            "key_points": [
                "Introducción a Azure Functions para procesamiento asíncrono",
                "Integración con Azure AI Video Indexer para análisis automático",
                "Implementación de arquitectura serverless escalable",
                "Mejores prácticas para manejo de archivos multimedia en la nube"
            ],
            "target_audience": "Desarrolladores interesados en soluciones cloud y procesamiento multimedia",
            "complexity_level": "Intermedio",
            "estimated_learning_time_minutes": 25
        },
        "content_analysis": {
            "primary_topics": [
                {"topic": "Azure Functions", "relevance": 0.95, "coverage_percentage": 65},
                {"topic": "Video Processing", "relevance": 0.90, "coverage_percentage": 45},
                {"topic": "Cloud Architecture", "relevance": 0.85, "coverage_percentage": 35},
                {"topic": "AI Services", "relevance": 0.80, "coverage_percentage": 30}
            ],
            "content_type": "Educational/Tutorial",
            "presentation_style": "Technical demonstration with code examples",
            "visual_elements": [
                "Architecture diagrams",
                "Code snippets in VS Code", 
                "Azure portal interface",
                "Live coding sessions"
            ]
        },
        "engagement_metrics": {
            "estimated_engagement_score": 0.82,
            "content_density": "High",
            "pace": "Moderate",
            "technical_depth": "Detailed with practical examples",
            "accessibility": {
                "language_clarity": 0.88,
                "visual_support": 0.85,
                "code_readability": 0.90
            }
        },
        "actionable_insights": {
            "recommended_tags": [
                "azure-functions", "video-processing", "serverless", 
                "ai-video-indexer", "cloud-architecture", "tutorial"
            ],
            "suggested_follow_up_content": [
                "Advanced Azure Functions patterns",
                "Performance optimization for video processing",
                "Cost management in serverless video solutions",
                "Integration with other Azure AI services"
            ],
            "learning_objectives": [
                "Understand Azure Functions architecture",
                "Implement video processing workflows", 
                "Configure AI service integrations",
                "Deploy scalable multimedia solutions"
            ]
        },
        "technical_metadata": {
            "complexity_indicators": {
                "code_complexity": "Intermediate",
                "architecture_complexity": "Advanced",
                "deployment_complexity": "Intermediate"
            },
            "prerequisites": [
                "Basic Azure knowledge",
                "Python programming experience",
                "Understanding of cloud concepts",
                "Familiarity with REST APIs"
            ],
            "technologies_covered": [
                "Azure Functions", "Azure AI Video Indexer", 
                "Azure Blob Storage", "Azure Cognitive Search",
                "Python", "JSON", "REST APIs"
            ]
        },
        "search_optimization": {
            "optimized_title": "Azure Functions Video Processing: Complete Tutorial with AI Analysis",
            "meta_description": "Learn to build scalable video processing solutions using Azure Functions, AI Video Indexer, and serverless architecture. Includes code examples and best practices.",
            "search_keywords": [
                "azure functions tutorial", "video processing cloud", 
                "ai video analysis", "serverless multimedia", 
                "azure video indexer", "python azure functions"
            ],
            "content_categories": ["Tutorial", "Azure", "Video Processing", "AI", "Serverless"]
        },
        "processing_info": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "ai_model": "gpt-4",
            "insights_version": "1.0",
            "search_document_id": search_document_id,
            "confidence_score": 0.89,
            "status": "completed"
        }
    }