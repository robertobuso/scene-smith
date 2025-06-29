"""
Memory utilities for SceneSmith using LangChain vector storage.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dataclasses import asdict

logger = logging.getLogger(__name__)

class SceneMemory:
    """Vector-based memory system for storing and retrieving scene information."""
    
    def __init__(self, persist_directory: Optional[str] = None) -> None:
        """Initialize the memory system with FAISS vector store."""
        self.persist_directory = persist_directory or os.getenv("MEMORY_PERSIST_DIR", "./scene_memory")
        self.enabled = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
        self.vectorstore: Optional[FAISS] = None
        
        if not self.enabled:
            logger.info("Memory system disabled by configuration")
            return
            
        try:
            self.embeddings = OpenAIEmbeddings()
            self._initialize_vectorstore()
        except Exception as e:
            logger.warning(f"Could not initialize memory system: {e}")
            self.enabled = False
    
    def _initialize_vectorstore(self) -> None:
        """Initialize or load existing vector store."""
        try:
            if os.path.exists(self.persist_directory):
                self.vectorstore = FAISS.load_local(
                    self.persist_directory, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded existing memory from {self.persist_directory}")
            else:
                # Create empty vectorstore with dummy document
                dummy_doc = Document(page_content="SceneSmith memory initialized", metadata={"type": "system"})
                self.vectorstore = FAISS.from_documents([dummy_doc], self.embeddings)
                logger.info("Created new memory system")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def store_scene(self, scene_meta: Any) -> None:
        """Store a scene in memory for future reference."""
        if not self.enabled or not self.vectorstore:
            return
        
        try:
            # Convert scene to document
            scene_dict = asdict(scene_meta) if hasattr(scene_meta, '__dict__') else scene_meta.__dict__
            
            content = f"""
            Logline: {scene_dict.get('logline', '')}
            Structure: {scene_dict.get('structure', '')}
            Outline: {scene_dict.get('scene_outline', '')}
            Dialogue: {scene_dict.get('dialogue', '')}
            Review: {scene_dict.get('review', '')}
            """
            
            doc = Document(
                page_content=content.strip(),
                metadata={
                    "type": "scene",
                    "logline": scene_dict.get('logline', ''),
                    "genre": self._extract_genre(scene_dict.get('structure', '')),
                    "retry_count": scene_dict.get('retry_count', 0)
                }
            )
            
            # Add to vectorstore
            self.vectorstore.add_documents([doc])
            
            # Persist changes
            self.vectorstore.save_local(self.persist_directory)
            logger.info("Scene stored successfully in memory")
            
        except Exception as e:
            logger.warning(f"Could not store scene in memory: {e}")
    
    def retrieve_similar_scenes(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve similar scenes based on query."""
        if not self.enabled or not self.vectorstore:
            return []
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            # Filter out system documents
            scene_docs = [doc for doc in docs if doc.metadata.get('type') == 'scene']
            logger.info(f"Retrieved {len(scene_docs)} similar scenes for query: {query}")
            return scene_docs
        except Exception as e:
            logger.warning(f"Could not retrieve from memory: {e}")
            return []
    
    def get_genre_examples(self, genre: str, k: int = 2) -> List[Document]:
        """Get examples of scenes from a specific genre."""
        if not self.enabled or not self.vectorstore:
            return []
        
        try:
            # Search for genre-specific content
            query = f"genre {genre} story structure character"
            docs = self.vectorstore.similarity_search(query, k=k*2)
            
            # Filter by genre metadata
            genre_docs = [
                doc for doc in docs 
                if doc.metadata.get('genre', '').lower() == genre.lower()
                and doc.metadata.get('type') == 'scene'
            ]
            
            logger.info(f"Retrieved {len(genre_docs)} examples for genre: {genre}")
            return genre_docs[:k]
        except Exception as e:
            logger.warning(f"Could not retrieve genre examples: {e}")
            return []
    
    def get_successful_patterns(self, k: int = 5) -> List[Document]:
        """Get scenes that were generated successfully without retries."""
        if not self.enabled or not self.vectorstore:
            return []
        
        try:
            # Get all scenes
            all_docs = self.vectorstore.similarity_search("scene structure dialogue", k=k*2)
            
            # Filter for successful scenes (low retry count)
            successful_docs = [
                doc for doc in all_docs 
                if doc.metadata.get('type') == 'scene' 
                and doc.metadata.get('retry_count', 0) <= 1
            ]
            
            logger.info(f"Retrieved {len(successful_docs)} successful scene patterns")
            return successful_docs[:k]
        except Exception as e:
            logger.warning(f"Could not retrieve successful patterns: {e}")
            return []
    
    def _extract_genre(self, structure_text: str) -> str:
        """Extract genre from structure analysis text."""
        genres = ['drama', 'comedy', 'thriller', 'horror', 'romance', 'action', 'sci-fi', 'fantasy', 'mystery', 'western']
        
        structure_lower = structure_text.lower()
        for genre in genres:
            if genre in structure_lower:
                return genre
        
        return 'drama'  # default
    
    def clear_memory(self) -> None:
        """Clear all stored scenes."""
        if not self.enabled:
            return
            
        try:
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory)
            self._initialize_vectorstore()
            logger.info("Memory cleared successfully")
        except Exception as e:
            logger.error(f"Could not clear memory: {e}")

# Global memory instance
scene_memory = SceneMemory()
