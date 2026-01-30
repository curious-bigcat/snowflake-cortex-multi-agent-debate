"""
Base agent class for all debate agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from graph.state import DebateState, Argument
from tools.cortex_llm import CortexLLM


class BaseAgent(ABC):
    """
    Base class for all debate agents.
    
    Each agent has:
    - A unique perspective/persona
    - Access to Cortex LLM for reasoning
    - Methods to generate arguments
    """
    
    def __init__(self, name: str, persona: str):
        self.name = name
        self.persona = persona
        self.llm = CortexLLM()
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    def format_research_context(self, research_data: dict) -> str:
        """Format research data into context for the LLM."""
        if not research_data:
            return "No research data available."
        
        context_parts = []
        
        # Metrics
        if research_data.get("metrics"):
            m = research_data["metrics"]
            context_parts.append(f"""
VALUATION METRICS:
- P/E Ratio: {m.get('PE_RATIO', 'N/A')}
- Forward P/E: {m.get('FORWARD_PE', 'N/A')}
- Price/Book: {m.get('PRICE_TO_BOOK', 'N/A')}
- ROE: {m.get('ROE_PCT', 'N/A')}%
- Debt/Equity: {m.get('DEBT_TO_EQUITY', 'N/A')}
- Dividend Yield: {m.get('DIVIDEND_YIELD_PCT', 'N/A')}%
""")
        
        # Technical Indicators
        if research_data.get("technical_indicators"):
            t = research_data["technical_indicators"]
            context_parts.append(f"""
TECHNICAL INDICATORS:
- Close Price: ${t.get('CLOSE_PRICE', 'N/A')}
- RSI (14): {t.get('RSI_14', 'N/A')}
- MACD: {t.get('MACD', 'N/A')}
- SMA 50: ${t.get('SMA_50', 'N/A')}
- SMA 200: ${t.get('SMA_200', 'N/A')}
""")
        
        # Sentiment
        if research_data.get("sentiment"):
            s = research_data["sentiment"]
            context_parts.append(f"""
MARKET SENTIMENT:
- Overall: {s.get('OVERALL_SENTIMENT', 'N/A')}
- News Score: {s.get('NEWS_SENTIMENT_SCORE', 'N/A')}
- Social Score: {s.get('SOCIAL_MEDIA_SENTIMENT_SCORE', 'N/A')}
- Bullish %: {s.get('BULLISH_PCT', 'N/A')}%
- Bearish %: {s.get('BEARISH_PCT', 'N/A')}%
""")
        
        # Earnings History
        if research_data.get("earnings_history"):
            context_parts.append("RECENT EARNINGS:")
            for e in research_data["earnings_history"][:3]:
                beat_miss = e.get('BEAT_MISS', 'N/A')
                surprise = e.get('EPS_SURPRISE_PCT', 0)
                context_parts.append(
                    f"- {e.get('FISCAL_QUARTER', 'N/A')} {e.get('FISCAL_YEAR', 'N/A')}: "
                    f"EPS ${e.get('EPS_ACTUAL', 'N/A')} ({beat_miss}, {surprise:+.1f}% surprise)"
                )
        
        # Analyst Reports
        if research_data.get("analyst_reports"):
            context_parts.append("\nANALYST REPORTS:")
            for r in research_data["analyst_reports"][:3]:
                context_parts.append(
                    f"- [{r.get('FIRM', 'Unknown')}] {r.get('RATING', 'N/A')} "
                    f"PT: ${r.get('PRICE_TARGET', 'N/A')}"
                )
                if r.get('REPORT_CONTENT'):
                    context_parts.append(f"  {r['REPORT_CONTENT'][:200]}...")
        
        # Insider Activity
        if research_data.get("insider_activity"):
            context_parts.append("\nINSIDER ACTIVITY:")
            for i in research_data["insider_activity"][:3]:
                context_parts.append(
                    f"- {i.get('INSIDER_NAME', 'Unknown')} ({i.get('INSIDER_TITLE', 'N/A')}): "
                    f"{i.get('TRANSACTION_TYPE', 'N/A')} {i.get('SHARES_TRADED', 'N/A'):,} shares "
                    f"@ ${i.get('PRICE_PER_SHARE', 'N/A')}"
                )
        
        return "\n".join(context_parts)
    
    def format_debate_history(self, arguments: List[dict]) -> str:
        """Format previous arguments into context."""
        if not arguments:
            return "No previous arguments."
        
        history_parts = ["DEBATE HISTORY:"]
        for arg in arguments:
            agent = arg.get("agent", "unknown").upper()
            content = arg.get("content", "")
            confidence = arg.get("confidence", 0)
            history_parts.append(f"\n[{agent}] (confidence: {confidence:.0%})")
            history_parts.append(content[:500] + "..." if len(content) > 500 else content)
        
        return "\n".join(history_parts)
    
    @abstractmethod
    def generate_argument(
        self,
        state: DebateState,
        opponent_argument: str = None,
    ) -> Argument:
        """
        Generate an argument based on current state.
        
        Args:
            state: Current debate state
            opponent_argument: Previous opponent's argument to respond to
            
        Returns:
            Generated Argument
        """
        pass
    
    def close(self):
        """Clean up resources."""
        self.llm.close()
