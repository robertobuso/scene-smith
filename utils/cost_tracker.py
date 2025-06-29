"""
Cost tracking utility for mixed AI models.
"""

import logging
import tiktoken
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ModelCost:
    """Cost information for a specific model."""
    input_cost_per_1k: float
    output_cost_per_1k: float
    
# Current pricing as of 2025 (per 1K tokens)
MODEL_COSTS = {
    "gpt-4": ModelCost(0.03, 0.06),
    "gpt-4o": ModelCost(0.01, 0.03),
    "claude-3-5-sonnet-20241022": ModelCost(0.003, 0.015),
    "claude-3-haiku-20240307": ModelCost(0.00025, 0.00125)
}

@dataclass
class AgentCostSummary:
    """Cost summary for a single agent call."""
    agent_name: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: datetime = field(default_factory=datetime.now)

class CostTracker:
    """Tracks API costs across different models and agents."""
    
    def __init__(self):
        self.costs: list[AgentCostSummary] = []
        self.enabled = True
        
    def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count for given text and model."""
        try:
            if model.startswith("gpt"):
                encoding = tiktoken.encoding_for_model("gpt-4")
                return len(encoding.encode(text))
            elif model.startswith("claude"):
                # Claude uses similar tokenization to GPT-4, rough estimate
                encoding = tiktoken.encoding_for_model("gpt-4")
                return len(encoding.encode(text))
            else:
                # Fallback estimate: ~4 chars per token
                return len(text) // 4
        except Exception:
            return len(text) // 4
    
    def log_agent_cost(self, 
                      agent_name: str, 
                      model: str, 
                      input_text: str, 
                      output_text: str) -> Optional[AgentCostSummary]:
        """Log cost for an agent's API call."""
        if not self.enabled or model not in MODEL_COSTS:
            return None
            
        try:
            input_tokens = self.estimate_tokens(input_text, model)
            output_tokens = self.estimate_tokens(output_text, model)
            
            cost_info = MODEL_COSTS[model]
            input_cost = (input_tokens / 1000) * cost_info.input_cost_per_1k
            output_cost = (output_tokens / 1000) * cost_info.output_cost_per_1k
            total_cost = input_cost + output_cost
            
            summary = AgentCostSummary(
                agent_name=agent_name,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost=input_cost,
                output_cost=output_cost,
                total_cost=total_cost
            )
            
            self.costs.append(summary)
            
            logger.info(f"💰 {agent_name} ({model}): "
                       f"${total_cost:.4f} ({input_tokens} in + {output_tokens} out tokens)")
            
            return summary
            
        except Exception as e:
            logger.warning(f"Failed to track cost for {agent_name}: {e}")
            return None
    
    def get_total_cost(self) -> float:
        """Get total cost across all tracked calls."""
        return sum(cost.total_cost for cost in self.costs)
    
    def get_cost_by_model(self) -> Dict[str, float]:
        """Get cost breakdown by model."""
        model_costs = {}
        for cost in self.costs:
            if cost.model not in model_costs:
                model_costs[cost.model] = 0
            model_costs[cost.model] += cost.total_cost
        return model_costs
    
    def print_summary(self) -> None:
        """Print cost summary to console."""
        if not self.costs:
            print("📊 No costs tracked.")
            return
            
        print("\n" + "=" * 60)
        print("💰 COST TRACKING SUMMARY")
        print("=" * 60)
        
        by_model = self.get_cost_by_model()
        for model, cost in by_model.items():
            print(f"{model}: ${cost:.4f}")
            
        print(f"\n🎯 TOTAL COST: ${self.get_total_cost():.4f}")
        print("=" * 60)

# Global cost tracker instance
cost_tracker = CostTracker()