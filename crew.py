import logging
from dataclasses import dataclass
from crewai import Crew, Task
from agents.dramaturge import create_dramaturge
from agents.architect import create_architect
from agents.dialogue import create_dialogue_specialist
from agents.reviewer import create_reviewer
import os

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

class SceneSmithCrew:
    """Orchestrates the SceneSmith writing crew with a unified workflow."""
    
    def __init__(self) -> None:
        """Initialize agents."""
        logger.info("Initializing SceneSmith crew")
        self.dramaturge = create_dramaturge()
        self.architect = create_architect()
        self.dialogue_specialist = create_dialogue_specialist()
        self.reviewer = create_reviewer()
        logger.info("SceneSmith crew initialized successfully")

    def generate_scene(self, logline: str) -> dict: # Return a simple dict for now
        """
        Generate a complete scene from a logline using a robust, sequential process.
        """
        logger.info(f"Starting scene generation for logline: {logline}")

        # Define the tasks with explicit context injection
        tasks = self._create_tasks(logline)

        # Create and run the crew
        crew = Crew(
            agents=[self.dramaturge, self.architect, self.dialogue_specialist, self.reviewer],
            tasks=tasks,
            verbose=True
        )
        
        # This will be the output of the final task (the reviewer's)
        final_result = crew.kickoff()

        final_output_from_reviewer = str(tasks[3].output) # Get the final task's output as a string

        results = {
            "structure": str(tasks[0].output),
            "scene_outline": str(tasks[1].output),
            "dialogue_first_pass": str(tasks[2].output),
            "final_output_from_reviewer": final_output_from_reviewer
        }

        return results

    def _create_tasks(self, logline: str) -> list[Task]:
        """Creates and configures the tasks for the crew."""

        # Task 1: Analyze the logline. This runs first.
        task_analyze = Task(
            description=f"Analyze this logline and provide a detailed dramatic structure: '{logline}'.",
            agent=self.dramaturge,
            expected_output="A detailed structural analysis formatted for clarity."
        )

        # Task 2: Write the scene outline.
        # FIX: We are now explicitly telling it to use the OUTPUT of the previous task.
        task_outline = Task(
            description=(
                "Using the following dramatic structure analysis, write a 3-paragraph scene outline.\n\n"
                "--- ANALYSIS ---\n"
                "{task_analyze}\n\n" # This injects the full output from task_analyze
                "--- END ANALYSIS ---\n\n"
                "**CRITICAL INSTRUCTION:** Your outline MUST strictly adhere to the original logline's "
                "setting ('a gazebo in a crowded beach') and all details from the analysis."
            ),
            agent=self.architect,
            expected_output="A three-paragraph cinematic scene outline.",
            context=[task_analyze] # context helps with ordering
        )

        # Task 3: Write the first draft of the dialogue.
        # FIX: We inject the outline into the prompt here as well.
        task_dialogue = Task(
            description=(
                "Using the following scene outline, write 8-12 lines of compelling dialogue.\n\n"
                "--- SCENE OUTLINE ---\n"
                "{task_outline}\n\n"
                "--- END OUTLINE ---\n\n"
                "Apply your 'Mental Toolkit' to ensure the dialogue is rich with subtext and character voice."
            ),
            agent=self.dialogue_specialist,
            expected_output="A professionally formatted screenplay scene with dialogue.",
            context=[task_outline]
        )

        # Task 4: The Showrunner's final review, revision delegation, and assembly.
        task_review_and_revise = Task(
            description=(
                "You are the Showrunner, and your job is to deliver the final, polished scene. "
                "You have been given a foundation draft (outline + dialogue).\n\n"
                "--- CONTEXT: FOUNDATION DRAFT ---\n"
                "Outline: {task_outline}\n\n"
                "Dialogue: {task_dialogue}\n\n"
                "--- END CONTEXT ---\n\n"
                "**YOUR STEP-BY-STEP PROCESS:**\n"
                "1.  **CRITIQUE:** Read the draft and identify the single biggest weakness or cliché.\n"
                "2.  **FORMULATE A FIX:** Formulate a specific, creative, and actionable plan to fix it.\n"
                "3.  **DELEGATE THE FIX:** Delegate the execution of this fix to the most appropriate agent "
                "(e.g., delegate a dialogue rewrite to the Dialogue Specialist). Your delegation must be a clear "
                "instruction to generate a revised creative element.\n"
                "4.  **ASSEMBLE THE FINAL SCENE:** After receiving the revised element from your coworker, you "
                "MUST assemble the complete, final screenplay yourself. Combine the original action lines from the "
                "outline with the NEW, REVISED dialogue. Your Final Answer must be the complete, professionally "
                "formatted screenplay scene."
            ),
            agent=self.reviewer,
            expected_output=(
                "The final, complete, and professionally formatted screenplay scene, which incorporates the "
                "results of the delegated revision."
            ),
            context=[task_dialogue, task_outline]
        )

        return [task_analyze, task_outline, task_dialogue, task_review_and_revise]