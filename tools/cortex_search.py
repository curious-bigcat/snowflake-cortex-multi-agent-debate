"""
Cortex Search wrapper for RAG on unstructured financial documents.
"""
import json
from typing import Optional, Dict, Any, List
import snowflake.connector
from config import CORTEX_CONFIG, get_snowflake_connection


class CortexSearch:
    """
    Wrapper for Snowflake Cortex Search services.
    Provides semantic search over unstructured financial documents.
    """
    
    def __init__(self, search_services: Dict[str, str] = None):
        self.search_services = search_services or CORTEX_CONFIG.search_services
        self._connection = None
        # Track queries for debugging
        self.query_log: List[Dict[str, Any]] = []
    
    def _get_connection(self):
        """Get or create Snowflake connection."""
        if self._connection is None or self._connection.is_closed():
            self._connection = get_snowflake_connection()
        return self._connection
    
    def _log_query(self, query_type: str, service: str, request: dict, results: Any = None):
        """Log a search query for debugging."""
        self.query_log.append({
            "type": query_type,
            "service": service,
            "request": request,
            "results": results,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        })
    
    def get_query_log(self) -> List[Dict[str, Any]]:
        """Get the query log."""
        return self.query_log
    
    def clear_query_log(self):
        """Clear the query log."""
        self.query_log = []
    
    def search(
        self,
        query: str,
        service_name: str,
        columns: List[str] = None,
        filter_dict: Dict[str, Any] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search a Cortex Search service.
        
        Args:
            query: Search query text
            service_name: Name of the search service (key from search_services)
            columns: Columns to return in results
            filter_dict: Optional filter conditions
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        service_path = self.search_services.get(service_name, service_name)
        
        # Build search request
        search_request = {
            "query": query,
            "limit": limit,
        }
        
        if columns:
            search_request["columns"] = columns
        
        if filter_dict:
            search_request["filter"] = filter_dict
        
        # Use dollar quoting to avoid escaping issues
        request_json = json.dumps(search_request)
        
        sql = f"""SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW('{service_path}', $${request_json}$$) as results"""
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result:
                response = json.loads(result[0]) if isinstance(result[0], str) else result[0]
                results = response.get("results", [])
                # Log the query
                self._log_query(f"search_{service_name}", service_path, search_request, results)
                return results
            self._log_query(f"search_{service_name}", service_path, search_request, [])
            return []
            
        except Exception as e:
            self._log_query(f"search_{service_name}", service_path, search_request, {"error": str(e)})
            return [{"error": str(e)}]
        finally:
            cursor.close()
    
    def search_analyst_reports(
        self,
        query: str,
        ticker: str = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search analyst reports for relevant information.
        
        Args:
            query: Search query
            ticker: Optional ticker to filter by
            limit: Maximum results
            
        Returns:
            List of matching analyst reports
        """
        columns = ["TICKER", "FIRM", "ANALYST_NAME", "RATING", "PRICE_TARGET", "REPORT_TITLE", "REPORT_CONTENT"]
        filter_dict = {"@eq": {"TICKER": ticker}} if ticker else None
        
        return self.search(
            query=query,
            service_name="analyst_reports",
            columns=columns,
            filter_dict=filter_dict,
            limit=limit,
        )
    
    def search_earnings_transcripts(
        self,
        query: str,
        ticker: str = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search earnings call transcripts.
        
        Args:
            query: Search query
            ticker: Optional ticker to filter by
            limit: Maximum results
            
        Returns:
            List of matching transcript excerpts
        """
        columns = ["TICKER", "COMPANY_NAME", "QUARTER", "FISCAL_YEAR", "CEO_NAME", "TRANSCRIPT_CONTENT", "QA_SECTION"]
        filter_dict = {"@eq": {"TICKER": ticker}} if ticker else None
        
        return self.search(
            query=query,
            service_name="earnings_transcripts",
            columns=columns,
            filter_dict=filter_dict,
            limit=limit,
        )
    
    def search_sec_filings(
        self,
        query: str,
        ticker: str = None,
        filing_type: str = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search SEC filings.
        
        Args:
            query: Search query
            ticker: Optional ticker to filter by
            filing_type: Optional filing type (8-K, 10-Q, etc.)
            limit: Maximum results
            
        Returns:
            List of matching SEC filing excerpts
        """
        columns = ["TICKER", "COMPANY_NAME", "FILING_TYPE", "FILING_DATE", "FILING_DESCRIPTION", "FILING_CONTENT"]
        
        filter_dict = None
        if ticker and filing_type:
            filter_dict = {"@and": [{"@eq": {"TICKER": ticker}}, {"@eq": {"FILING_TYPE": filing_type}}]}
        elif ticker:
            filter_dict = {"@eq": {"TICKER": ticker}}
        elif filing_type:
            filter_dict = {"@eq": {"FILING_TYPE": filing_type}}
        
        return self.search(
            query=query,
            service_name="sec_filings",
            columns=columns,
            filter_dict=filter_dict,
            limit=limit,
        )
    
    def search_annual_reports(
        self,
        query: str,
        ticker: str = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search annual reports (10-K filings).
        
        Args:
            query: Search query
            ticker: Optional ticker to filter by
            limit: Maximum results
            
        Returns:
            List of matching annual report excerpts
        """
        columns = ["TICKER", "COMPANY_NAME", "FISCAL_YEAR", "REPORT_CONTENT", "KEY_HIGHLIGHTS"]
        filter_dict = {"@eq": {"TICKER": ticker}} if ticker else None
        
        return self.search(
            query=query,
            service_name="annual_reports",
            columns=columns,
            filter_dict=filter_dict,
            limit=limit,
        )
    
    def search_all(
        self,
        query: str,
        ticker: str = None,
        limit_per_service: int = 3,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search all available services and aggregate results.
        
        Args:
            query: Search query
            ticker: Optional ticker to filter by
            limit_per_service: Maximum results per service
            
        Returns:
            Dictionary with results from each service
        """
        return {
            "analyst_reports": self.search_analyst_reports(query, ticker, limit_per_service),
            "earnings_transcripts": self.search_earnings_transcripts(query, ticker, limit_per_service),
            "sec_filings": self.search_sec_filings(query, ticker, limit=limit_per_service),
            "annual_reports": self.search_annual_reports(query, ticker, limit_per_service),
        }
    
    def get_context_for_ticker(self, ticker: str, topics: List[str] = None) -> str:
        """
        Get comprehensive context about a ticker from all sources.
        
        Args:
            ticker: Stock ticker symbol
            topics: Optional list of topics to search for
            
        Returns:
            Formatted string with all relevant context
        """
        if topics is None:
            topics = ["outlook", "growth", "risks", "competitive position"]
        
        context_parts = []
        
        for topic in topics:
            query = f"{ticker} {topic}"
            results = self.search_all(query, ticker=ticker, limit_per_service=2)
            
            for service_name, service_results in results.items():
                for result in service_results:
                    if "error" not in result:
                        # Extract the main content field
                        content = (
                            result.get("REPORT_CONTENT") or 
                            result.get("TRANSCRIPT_CONTENT") or 
                            result.get("FILING_CONTENT") or 
                            ""
                        )
                        if content:
                            source = result.get("FIRM") or result.get("FILING_TYPE") or service_name
                            context_parts.append(f"[{source}]: {content[:500]}...")
        
        return "\n\n".join(context_parts) if context_parts else "No relevant context found."
    
    def close(self):
        """Close the connection."""
        if self._connection and not self._connection.is_closed():
            self._connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_cortex_search():
    """Test the CortexSearch wrapper."""
    with CortexSearch() as search:
        # Test analyst reports search
        results = search.search_analyst_reports("AI chip demand", ticker="NVDA", limit=2)
        print(f"Analyst Reports: {json.dumps(results, indent=2)}")
        
        # Test earnings transcripts search
        results = search.search_earnings_transcripts("revenue growth", ticker="AAPL", limit=2)
        print(f"Earnings Transcripts: {json.dumps(results, indent=2)}")


if __name__ == "__main__":
    test_cortex_search()
