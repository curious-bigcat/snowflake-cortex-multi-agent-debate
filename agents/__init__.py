"""
Agent nodes for Multi-Agent Debate System.
"""
from agents.base import BaseAgent
from agents.bull_agent import BullAgent
from agents.bear_agent import BearAgent
from agents.moderator import Moderator
from agents.judge import Judge
from agents.researcher import Researcher

__all__ = [
    "BaseAgent",
    "BullAgent",
    "BearAgent",
    "Moderator",
    "Judge",
    "Researcher",
]
