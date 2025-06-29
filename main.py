"""
Mixed-Model SceneSmith CLI with Cost Tracking
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from crew import MixedModelSceneSmithCrew, MixedModelOutput
from utils.logging_config import setup_logging

def setup_environment() -> bool:
    """Setup environment variables and logging."""
    load_dotenv()
    setup_logging()
    
    missing_keys = []
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing_keys.append("ANTHROPIC_API_KEY")
        
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
    """Display Mixed-Model Production results with cost breakdown."""
    
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
    
    # Cost Summary
    print("\n" + "=" * 80)
    print("💰 PRODUCTION COST BREAKDOWN")
    print("=" * 80)
    for model, cost in output.cost_by_model.items():
        print(f"{model}: ${cost:.4f}")
    print(f"\n🎯 TOTAL PRODUCTION COST: ${output.total_cost:.4f}")
    print("=" * 80)

def main() -> None:
    """Main CLI entry point."""
    if not setup_environment():
        return
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Mixed-Model SceneSmith")
    
    logline = get_user_input()
    if not logline:
        print("Error: Please provide a valid logline.")
        return
    
    print(f"\n🚀 Starting Mixed-Model Production...")
    print("🤖 Using GPT-4 for structure, Claude for psychology & dialogue")
    
    try:
        studio = MixedModelSceneSmithCrew()
        output = studio.generate_scene(logline)
        display_mixed_model_results(output)
        
    except Exception as e:
        logger.error(f"Production error: {str(e)}", exc_info=True)
        print(f"\n❌ Production Error: {str(e)}")

if __name__ == "__main__":
    main()