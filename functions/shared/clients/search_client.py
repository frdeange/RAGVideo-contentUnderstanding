"""
Azure Cognitive Search client using official Azure SDK.
Handles document indexing and semantic search operations.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
import json
from datetime import datetime


class AzureSearchClient:
    """Client for Azure Cognitive Search using official Azure SDK."""
    
    def __init__(self):
        """Initialize the Azure Search client."""
        self.endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
        self.index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME", "videos")
        self.admin_key = os.environ.get("AZURE_SEARCH_ADMIN_KEY")
        
        # Setup clients
        self._setup_clients()
    
    def _setup_clients(self):
        """Set up Azure Search clients with proper authentication."""
        if not self.endpoint:
            raise ValueError("AZURE_SEARCH_ENDPOINT not configured")
        
        try:
            if self.admin_key:
                # Use API key authentication
                credential = AzureKeyCredential(self.admin_key)
                logging.info("Azure Search client configured with admin key")
            else:
                # Use managed identity authentication
                credential = DefaultAzureCredential()
                logging.info("Azure Search client configured with managed identity")
            
            # Initialize clients
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=credential
            )
            
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=credential
            )
            
        except Exception as e:
            logging.error(f"Failed to setup Azure Search clients: {e}")
            raise
    
    def upload_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a single document to the search index.
        
        Args:
            document: Document to upload
            
        Returns:
            Upload result
        """
        return self.upload_documents([document])
    
    def upload_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Upload multiple documents to the search index.
        
        Args:
            documents: List of documents to upload
            
        Returns:
            Batch upload result
        """
        try:
            # Upload documents using the official client
            result = self.search_client.upload_documents(documents=documents)
            
            # Process results
            successful_count = 0
            failed_docs = []
            
            for doc_result in result:
                if doc_result.succeeded:
                    successful_count += 1
                else:
                    failed_docs.append({
                        "key": doc_result.key,
                        "error": doc_result.error_message
                    })
            
            if failed_docs:
                logging.warning(f"Some documents failed to upload: {failed_docs}")
            
            logging.info(f"Successfully uploaded {successful_count}/{len(documents)} documents")
            
            return {
                "successful_count": successful_count,
                "failed_count": len(failed_docs),
                "failed_documents": failed_docs,
                "status": "completed"
            }
            
        except Exception as e:
            logging.error(f"Error uploading documents: {e}")
            raise
    
    def search_documents(
        self, 
        query: str, 
        filters: Optional[str] = None,
        top: int = 10,
        select_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search documents in the index.
        
        Args:
            query: Search query text
            filters: OData filter expression
            top: Number of results to return
            select_fields: Specific fields to return
            
        Returns:
            Search results
        """
        try:
            # Perform search using official client
            results = self.search_client.search(
                search_text=query,
                filter=filters,
                top=top,
                select=select_fields
            )
            
            # Convert results to list
            documents = []
            for result in results:
                documents.append(dict(result))
            
            logging.info(f"Search completed: {len(documents)} results for query '{query}'")
            
            return {
                "value": documents,
                "count": len(documents)
            }
            
        except Exception as e:
            logging.error(f"Error searching documents: {e}")
            raise
    
    def semantic_search(
        self, 
        query: str, 
        embedding_vector: Optional[List[float]] = None,
        filters: Optional[str] = None,
        top: int = 10,
        select_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform semantic search using vector similarity.
        
        Args:
            query: Search query text
            embedding_vector: Query embedding vector for semantic search
            filters: OData filter expression
            top: Number of results to return
            select_fields: Specific fields to return
            
        Returns:
            Semantic search results
        """
        try:
            search_kwargs = {
                "search_text": query,
                "filter": filters,
                "top": top,
                "select": select_fields
            }
            
            # Add vector search if embedding provided
            if embedding_vector:
                vector_query = VectorizedQuery(
                    vector=embedding_vector,
                    k_nearest_neighbors=top,
                    fields="transcript_vector,topics_vector,scenes_vector"
                )
                search_kwargs["vector_queries"] = [vector_query]
            
            # Perform search
            results = self.search_client.search(**search_kwargs)
            
            # Convert results to list
            documents = []
            for result in results:
                documents.append(dict(result))
            
            logging.info(f"Semantic search completed: {len(documents)} results")
            
            return {
                "value": documents,
                "count": len(documents)
            }
            
        except Exception as e:
            logging.error(f"Error in semantic search: {e}")
            raise
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Document data or None if not found
        """
        try:
            result = self.search_client.get_document(key=document_id)
            
            logging.info(f"Retrieved document: {document_id}")
            return dict(result)
            
        except Exception as e:
            if "Not Found" in str(e):
                return None
            logging.error(f"Error getting document: {e}")
            raise
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document from the index.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Deletion result
        """
        try:
            # Delete using official client
            documents_to_delete = [{"id": document_id}]
            result = self.search_client.delete_documents(documents=documents_to_delete)
            
            # Check result
            success = result[0].succeeded if result else False
            
            if success:
                logging.info(f"Document deleted: {document_id}")
            else:
                error_msg = result[0].error_message if result else "Unknown error"
                logging.error(f"Failed to delete document {document_id}: {error_msg}")
            
            return {
                "document_id": document_id,
                "success": success,
                "error": result[0].error_message if result and not success else None
            }
            
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            raise


# Global instance for reuse
_search_client_instance = None

def get_search_client() -> AzureSearchClient:
    """Get a singleton instance of the Azure Search client."""
    global _search_client_instance
    if _search_client_instance is None:
        _search_client_instance = AzureSearchClient()
    return _search_client_instance