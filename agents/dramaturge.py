"""
Dramaturge agent - Expert in story structure and dramatic theory.
"""

import os
import logging
from crewai import Agent
from langchain_openai import ChatOpenAI
from utils.prompts import DRAMATURGE_PROMPTS

logger = logging.getLogger(__name__)

def create_dramaturge() -> Agent:
    """Create the Dramaturge agent for structural analysis."""
    
    try:
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("TEMPERATURE_DRAMATURGE", "0.3")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        )
        
        agent = Agent(
            role="Dramaturge and Story Structure Expert",
            goal="Analyze loglines and break them down into compelling dramatic structure using proven storytelling principles",
            backstory=(
                "You are a master dramaturge with deep expertise in Robert McKee's 'Story', "
                "Syd Field's three-act structure, Blake Snyder's 'Save the Cat', and Joseph Campbell's "
                "Hero's Journey. You dissect loglines to uncover their dramatic potential. "
                "You believe that a story is only as strong as its foundation, and your purpose is to "
                "provide a rock-solid structural analysis covering genre, conflict, and most importantly, "
                "the emotional stakes. You ensure every creative choice that follows is grounded in "
                "sound dramatic theory."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm,
            system_message=DRAMATURGE_PROMPTS["system_message"]
        )
        
        logger.info("Dramaturge agent created successfully")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create Dramaturge agent: {e}")
        raise
