"""
State definitions for the Multi-Agent Debate system.
"""
from typing import TypedDict, List, Optional, Annotated, Literal
from dataclasses import dataclass, field
from datetime import datetime
import operator


@dataclass
class Argument:
    """Represents a single argument in the debate."""
    agent: str  # "bull", "bear", "moderator", "judge"
    content: str
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1 score
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "content": self.content,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }


@dataclass
class ResearchData:
    """Aggregated research data for the debate."""
    ticker: str
    company_name: str = ""
    
    # Structured data from Cortex Analyst
    metrics: dict = field(default_factory=dict)
    earnings_history: List[dict] = field(default_factory=list)
    technical_indicators: dict = field(default_factory=dict)
    sentiment: dict = field(default_factory=dict)
    insider_activity: List[dict] = field(default_factory=list)
    institutional_holdings: List[dict] = field(default_factory=list)
    
    # Unstructured data from Cortex Search
    analyst_reports: List[dict] = field(default_factory=list)
    earnings_transcripts: List[dict] = field(default_factory=list)
    sec_filings: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "metrics": self.metrics,
            "earnings_history": self.earnings_history,
            "technical_indicators": self.technical_indicators,
            "sentiment": self.sentiment,
            "insider_activity": self.insider_activity,
            "institutional_holdings": self.institutional_holdings,
            "analyst_reports": self.analyst_reports,
            "earnings_transcripts": self.earnings_transcripts,
            "sec_filings": self.sec_filings,
        }


def add_arguments(left: List[dict], right: List[dict]) -> List[dict]:
    """Reducer function to append new arguments to existing list."""
    return left + right


class DebateState(TypedDict):
    """
    State for the Multi-Agent Debate graph.
    
    This state is shared across all nodes in the LangGraph workflow.
    """
    # Input parameters
    ticker: str
    question: Optional[str]  # Optional specific question to debate
    
    # Research data
    research_data: Optional[dict]  # ResearchData as dict
    
    # Debate tracking
    current_round: int
    max_rounds: int
    current_speaker: Literal["research", "bull", "bear", "moderator", "judge", "end"]
    
    # Argument history (uses reducer to append)
    arguments: Annotated[List[dict], add_arguments]
    
    # Moderation feedback
    fact_checks: List[dict]
    
    # Final verdict
    verdict: Optional[dict]  # Final recommendation
    
    # Error tracking
    errors: List[str]
    
    # Debug/Query logs (optional)
    _analyst_log: Optional[List[dict]]
    _search_log: Optional[List[dict]]


def create_initial_state(
    ticker: str,
    question: str = None,
    max_rounds: int = 3,
) -> DebateState:
    """
    Create initial state for a new debate.
    
    Args:
        ticker: Stock ticker to debate
        question: Optional specific question (e.g., "Should we buy AAPL?")
        max_rounds: Number of debate rounds (bull-bear exchanges)
        
    Returns:
        Initial DebateState
    """
    return DebateState(
        ticker=ticker.upper(),
        question=question or f"Should we buy or sell {ticker.upper()}?",
        research_data=None,
        current_round=0,
        max_rounds=max_rounds,
        current_speaker="research",
        arguments=[],
        fact_checks=[],
        verdict=None,
        errors=[],
        _analyst_log=[],
        _search_log=[],
    )


@dataclass
class Verdict:
    """Final verdict from the judge."""
    recommendation: Literal["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
    confidence: float  # 0-1
    summary: str
    bull_score: float  # 0-100
    bear_score: float  # 0-100
    key_factors: List[str]
    risks: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "summary": self.summary,
            "bull_score": self.bull_score,
            "bear_score": self.bear_score,
            "key_factors": self.key_factors,
            "risks": self.risks,
            "timestamp": self.timestamp,
        }
