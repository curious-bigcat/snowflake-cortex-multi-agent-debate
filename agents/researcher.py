"""
Researcher agent - gathers data from Cortex Analyst and Cortex Search.
"""
from typing import Dict, Any
from graph.state import DebateState, ResearchData
from tools.cortex_analyst import CortexAnalyst
from tools.cortex_search import CortexSearch


class Researcher:
    """
    Research agent that gathers comprehensive data about a stock.
    Uses Cortex Analyst for structured data and Cortex Search for unstructured data.
    """
    
    def __init__(self):
        self.analyst = CortexAnalyst()
        self.search = CortexSearch()
    
    def gather_research(self, ticker: str) -> ResearchData:
        """
        Gather comprehensive research data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            ResearchData with all available information
        """
        ticker = ticker.upper()
        
        research = ResearchData(ticker=ticker)
        
        # Gather structured data from Cortex Analyst
        try:
            research.metrics = self.analyst.get_metrics(ticker)
            research.company_name = research.metrics.get("COMPANY_NAME", ticker)
        except Exception as e:
            print(f"Error getting metrics: {e}")
        
        try:
            research.earnings_history = self.analyst.get_earnings_history(ticker, limit=4)
        except Exception as e:
            print(f"Error getting earnings history: {e}")
        
        try:
            research.technical_indicators = self.analyst.get_technical_indicators(ticker)
        except Exception as e:
            print(f"Error getting technical indicators: {e}")
        
        try:
            research.sentiment = self.analyst.get_sentiment(ticker)
        except Exception as e:
            print(f"Error getting sentiment: {e}")
        
        try:
            research.insider_activity = self.analyst.get_insider_activity(ticker, limit=5)
        except Exception as e:
            print(f"Error getting insider activity: {e}")
        
        try:
            research.institutional_holdings = self.analyst.get_institutional_holdings(ticker, limit=5)
        except Exception as e:
            print(f"Error getting institutional holdings: {e}")
        
        # Gather unstructured data from Cortex Search
        try:
            research.analyst_reports = self.search.search_analyst_reports(
                f"{ticker} outlook growth risks",
                ticker=ticker,
                limit=5,
            )
        except Exception as e:
            print(f"Error searching analyst reports: {e}")
        
        try:
            research.earnings_transcripts = self.search.search_earnings_transcripts(
                f"{ticker} guidance outlook",
                ticker=ticker,
                limit=3,
            )
        except Exception as e:
            print(f"Error searching earnings transcripts: {e}")
        
        try:
            research.sec_filings = self.search.search_sec_filings(
                f"{ticker} material events",
                ticker=ticker,
                limit=3,
            )
        except Exception as e:
            print(f"Error searching SEC filings: {e}")
        
        return research
    
    def __call__(self, state: DebateState) -> Dict[str, Any]:
        """
        LangGraph node function.
        
        Args:
            state: Current debate state
            
        Returns:
            State updates with research data
        """
        ticker = state["ticker"]
        
        try:
            research = self.gather_research(ticker)
            return {
                "research_data": research.to_dict(),
                "current_speaker": "bull",  # Bull goes first after research
                "_analyst_log": self.analyst.get_query_log(),
                "_search_log": self.search.get_query_log(),
            }
        except Exception as e:
            return {
                "errors": [f"Research error: {str(e)}"],
                "current_speaker": "bull",
                "_analyst_log": self.analyst.get_query_log(),
                "_search_log": self.search.get_query_log(),
            }
    
    def close(self):
        """Clean up resources."""
        self.analyst.close()
        self.search.close()
