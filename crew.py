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
            
            # Task 1: McKee Scene Analysis (not story analysis)
            task_analyze = Task(
                description=f"""
                Analyze this logline to identify ONE McKee-style scene: '{logline}'
                
                FOCUS ON SINGLE SCENE EXTRACTION:
                - Identify the specific moment of value transformation
                - Define opening and closing emotional states for main character
                - Outline 3-5 key beats that drive the change
                - Ensure scene fits 2-3 screenplay pages
                
                This is NOT a complete story analysis - focus on ONE transformative moment.
                """,
                agent=self.dramaturge,
                expected_output="McKee scene analysis identifying single value shift with beat structure."
            )
            
            # Task 2: Character Bible with Conscious/Unconscious Desires (Claude)
            task_character_bible = Task(
                description=f"""
                Create focused character profiles for the SINGLE SCENE:
                
                {{task_analyze}}
                
                For each character in this specific scene moment:
                - Conscious desire during this scene
                - Unconscious desire that creates internal conflict
                - How this contradiction manifests in behavior during the 2-3 page scene
                
                Focus only on character psychology relevant to this ONE scene transformation.
                """,
                agent=self.character_creator,
                expected_output="Character profiles focused on single scene's value shift dynamics.",
                context=[task_analyze]
            )
            
            # ===== ACT II: PRODUCTION =====
            logger.info("🎬 ACT II: PRODUCTION (GPT-4 + Claude)")
            
            # Task 3: Scene Outline (GPT-4)
            task_scene_outline = Task(
                description=f"""
                Create beat-by-beat outline for ONE scene (2-3 screenplay pages):
                
                ORIGINAL LOGLINE: '{logline}'
                SCENE ANALYSIS: {{task_analyze}}
                CHARACTER DYNAMICS: {{task_character_bible}}
                
                REQUIREMENTS:
                - Opening Beat: Character's initial value state
                - 3-5 Escalating Beats: Specific action/reaction exchanges
                - Turning Point Beat: Moment of value shift
                - Closing Beat: Character's new value state
                - Use EXACT setting from logline
                - Each beat must be specific, observable action
                """,
                agent=self.scene_architect,
                expected_output="McKee beat structure outline for single 2-3 page scene.",
                context=[task_analyze, task_character_bible]
            )
            
            # Task 4: Authentic Dialogue (Claude)  
            task_dialogue = Task(
                description=f"""
                Write dialogue for McKee scene transformation:
                
                BEAT STRUCTURE: {{task_scene_outline}}
                CHARACTER PSYCHOLOGY: {{task_character_bible}}
                
                CONSTRAINTS:
                - 15-25 lines of dialogue maximum (fits 2-3 screenplay pages)
                - Each line serves a specific beat in the value transformation
                - Age-appropriate speech for 60+ characters
                - Include essential action/parentheticals
                - Focus on the single value shift, not complete story
                """,
                agent=self.dialogue_specialist,
                expected_output="15-25 lines of dialogue driving single scene transformation.",
                context=[task_character_bible, task_scene_outline]
            )
            
            # ===== ACT III: POST-PRODUCTION =====
            logger.info("🎬 ACT III: POST-PRODUCTION (Claude)")
            
            # Task 5: AI Detection & Final Polish (Claude)
            task_final_scene = Task(
                description=f"""
                Create final screenplay ensuring McKee scene principles:
                
                ORIGINAL LOGLINE: '{logline}'
                SCENE STRUCTURE: {{task_scene_outline}}
                DIALOGUE: {{task_dialogue}}
                
                VERIFICATION CHECKLIST:
                - Clear value shift in main character
                - Proper beat structure driving change
                - 2-3 pages maximum in screenplay format
                - Eliminates AI writing patterns
                - Uses exact setting from logline
                
                OUTPUT: Complete, professionally formatted scene with FADE IN/FADE OUT.
                """,
                agent=self.creative_reviewer,
                expected_output="Professional 2-3 page screenplay scene with clear McKee structure.",
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