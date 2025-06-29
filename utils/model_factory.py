"""
CrewAI-compatible model factory for OpenAI and Anthropic models.
"""

import os
import logging
from crewai import LLM

logger = logging.getLogger(__name__)

class ModelFactory:
    """Factory for creating CrewAI-compatible LLM instances."""
    
    @staticmethod
    def create_openai_llm(temperature: float = 0.4, max_tokens: int = 1500) -> LLM:
        """Create OpenAI LLM for CrewAI agents."""
        return LLM(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    @staticmethod
    def create_claude_llm(temperature: float = 0.4, max_tokens: int = 1500) -> LLM:
        """Create Anthropic Claude LLM for CrewAI agents."""
        return LLM(
            model=f"anthropic/{os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')}",
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )