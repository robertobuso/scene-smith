"""
Creative Reviewer agent - Provides critique and improvement suggestions.
"""

import os
import logging
from crewai import Agent
from crewai.tools import SerperDevTool
from langchain_openai import ChatOpenAI
from utils.prompts import REVIEWER_PROMPTS

logger = logging.getLogger(__name__)

def create_reviewer() -> Agent:
    """Create the Creative Reviewer agent for scene critique."""
    
    try:
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("TEMPERATURE_REVIEWER", "0.3")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1200"))
        )
        
        agent = Agent(
            role="Creative Reviewer and Script Doctor",
            goal="Provide insightful critique on scene depth, originality, emotional resonance, and overall effectiveness",
            backstory=(
                "You are the 'Showrunner' of this writer's room and its ultimate 'Originality Enforcer.' "
                "You have a world-class eye for story and a deep intolerance for clichés. You believe the "
                "first draft is just the starting point. Your job is not just to critique, but to guide the "
                "creative team toward a more profound, unexpected, and emotionally resonant final product. "
                "You do this by providing sharp, actionable revision commands. You have the final say."
            ),
            verbose=True,
            allow_delegation=True,
            llm=llm,
            system_message=REVIEWER_PROMPTS["system_message"]
        )
        
        logger.info("Creative Reviewer agent created successfully")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create Creative Reviewer agent: {e}")
        raise
