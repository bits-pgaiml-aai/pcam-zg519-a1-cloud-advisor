from .goal_based import GoalBasedAgent
from .learning import LearningAgent
from .model_based import ModelBasedReflexAgent
from .simple_reflex import SimpleReflexAgent
from .utility_based import UtilityBasedAgent

CLASSICAL_AGENTS = {
    "Simple Reflex": SimpleReflexAgent,
    "Model-Based Reflex": ModelBasedReflexAgent,
    "Goal-Based": GoalBasedAgent,
    "Utility-Based": UtilityBasedAgent,
    "Learning": LearningAgent,
}

__all__ = [
    "SimpleReflexAgent",
    "ModelBasedReflexAgent",
    "GoalBasedAgent",
    "UtilityBasedAgent",
    "LearningAgent",
    "CLASSICAL_AGENTS",
]
