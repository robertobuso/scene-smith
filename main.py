#!/usr/bin/env python3
"""
SceneSmith CLI - Autonomous AI Screenwriting Application
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from crew import SceneSmithCrew
from utils.logging_config import setup_logging

def setup_environment() -> bool:
    """Setup environment variables and logging."""
    load_dotenv()
    setup_logging()
    
    if not os.getenv("OPENAI_API_KEY"):
        logging.error("OPENAI_API_KEY not found in environment variables")
        print("Error: Please set your OPENAI_API_KEY environment variable.")
        print("Copy .env.example to .env and add your API key.")
        return False
    
    return True

def get_user_input() -> Optional[str]:
    """Get and validate logline input from user."""
    print("🎬 Welcome to SceneSmith - Autonomous Screenwriting Assistant")
    print("=" * 60)
    
    logline = input("\nEnter your logline: ").strip()
    
    if not logline:
        print("Error: Please provide a valid logline.")
        return None
    
    if len(logline) < 10:
        print("Warning: Very short logline. Consider adding more detail for better results.")
    
    return logline

def parse_final_output(final_text: str) -> dict:
    """Parses the structured output from the Creative Reviewer."""
    critique = "Critique not found."
    directive = "Directive not found."
    final_scene = final_text # Default to the full text

    try:
        if "### SHOWRUNNER'S CRITIQUE" in final_text:
            parts = final_text.split("### REVISION DIRECTIVE")
            critique_part = parts[0].replace("### SHOWRUNNER'S CRITIQUE", "").strip()
            
            scene_parts = parts[1].split("### FINAL SCENE")
            directive_part = scene_parts[0].strip()
            final_scene_part = scene_parts[1].strip()
            
            return {
                "critique": critique_part,
                "directive": directive_part,
                "final_scene": final_scene_part
            }
    except Exception:
        # If parsing fails, return the full text as the scene
        pass
        
    return {"critique": critique, "directive": directive, "final_scene": final_scene}


def display_results(result: dict) -> None:
    """Display formatted scene generation results, including the writer's room transcript."""
    print("\n" + "=" * 60)
    print("🎭 WRITER'S ROOM PROCESS & FINAL SCENE")
    print("=" * 60)
    
    # --- Displaying the Foundation Draft ---
    print("\n📋 Foundation: Structure Analysis")
    print("-" * 40)
    print(result.get('structure', 'Not available.'))
    
    print("\n🏗️ Foundation: Scene Outline")
    print("-" * 40)
    print(result.get('scene_outline', 'Not available.'))
    
    print("\n💬 Foundation: First Pass Dialogue")
    print("-" * 40)
    print(result.get('dialogue_first_pass', 'Not available.'))

    # --- Displaying the Showrunner's Collaboration ---
    print("\n" + "=" * 60)
    print("🤝 THE SHOWRUNNER'S REVIEW & REVISION")
    print("=" * 60)

    final_output_text = result.get('final_output_from_reviewer', 'Final output not found.')
    
    # Simple, robust parsing
    critique = "Critique not found."
    directive = "Directive not found."
    final_scene = final_output_text

    if "### FINAL SCENE" in final_output_text:
        # Split the text into critique/directive and the final scene
        parts = final_output_text.split("### FINAL SCENE", 1)
        review_part = parts[0]
        final_scene = parts[1].strip()

        if "### REVISION DIRECTIVE" in review_part:
            review_parts = review_part.split("### REVISION DIRECTIVE", 1)
            critique = review_parts[0].replace("### SHOWRUNNER'S CRITIQUE", "").strip()
            directive = review_parts[1].strip()
        else:
            critique = review_part.replace("### SHOWRUNNER'S CRITIQUE", "").strip()
    
    print("\n🔍 Showrunner's Critique:")
    print(f"'{critique}'\n")

    print("✍️ Revision Directive:")
    print(f"'{directive}'\n")

    print("🎬 Final Scene:")
    print("-" * 40)
    print(final_scene)
    
    print("\n" + "=" * 60)
    print("✅ Scene generation complete!")

def main() -> None:
    """Main CLI entry point for SceneSmith."""
    if not setup_environment():
        return
    
    logger = logging.getLogger(__name__)
    logger.info("Starting SceneSmith application")
    
    logline = get_user_input()
    if not logline:
        return
    
    print(f"\n🎯 Generating scene for: {logline}")
    print("-" * 60)
    
    try:
        # Initialize and run the crew
        crew = SceneSmithCrew()
        result = crew.generate_scene(logline)
        
        # Display results
        display_results(result)
        logger.info("Scene generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error generating scene: {str(e)}", exc_info=True)
        print(f"\n❌ Error generating scene: {str(e)}")
        print("Please check your OpenAI API key and try again.")
        print("Check the log file for detailed error information.")

if __name__ == "__main__":
    main()

#crew.py
"""
CrewAI orchestration for SceneSmith agents and tasks.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from crewai import Crew, Task
from agents.dramaturge import create_dramaturge
from agents.architect import create_architect
from agents.dialogue import create_dialogue_specialist
from agents.reviewer import create_reviewer
from utils.memory import scene_memory

logger = logging.getLogger(__name__)

@dataclass
class SceneMeta:
    """Container for scene generation outputs."""
    logline: str
    structure: str = ""
    scene_outline: str = ""
    dialogue: str = ""
    review: str = ""
    revision_notes: str = ""
    retry_count: int = 0
    communication_log: List[str] = field(default_factory=list)

class SceneSmithCrew:
    """Orchestrates the SceneSmith writing crew with enhanced communication."""
    
    def __init__(self) -> None:
        """Initialize agents and crew."""
        logger.info("Initializing SceneSmith crew")
        
        try:
            self.dramaturge = create_dramaturge()
            self.architect = create_architect()
            self.dialogue_specialist = create_dialogue_specialist()
            self.reviewer = create_reviewer()
            
            # Create crew with agents
            self.crew = Crew(
                agents=[
                    self.dramaturge,
                    self.architect,
                    self.dialogue_specialist,
                    self.reviewer
                ],
                verbose=True
            )
            
            self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
            logger.info("SceneSmith crew initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize crew: {e}")
            raise
    
    def _validate_structure(self, structure: str) -> tuple[bool, str]:
        """Validate if structure analysis meets quality standards."""
        issues = []
        
        if len(structure) < 100:
            issues.append("Structure analysis too brief")
        
        required_elements = ['genre', 'conflict', 'stakes', 'protagonist']
        missing_elements = [elem for elem in required_elements 
                          if elem.lower() not in structure.lower()]
        
        if missing_elements:
            issues.append(f"Missing elements: {', '.join(missing_elements)}")
        
        if 'stakes' not in structure.lower() or len([line for line in structure.split('\n') if 'stakes' in line.lower()]) == 0:
            issues.append("Stakes not clearly defined")
        
        return len(issues) == 0, "; ".join(issues)
    
    def _request_clarification(self, from_agent: str, to_agent: str, question: str) -> str:
        """Simulate agent-to-agent communication for clarification."""
        logger.info(f"Agent communication: {from_agent} asking {to_agent}: {question}")
        
        # Create a clarification task
        clarification_task = Task(
            description=f"Clarification request from {from_agent}: {question}",
            agent=getattr(self, to_agent.lower().replace(' ', '_')),
            expected_output="A clear, specific response to the clarification request."
        )
        
        try:
            # Execute single clarification task
            temp_crew = Crew(agents=[getattr(self, to_agent.lower().replace(' ', '_'))], verbose=False)
            temp_crew.tasks = [clarification_task]
            result = temp_crew.kickoff()
            
            response = result.raw if hasattr(result, 'raw') else str(result)
            logger.info(f"Clarification response from {to_agent}: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.warning(f"Clarification request failed: {e}")
            return "Unable to get clarification at this time."
    
    def generate_scene(self, logline: str) -> SceneMeta:
        """Generate a complete scene from a logline with retry logic."""
        logger.info(f"Starting scene generation for logline: {logline}")
        
        scene_meta = SceneMeta(logline=logline)
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scene generation attempt {attempt + 1}/{self.max_retries}")
                scene_meta.retry_count = attempt
                
                # Task 1: Dramatic structure analysis
                structure_task = Task(
                    description=(
                        f"Analyze this logline and provide dramatic structure: '{logline}'\n"
                        "Break down genre, protagonist conflict, stakes, tone, and key dramatic beats. "
                        "Apply McKee, Field, Save the Cat, and Hero's Journey principles. "
                        "Be specific about stakes and what the protagonist stands to lose."
                    ),
                    agent=self.dramaturge,
                    expected_output="A detailed structural analysis with genre, conflict, stakes, and dramatic beats."
                )
                
                # Execute structure task first to validate
                self.crew.tasks = [structure_task]
                structure_result = self.crew.kickoff()
                structure_output = structure_result.raw if hasattr(structure_result, 'raw') else str(structure_result)
                
                # Validate structure quality
                is_valid, validation_message = self._validate_structure(structure_output)
                
                if not is_valid and attempt < self.max_retries - 1:
                    logger.warning(f"Structure validation failed: {validation_message}")
                    scene_meta.communication_log.append(f"Attempt {attempt + 1}: Structure validation failed - {validation_message}")
                    
                    # Request clarification from dramaturge
                    clarification = self._request_clarification(
                        "Scene Architect", 
                        "Dramaturge",
                        f"The structure analysis needs improvement: {validation_message}. Please provide more detail on stakes and conflict."
                    )
                    scene_meta.communication_log.append(f"Clarification requested: {clarification[:100]}...")
                    continue
                
                scene_meta.structure = structure_output
                
                # Task 2: Scene outline creation
                outline_task = Task(
                    description=(
                        "Using the dramatic structure analysis, create a compelling 3-paragraph scene outline. "
                        "Include vivid setting details, character actions, and escalating conflict. "
                        "Focus on visual storytelling and emotional beats. Each paragraph should build tension."
                    ),
                    agent=self.architect,
                    expected_output="A 3-paragraph scene outline with setting, action, and conflict progression.",
                    context=[structure_task]
                )
                
                # Task 3: Dialogue generation
                dialogue_task = Task(
                    description=(
                        "Transform the scene outline into 8-12 lines of compelling dialogue. "
                        "Ensure each character has a distinct voice, include subtext, and maintain dramatic tension. "
                        "Use proper screenplay format with character names and dialogue. "
                        "Make sure dialogue serves both character development and plot advancement."
                    ),
                    agent=self.dialogue_specialist,
                    expected_output="8-12 lines of character-driven dialogue in proper screenplay format.",
                    context=[outline_task]
                )
                
                # Task 4: Creative review
                review_task = Task(
                    description=(
                        "Review the complete scene (outline + dialogue) for depth, originality, and emotional resonance. "
                        "Analyze character development, pacing, tension, and overall effectiveness. "
                        "Provide specific critique and improvement suggestions. "
                        "If significant issues exist, recommend specific revisions."
                    ),
                    agent=self.reviewer,
                    expected_output="Detailed critique with specific feedback and improvement suggestions.",
                    context=[outline_task, dialogue_task]
                )
                
                # Execute remaining tasks
                self.crew.tasks = [outline_task, dialogue_task, review_task]
                results = self.crew.kickoff()
                
                # Extract results
                scene_meta.scene_outline = outline_task.output.raw if hasattr(outline_task.output, 'raw') else str(outline_task.output)
                scene_meta.dialogue = dialogue_task.output.raw if hasattr(dialogue_task.output, 'raw') else str(dialogue_task.output)
                scene_meta.review = review_task.output.raw if hasattr(review_task.output, 'raw') else str(review_task.output)
                
                # Check if reviewer suggests major revisions
                if "major revision" in scene_meta.review.lower() or "significant issues" in scene_meta.review.lower():
                    if attempt < self.max_retries - 1:
                        logger.info("Reviewer suggests major revisions, attempting retry...")
                        scene_meta.communication_log.append(f"Attempt {attempt + 1}: Reviewer suggested major revisions")
                        continue
                
                # Store successful scene in memory
                try:
                    scene_memory.store_scene(scene_meta)
                    logger.info("Scene stored in memory successfully")
                except Exception as e:
                    logger.warning(f"Failed to store scene in memory: {e}")
                
                scene_meta.revision_notes = f"Generated successfully on attempt {attempt + 1}"
                logger.info(f"Scene generation completed successfully on attempt {attempt + 1}")
                return scene_meta
                
            except Exception as e:
                logger.error(f"Scene generation attempt {attempt + 1} failed: {e}")
                scene_meta.communication_log.append(f"Attempt {attempt + 1}: Error - {str(e)}")
                
                if attempt == self.max_retries - 1:
                    raise Exception(f"Scene generation failed after {self.max_retries} attempts: {e}")
        
        return scene_meta
