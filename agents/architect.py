"""
Scene Architect agent - Creates detailed scene outlines and visual storytelling.
"""

import os
import logging
from crewai import Agent
from langchain_openai import ChatOpenAI
from utils.prompts import ARCHITECT_PROMPTS

logger = logging.getLogger(__name__)

def create_architect() -> Agent:
    """Create the Scene Architect agent for scene construction."""
    
    try:
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("TEMPERATURE_ARCHITECT", "0.4")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1200"))
        )
        
        agent = Agent(
            role="Scene Architect and Visual Storyteller",
            goal="Transform dramatic structure into vivid, cinematic scene outlines with rich setting details and escalating action",
            backstory=(
                "You are a master of visual storytelling, a disciple of the 'show, don't tell' philosophy. "
                "You believe the environment is a character in itself. Your primary directive is to honor "
                "every detail from the logline and the Dramaturge's analysis, treating them as sacred text. "
                "You build worlds by layering sensory details: the sound of rain on a tin roof, the smell "
                "of salt on a wet beach, the visual chaos of a crowd. You choreograph character actions "
                "to reveal their internal state—a nervous fumble, a defiant stance, a comforting gesture."
            ),
            verbose=True,
            tools=[],
            allow_delegation=False,
            llm=llm,
            system_message=ARCHITECT_PROMPTS["system_message"]
        )
        
        logger.info("Scene Architect agent created successfully")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create Scene Architect agent: {e}")
        raise
