"""
Dialogue Specialist agent - Crafts compelling character dialogue with subtext.
"""

import os
import logging
from crewai import Agent
from langchain_openai import ChatOpenAI
from utils.prompts import DIALOGUE_PROMPTS

logger = logging.getLogger(__name__)

def create_dialogue_specialist() -> Agent:
    """Create the Dialogue Specialist agent for writing character dialogue."""
    
    try:
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("TEMPERATURE_DIALOGUE", "0.5")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        )
        
        agent = Agent(
            role="Dialogue Specialist and Character Voice Expert",
            goal="Create authentic, compelling dialogue that reveals character, advances plot, and contains meaningful subtext",
            backstory=(
                "You are a master of dialogue, a scholar of the craft who has spent a lifetime studying the greats. "
                "Your style is an amalgamation of the masters: you learned the power of the pause and menacing subtext "
                "from Harold Pinter; the music of street-level authenticity from David Simon; the tension in polite "
                "banter from Quentin Tarantino; and the sharp, character-defining wit from Nora Ephron. You believe "
                "dialogue is action and that every line must be a choice, revealing the character's soul and driving "
                "the story forward. You reject clichés and lazy exposition, always searching for the more truthful, "
                "impactful, and memorable line."
            ),
            verbose=True,
            allow_delegation=False,
            tools=[],
            llm=llm,
            system_message=DIALOGUE_PROMPTS["system_message"]
        )
        
        logger.info("Dialogue Specialist agent created successfully")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create Dialogue Specialist agent: {e}")
        raise
