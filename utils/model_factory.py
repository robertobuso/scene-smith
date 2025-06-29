"""
Factory for creating different AI models with cost tracking.
"""

import os
import logging
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from utils.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)

class ModelFactory:
    """Factory for creating AI models with consistent configuration."""
    
    @staticmethod
    def create_openai_model(temperature: float = 0.4, max_tokens: int = 1500) -> ChatOpenAI:
        """Create OpenAI GPT model."""
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    @staticmethod
    def create_claude_model(temperature: float = 0.4, max_tokens: int = 1500) -> ChatAnthropic:
        """Create Anthropic Claude model."""
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

def create_tracked_agent(agent_class, agent_name: str, model_type: str, **kwargs) -> Any:
    """Create an agent with cost tracking wrapper."""
    
    # Select model based on type
    if model_type == "openai":
        llm = ModelFactory.create_openai_model(
            temperature=kwargs.get('temperature', 0.4),
            max_tokens=kwargs.get('max_tokens', 1500)
        )
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    elif model_type == "claude":
        llm = ModelFactory.create_claude_model(
            temperature=kwargs.get('temperature', 0.4),
            max_tokens=kwargs.get('max_tokens', 1500)
        )
        model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Create agent with selected model
    agent = agent_class(llm=llm, **{k:v for k,v in kwargs.items() if k not in ['temperature', 'max_tokens']})
    
    # Wrap the agent's _call method to track costs
    original_call = getattr(agent, '_call', None)
    if original_call:
        def tracked_call(inputs, *args, **kwargs):
            input_text = str(inputs)
            result = original_call(inputs, *args, **kwargs)
            output_text = str(result)
            cost_tracker.log_agent_cost(agent_name, model_name, input_text, output_text)
            return result
        
        setattr(agent, '_call', tracked_call)
    
    logger.info(f"✅ Created {agent_name} using {model_name}")
    return agent