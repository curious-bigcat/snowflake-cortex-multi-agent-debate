"""
Graph module for Multi-Agent Debate System.
"""
from graph.state import DebateState, create_initial_state, Argument, ResearchData, Verdict

# Lazy import to avoid circular dependency
def create_debate_graph():
    from graph.workflow import create_debate_graph as _create
    return _create()

def run_debate(*args, **kwargs):
    from graph.workflow import run_debate as _run
    return _run(*args, **kwargs)

__all__ = [
    "DebateState",
    "create_initial_state", 
    "Argument",
    "ResearchData",
    "Verdict",
    "create_debate_graph",
    "run_debate",
]
