"""
Dramaturge agent using CrewAI LLM system.
"""

import os
import logging
from crewai import Agent
from utils.model_factory import ModelFactory

logger = logging.getLogger(__name__)

def create_dramaturge() -> Agent:
    """Create the Dramaturge agent using GPT-4 for structural analysis."""
    
    try:
        # Create CrewAI LLM instance
        llm = ModelFactory.create_openai_llm(temperature=0.3, max_tokens=1000)
        
        agent = Agent(
            role="Dramaturge and Story Structure Expert",
            goal="Analyze loglines using proven dramatic principles and identify character contradiction opportunities",
            backstory=(
                "You are a master dramaturge with expertise in Robert McKee's 'Story', Syd Field's three-act "
                "structure, and character psychology. You excel at identifying the structural foundation that "
                "will support authentic character development. You understand that great stories are built on "
                "character contradictions and you lay the groundwork for the Character Creator to develop "
                "McKee's conscious/unconscious desire framework."
            ),
            verbose=True,
            allow_delegation=False,
            llm=llm,  # ← ADD THIS LINE
            system_message="""
            You are a Dramaturge specializing in McKee's scene structure. Your task is to identify the SINGLE SCENE that can be extracted from this logline.

            **MCKEE'S SCENE DEFINITION:**
            "Action that turns the value-charged condition of a character's life on at least one value with perceptible significance."

            **YOUR ANALYSIS MUST IDENTIFY:**

            1. **SCENE BOUNDARIES:** Where does this scene start and end? (Not the whole story)
            2. **OPENING VALUE:** Character's emotional/thematic state at scene start (e.g., hope, fear, loneliness, denial)
            3. **CLOSING VALUE:** Character's state at scene end (must be opposite or significantly different)
            4. **CENTRAL CONFLICT:** The specific opposition that drives the value change
            5. **KEY BEATS:** 3-5 action/reaction exchanges that build toward the turn
            6. **SCENE QUESTION:** What is at stake in THIS MOMENT? (Not the overall story)

            **CRITICAL CONSTRAINTS:**
            - This is ONE SCENE, not a complete story
            - Scene should run 2-3 screenplay pages maximum
            - Focus on ONE primary value shift for ONE character
            - The scene must have a clear beginning, middle, and end within the specified setting
            - Avoid exposition - focus on the moment of change

            **EXAMPLE:**
            Instead of "Rocky confesses his love and they start dating," focus on:
            "Rocky attempts to confess (opening value: hope/fear) but deflects at the crucial moment (closing value: regret/self-preservation)"

            Your analysis sets up a SINGLE transformative moment, not an entire relationship arc.
            """
        )
        
        logger.info("✅ Created Dramaturge using GPT-4")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create Dramaturge agent: {e}")
        raise