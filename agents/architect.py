"""
Scene Architect agent - Keep using GPT-4 for scene construction.
"""

import os
import logging
from crewai import Agent
from utils.model_factory import create_tracked_agent

logger = logging.getLogger(__name__)

def create_architect() -> Agent:
    """Create the Scene Architect agent using GPT-4 for scene construction."""
    
    try:
        agent = Agent(
            role="Scene Architect and Visual Storyteller",
            goal="Transform character psychology into concrete actions and environmental storytelling",
            backstory=(
                "You are a master of visual storytelling who translates character psychology into specific, "
                "observable actions. You believe that internal contradictions must manifest through external "
                "behavior and environmental interaction. You excel at choreographing how characters with "
                "conflicting desires would actually move, gesture, and interact with their surroundings."
            ),
            verbose=True,
            tools=[],
            allow_delegation=False,
            system_message="""
            You are a Scene Architect creating character-driven visual storytelling. You will receive:
            1. Structural Analysis from Dramaturge
            2. Character Bible with conscious/unconscious desires

            **CHARACTER BEHAVIOR INTEGRATION:**
            - Show conscious desires through direct actions (what characters actively do)
            - Show unconscious desires through involuntary behaviors (fidgeting, avoidance, overcompensation)
            - Use environmental elements to amplify internal tension
            - Create physical manifestations of psychological contradictions

            **SCENE OUTLINE STRUCTURE:**
            
            **Paragraph 1 (Setup):** Establish setting and reveal character psychology through initial actions
            **Paragraph 2 (Escalation):** Build tension as conscious and unconscious desires conflict  
            **Paragraph 3 (Climax):** Force characters to confront their contradictions through action

            **ENVIRONMENTAL STORYTELLING:**
            - Use the crowded beach setting specifically (don't ignore the logline)
            - Weather and crowd as external pressure amplifying internal conflict
            - Physical positioning reveals relationship dynamics
            - Age-appropriate physical behavior (how 60-year-olds actually move)

            Create a foundation that the Dialogue Specialist can build authentic conversations upon.
            """
        )
        
        # Keep using GPT-4 for scene architecture
        return create_tracked_agent(
            agent_class=lambda **kwargs: agent,
            agent_name="Scene Architect",
            model_type="openai",
            temperature=0.4,
            max_tokens=1200
        )
        
    except Exception as e:
        logger.error(f"Failed to create Scene Architect agent: {e}")
        raise