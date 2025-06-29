"""
Mixed-Model SceneSmith Three-Act Production Studio with Cost Tracking
"""

import logging
from dataclasses import dataclass, field
from typing import List
from crewai import Crew, Task
from agents.dramaturge import create_dramaturge
from agents.character_creator import create_character_creator
from agents.architect import create_architect
from agents.dialogue import create_dialogue_specialist
from agents.reviewer import create_reviewer
import os

logger = logging.getLogger(__name__)

@dataclass
class MixedModelOutput:
    """Container for Mixed-Model Production Studio outputs."""
    logline: str
    # ACT I: PRE-PRODUCTION (GPT-4 + Claude)
    structure_analysis: str = ""
    character_bible: str = ""
    # ACT II: PRODUCTION (GPT-4 + Claude)
    scene_outline: str = ""
    first_draft_dialogue: str = ""
    # ACT III: POST-PRODUCTION (Claude)
    final_screenplay: str = ""
    # PRODUCTION METADATA
    production_log: List[str] = field(default_factory=list)

class MixedModelSceneSmithCrew:
    """
    Mixed-Model Three-Act Production Studio:
    - GPT-4: Structure, Scene Architecture  
    - Claude: Character Psychology, Dialogue, Final Review
    """
    
    def __init__(self) -> None:
        """Initialize the Mixed-Model Production Studio."""
        logger.info("Initializing Mixed-Model Production Studio")
        
        try:
            # Verify API keys
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY not found")
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY not found")
            
            # ACT I: PRE-PRODUCTION 
            self.dramaturge = create_dramaturge()              # GPT-4 (structure)
            self.character_creator = create_character_creator() # Claude (psychology)
            
            # ACT II: PRODUCTION
            self.scene_architect = create_architect()          # GPT-4 (scene construction)
            self.dialogue_specialist = create_dialogue_specialist() # Claude (authentic dialogue)
            
            # ACT III: POST-PRODUCTION
            self.creative_reviewer = create_reviewer()         # Claude (AI detection & polish)
            
            # REMOVE: All cost_tracker references
            
            logger.info("Mixed-Model Production Studio initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Mixed-Model Studio: {e}")
            raise

    def generate_scene(self, logline: str) -> MixedModelOutput:
        """Generate scene using mixed AI models with cost tracking."""
        logger.info(f"Starting Mixed-Model Production for: {logline}")
        
        output = MixedModelOutput(logline=logline)
        
        try:
            # ===== ACT I: PRE-PRODUCTION =====
            logger.info("🎬 ACT I: PRE-PRODUCTION (GPT-4 + Claude)")
            
            # Task 1: Dramatic Structure (GPT-4)
            task_analyze = Task(
                description=f"""
                Analyze this logline for character contradiction opportunities: '{logline}'
                
                Identify where each character might have opposing conscious/unconscious desires.
                Set up the foundation for McKee's character development framework.
                """,
                agent=self.dramaturge,
                expected_output="Structural analysis with character contradiction opportunities."
            )
            
            # Task 2: Character Bible with Conscious/Unconscious Desires (Claude)
            task_character_bible = Task(
                description=f"""
                Create Character Bible using McKee's conscious/unconscious desire framework:
                
                {{task_analyze}}
                
                For each character, identify contradictory conscious and unconscious desires that create internal tension.
                """,
                agent=self.character_creator,
                expected_output="Character Bible with McKee's conscious/unconscious desire contradictions.",
                context=[task_analyze]
            )
            
            # ===== ACT II: PRODUCTION =====
            logger.info("🎬 ACT II: PRODUCTION (GPT-4 + Claude)")
            
            # Task 3: Scene Outline (GPT-4)
            task_scene_outline = Task(
                description=f"""
                Create a SINGLE scene outline (not multiple scenes) showing character contradictions in action:
                
                ORIGINAL LOGLINE: '{logline}'
                ANALYSIS: {{task_analyze}}
                CHARACTER BIBLE: {{task_character_bible}}
                
                REQUIREMENTS:
                - ONE scene only, taking place in the EXACT setting from the logline: '{logline}'
                - Use EXACT ages, location, and weather from the original logline
                - 3 paragraphs maximum (Setup, Escalation, Climax)
                - Show how conscious and unconscious desires create behavioral contradictions
                - Keep all action within the specified location
                - Focus on one dramatic moment, not a complete story
                """,
                agent=self.scene_architect,
                expected_output="Single scene outline (3 paragraphs) with character psychology driving action.",
                context=[task_analyze, task_character_bible]
            )
            
            # Task 4: Authentic Dialogue (Claude)  
            task_dialogue = Task(
                description=f"""
                Write dialogue where characters pursue conscious desires while unconscious desires leak through:
                
                CHARACTER BIBLE: {{task_character_bible}}
                SCENE OUTLINE: {{task_scene_outline}}
                
                CONSTRAINTS:
                - Maximum 8-12 lines of dialogue total
                - Single scene only (use the setting from the logline)
                - Focus on one key dramatic moment
                - Create authentic 60-year-old speech patterns with meaningful subtext.
                """,
                agent=self.dialogue_specialist,
                expected_output="8-12 lines of authentic dialogue revealing character contradictions.",
                context=[task_character_bible, task_scene_outline]
            )
            
            # ===== ACT III: POST-PRODUCTION =====
            logger.info("🎬 ACT III: POST-PRODUCTION (Claude)")
            
            # Task 5: AI Detection & Final Polish (Claude)
            task_final_scene = Task(
                description=f"""
                Eliminate AI-like writing and deliver production-ready screenplay:
                
                ORIGINAL LOGLINE: '{logline}'
                CHARACTER BIBLE: {{task_character_bible}}
                SCENE OUTLINE: {{task_scene_outline}}
                DIALOGUE: {{task_dialogue}}
                
                CRITICAL: Ensure final screenplay uses EXACT setting, ages, and details from original logline: '{logline}'
                
                Remove purple prose, clichés, and artificial patterns. Create authentic human behavior.
                """,
                agent=self.creative_reviewer,
                expected_output="Production-ready screenplay free of AI-writing patterns.",
                context=[task_character_bible, task_scene_outline, task_dialogue]
            )
            
            # Execute Mixed-Model Process
            tasks = [task_analyze, task_character_bible, task_scene_outline, task_dialogue, task_final_scene]
            
            crew = Crew(
                agents=[
                    self.dramaturge, 
                    self.character_creator, 
                    self.scene_architect, 
                    self.dialogue_specialist, 
                    self.creative_reviewer
                ],
                tasks=tasks,
                verbose=True
            )
            
            final_result = crew.kickoff()
            
            # Extract outputs
            output.structure_analysis = str(tasks[0].output)
            output.character_bible = str(tasks[1].output)
            output.scene_outline = str(tasks[2].output)
            output.first_draft_dialogue = str(tasks[3].output)
            output.final_screenplay = str(tasks[4].output)
            
            # Add cost tracking data
            output.production_log.append("Mixed-Model Production completed successfully")

            logger.info("Mixed-Model Production completed successfully")
            return output
                        
        except Exception as e:
            logger.error(f"Mixed-Model Production failed: {e}")
            output.production_log.append(f"Production failed: {str(e)}")
            raise