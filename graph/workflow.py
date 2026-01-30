"""
LangGraph workflow for Multi-Agent Debate System.
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from graph.state import DebateState, create_initial_state
from agents.researcher import Researcher
from agents.bull_agent import BullAgent
from agents.bear_agent import BearAgent
from agents.moderator import Moderator
from agents.judge import Judge


def create_debate_graph() -> StateGraph:
    """
    Create the LangGraph state graph for the debate.
    
    Flow:
    START -> Research -> Bull -> Moderator -> Bear -> Moderator -> ... -> Judge -> END
    
    The debate alternates between Bull and Bear with Moderator fact-checking
    until max_rounds is reached, then Judge makes final decision.
    """
    # Initialize agents
    researcher = Researcher()
    bull_agent = BullAgent()
    bear_agent = BearAgent()
    moderator = Moderator()
    judge = Judge()
    
    # Create the graph
    graph = StateGraph(DebateState)
    
    # Add nodes
    graph.add_node("research", researcher)
    graph.add_node("bull", bull_agent)
    graph.add_node("bear", bear_agent)
    graph.add_node("moderator", moderator)
    graph.add_node("judge", judge)
    
    # Define routing function
    def route_next_speaker(state: DebateState) -> Literal["bull", "bear", "moderator", "judge", "end"]:
        """Route to the next speaker based on state."""
        speaker = state.get("current_speaker", "research")
        
        if speaker == "end":
            return END
        elif speaker == "bull":
            return "bull"
        elif speaker == "bear":
            return "bear"
        elif speaker == "moderator":
            return "moderator"
        elif speaker == "judge":
            return "judge"
        else:
            return "bull"  # Default to bull
    
    # Set entry point
    graph.set_entry_point("research")
    
    # Add edges from research
    graph.add_edge("research", "bull")
    
    # Add conditional edges from bull
    graph.add_conditional_edges(
        "bull",
        route_next_speaker,
        {
            "moderator": "moderator",
            "judge": "judge",
            END: END,
        }
    )
    
    # Add conditional edges from moderator
    def route_after_moderator(state: DebateState) -> Literal["bull", "bear", "judge", "end"]:
        """Route after moderator based on debate round."""
        current_round = state.get("current_round", 1)
        max_rounds = state.get("max_rounds", 3)
        current_speaker = state.get("current_speaker", "bull")
        
        if current_speaker == "judge" or current_round > max_rounds:
            return "judge"
        elif current_speaker == "bull":
            return "bull"
        else:
            return "bear"
    
    graph.add_conditional_edges(
        "moderator",
        route_after_moderator,
        {
            "bull": "bull",
            "bear": "bear",
            "judge": "judge",
        }
    )
    
    # Add conditional edges from bear
    graph.add_conditional_edges(
        "bear",
        route_next_speaker,
        {
            "moderator": "moderator",
            "judge": "judge",
            END: END,
        }
    )
    
    # Judge always ends the graph
    graph.add_edge("judge", END)
    
    return graph.compile()


def run_debate(
    ticker: str,
    question: str = None,
    max_rounds: int = 3,
    verbose: bool = True,
) -> DebateState:
    """
    Run a complete debate on a stock.
    
    Args:
        ticker: Stock ticker to debate
        question: Optional specific question
        max_rounds: Number of bull-bear exchange rounds
        verbose: Whether to print progress
        
    Returns:
        Final DebateState with verdict
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    if verbose:
        console.print(Panel(
            f"[bold blue]Starting Multi-Agent Debate[/bold blue]\n"
            f"Ticker: [green]{ticker.upper()}[/green]\n"
            f"Rounds: {max_rounds}",
            title="Debate System"
        ))
    
    # Create initial state
    initial_state = create_initial_state(
        ticker=ticker,
        question=question,
        max_rounds=max_rounds,
    )
    
    # Create and run graph
    graph = create_debate_graph()
    
    # Stream execution for visibility
    final_state = None
    
    for event in graph.stream(initial_state):
        for node_name, node_output in event.items():
            if verbose:
                # Display progress
                if node_name == "research":
                    console.print("\n[yellow]📊 Research Phase Complete[/yellow]")
                elif node_name == "bull":
                    console.print("\n[green]🐂 BULL argues:[/green]")
                    args = node_output.get("arguments", [])
                    if args:
                        console.print(Panel(args[-1].get("content", "")[:500] + "...", 
                                          title="Bull Argument",
                                          border_style="green"))
                elif node_name == "bear":
                    console.print("\n[red]🐻 BEAR argues:[/red]")
                    args = node_output.get("arguments", [])
                    if args:
                        console.print(Panel(args[-1].get("content", "")[:500] + "...",
                                          title="Bear Argument", 
                                          border_style="red"))
                elif node_name == "moderator":
                    console.print("\n[blue]⚖️ MODERATOR:[/blue]")
                    args = node_output.get("arguments", [])
                    if args:
                        console.print(Panel(args[-1].get("content", "")[:300] + "...",
                                          title="Fact Check",
                                          border_style="blue"))
                elif node_name == "judge":
                    console.print("\n[bold magenta]👨‍⚖️ FINAL VERDICT[/bold magenta]")
                    verdict = node_output.get("verdict", {})
                    if verdict:
                        rec = verdict.get("recommendation", "HOLD")
                        conf = verdict.get("confidence", 0.5)
                        summary = verdict.get("summary", "No summary")
                        
                        rec_color = {
                            "STRONG BUY": "bold green",
                            "BUY": "green", 
                            "HOLD": "yellow",
                            "SELL": "red",
                            "STRONG SELL": "bold red",
                        }.get(rec, "white")
                        
                        console.print(Panel(
                            f"[{rec_color}]{rec}[/{rec_color}] (Confidence: {conf:.0%})\n\n"
                            f"{summary}\n\n"
                            f"Bull Score: {verdict.get('bull_score', 50)}/100\n"
                            f"Bear Score: {verdict.get('bear_score', 50)}/100",
                            title="Judge's Verdict",
                            border_style="magenta"
                        ))
            
            # Update final state
            if node_output:
                if final_state is None:
                    final_state = dict(initial_state)
                for key, value in node_output.items():
                    if key == "arguments":
                        final_state["arguments"] = final_state.get("arguments", []) + value
                    else:
                        final_state[key] = value
    
    return final_state


def create_simple_debate_graph() -> StateGraph:
    """
    Create a simplified debate graph without complex routing.
    
    Flow: Research -> Bull -> Bear -> Bull -> Bear -> Judge -> END
    """
    researcher = Researcher()
    bull_agent = BullAgent()
    bear_agent = BearAgent()
    judge = Judge()
    
    graph = StateGraph(DebateState)
    
    # Add nodes
    graph.add_node("research", researcher)
    graph.add_node("bull_1", bull_agent)
    graph.add_node("bear_1", bear_agent)
    graph.add_node("bull_2", bull_agent)
    graph.add_node("bear_2", bear_agent)
    graph.add_node("judge", judge)
    
    # Linear flow
    graph.set_entry_point("research")
    graph.add_edge("research", "bull_1")
    graph.add_edge("bull_1", "bear_1")
    graph.add_edge("bear_1", "bull_2")
    graph.add_edge("bull_2", "bear_2")
    graph.add_edge("bear_2", "judge")
    graph.add_edge("judge", END)
    
    return graph.compile()


if __name__ == "__main__":
    # Test the graph
    result = run_debate("NVDA", max_rounds=2, verbose=True)
    print(f"\nFinal verdict: {result.get('verdict', {}).get('recommendation', 'N/A')}")
