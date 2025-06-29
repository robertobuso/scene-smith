"""
Mixed-Model SceneSmith CLI with Cost Tracking
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from crew import MixedModelSceneSmithCrew, MixedModelOutput
from utils.logging_config import setup_logging
import agentops

def setup_environment() -> bool:
    """Setup environment variables and logging."""
    load_dotenv()
    setup_logging()
    
    missing_keys = []
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
    if not os.getenv("AGENTOPS_API_KEY"):  # ← ADD THIS LINE
        missing_keys.append("AGENTOPS_API_KEY")  # ← ADD THIS LINE
        
    if missing_keys:
        logging.error(f"Missing API keys: {', '.join(missing_keys)}")
        print(f"Error: Missing API keys: {', '.join(missing_keys)}")
        print("Copy .env.example to .env and add your API keys.")
        return False
    
    return True

def get_user_input() -> Optional[str]:
    """Get logline input from user."""
    print("🎬 SceneSmith Mixed-Model Production Studio")
    print("=" * 60)
    print("🤖 GPT-4: Structure & Scene Architecture")
    print("🧠 Claude: Character Psychology & Dialogue")
    print("💰 Real-time Cost Tracking")
    print("=" * 60)
    
    logline = input("\nEnter your logline: ").strip()
    return logline if logline else None

def display_mixed_model_results(output: MixedModelOutput) -> None:
    """Display Mixed-Model Production results."""
    
    print("\n" + "=" * 80)
    print("🎭 MIXED-MODEL PRODUCTION RESULTS")
    print("=" * 80)
    
    # ACT I
    print("\n🎬 ACT I: PRE-PRODUCTION")
    print("-" * 40)
    print("📋 DRAMATURGE (GPT-4): Structure Analysis")
    print(output.structure_analysis[:200] + "..." if len(output.structure_analysis) > 200 else output.structure_analysis)
    
    print("\n👥 CHARACTER CREATOR (Claude): McKee's Framework")
    print(output.character_bible[:200] + "..." if len(output.character_bible) > 200 else output.character_bible)
    
    # ACT II  
    print("\n🎬 ACT II: PRODUCTION")
    print("-" * 40)
    print("🏗️ SCENE ARCHITECT (GPT-4): Visual Storytelling")
    print(output.scene_outline[:200] + "..." if len(output.scene_outline) > 200 else output.scene_outline)
    
    print("\n💬 DIALOGUE SPECIALIST (Claude): Authentic Voices")
    print(output.first_draft_dialogue[:200] + "..." if len(output.first_draft_dialogue) > 200 else output.first_draft_dialogue)
    
    # ACT III
    print("\n🎬 ACT III: POST-PRODUCTION")
    print("-" * 40)
    print("🎯 FINAL SCREENPLAY (Claude - AI Detection & Polish)")
    print("=" * 40)
    print(output.final_screenplay)
    
    print("\n💰 Cost tracking available in AgentOps dashboard")
    print("=" * 80)

def main() -> None:
    """Main CLI entry point with AgentOps tracking."""
    if not setup_environment():
        return
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Mixed-Model SceneSmith")
    
    # Initialize AgentOps ONCE at the start
    agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))
    
    logline = get_user_input()
    if not logline:
        print("Error: Please provide a valid logline.")
        agentops.end_trace('Failed')  # ← UPDATED METHOD
        return
    
    print(f"\n🚀 Starting Mixed-Model Production...")
    print("🤖 Using GPT-4 for structure, Claude for psychology & dialogue")
    print("📊 Cost tracking via AgentOps")
    
    try:
        studio = MixedModelSceneSmithCrew()
        output = studio.generate_scene(logline)
        display_mixed_model_results(output)
        
        # End AgentOps session successfully
        agentops.end_session('Success')  # ← CORRECTED METHOD
        
    except Exception as e:
        logger.error(f"Production error: {str(e)}", exc_info=True)
        print(f"\n❌ Production Error: {str(e)}")
        
        # End AgentOps session with failure
        agentops.end_session('Failed')  # ← CORRECTED METHOD

if __name__ == "__main__":
    main()