"""
Cortex Analyst wrapper for Text-to-SQL on structured financial data.
"""
import json
from typing import Optional, Dict, Any, List
import snowflake.connector
from config import CORTEX_CONFIG, get_snowflake_connection


class CortexAnalyst:
    """
    Wrapper for Snowflake Cortex Analyst.
    Converts natural language questions to SQL and executes them.
    """
    
    def __init__(self, semantic_model_path: str = None):
        self.semantic_model_path = semantic_model_path or CORTEX_CONFIG.semantic_model_path
        self._connection = None
        # Track queries for debugging
        self.query_log: List[Dict[str, Any]] = []
    
    def _get_connection(self):
        """Get or create Snowflake connection."""
        if self._connection is None or self._connection.is_closed():
            self._connection = get_snowflake_connection()
        return self._connection
    
    def _log_query(self, query_type: str, sql: str, results: Any = None):
        """Log a query for debugging."""
        self.query_log.append({
            "type": query_type,
            "sql": sql,
            "results": results,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        })
    
    def get_query_log(self) -> List[Dict[str, Any]]:
        """Get the query log."""
        return self.query_log
    
    def clear_query_log(self):
        """Clear the query log."""
        self.query_log = []
    
    def ask(
        self,
        question: str,
        execute_sql: bool = True,
    ) -> Dict[str, Any]:
        """
        Ask a natural language question about the financial data.
        
        Args:
            question: Natural language question
            execute_sql: Whether to execute the generated SQL
            
        Returns:
            Dictionary with 'sql', 'explanation', and optionally 'results'
        """
        escaped_question = question.replace("'", "''")
        
        # Call Cortex Analyst REST API via SQL
        sql = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'analyst',
            OBJECT_CONSTRUCT(
                'semantic_model', '{self.semantic_model_path}',
                'question', '{escaped_question}'
            )
        ) as response
        """
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            
            if result:
                response_data = json.loads(result[0]) if isinstance(result[0], str) else result[0]
                generated_sql = response_data.get("sql", "")
                explanation = response_data.get("explanation", "")
                
                output = {
                    "question": question,
                    "sql": generated_sql,
                    "explanation": explanation,
                }
                
                # Execute the generated SQL if requested
                if execute_sql and generated_sql:
                    output["results"] = self._execute_sql(generated_sql)
                
                return output
            
            return {"question": question, "sql": "", "explanation": "No response", "results": []}
            
        except Exception as e:
            # Fallback: Use direct SQL generation approach
            return self._fallback_query(question, execute_sql)
        finally:
            cursor.close()
    
    def _fallback_query(self, question: str, execute_sql: bool = True) -> Dict[str, Any]:
        """
        Fallback method using CORTEX.COMPLETE for SQL generation.
        """
        from tools.cortex_llm import CortexLLM
        
        # Get table schemas for context
        schema_context = self._get_schema_context()
        
        system_prompt = f"""You are a SQL expert. Generate a Snowflake SQL query to answer the user's question.
        
Available tables in FINANCIAL_RESEARCH.EQUITY_RESEARCH:
{schema_context}

Rules:
- Return ONLY the SQL query, no explanations
- Use fully qualified table names (FINANCIAL_RESEARCH.EQUITY_RESEARCH.TABLE_NAME)
- Keep queries simple and efficient
"""
        
        llm = CortexLLM()
        sql_response = llm.complete(question, system_prompt=system_prompt)
        
        # Clean the SQL
        generated_sql = sql_response.strip()
        if generated_sql.startswith("```"):
            generated_sql = generated_sql.split("```")[1]
            if generated_sql.startswith("sql"):
                generated_sql = generated_sql[3:]
        generated_sql = generated_sql.strip()
        
        output = {
            "question": question,
            "sql": generated_sql,
            "explanation": "Generated via LLM fallback",
        }
        
        if execute_sql and generated_sql:
            output["results"] = self._execute_sql(generated_sql)
        
        return output
    
    def _get_schema_context(self) -> str:
        """Get schema information for SQL generation context."""
        return """
- INVESTMENT_METRICS: ticker, company_name, metric_date, pe_ratio, forward_pe, peg_ratio, price_to_book, roe_pct, roa_pct, debt_to_equity, dividend_yield_pct
- EARNINGS_HISTORY: ticker, company_name, fiscal_quarter, fiscal_year, report_date, eps_actual, eps_estimate, eps_surprise_pct, revenue_actual_millions, beat_miss
- INSIDER_TRANSACTIONS: ticker, company_name, insider_name, insider_title, transaction_type, transaction_date, shares_traded, total_value
- INSTITUTIONAL_HOLDINGS: ticker, company_name, institution_name, institution_type, shares_held, value_usd_millions, percent_of_shares_outstanding, change_type
- COMPETITOR_ANALYSIS: ticker, company_name, competitor_ticker, competitor_name, sector, market_cap_billions, revenue_growth_pct, market_share_pct
- MACROECONOMIC_INDICATORS: indicator_name, indicator_date, value, previous_value, change_pct, sector, region
- MARKET_SENTIMENT: ticker, company_name, sentiment_date, news_sentiment_score, social_media_sentiment_score, overall_sentiment, bullish_pct, bearish_pct
- TECHNICAL_INDICATORS: ticker, indicator_date, close_price, sma_20, sma_50, sma_200, rsi_14, macd, macd_signal, volume
"""
    
    def _execute_sql(self, sql: str, query_type: str = "query") -> List[Dict[str, Any]]:
        """Execute SQL and return results as list of dicts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            results = [dict(zip(columns, row)) for row in rows]
            # Log the query
            self._log_query(query_type, sql, results)
            return results
        except Exception as e:
            self._log_query(query_type, sql, {"error": str(e)})
            return [{"error": str(e)}]
        finally:
            cursor.close()
    
    def get_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get key investment metrics for a ticker."""
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.INVESTMENT_METRICS
        WHERE TICKER = '{ticker}'
        ORDER BY METRIC_DATE DESC
        LIMIT 1
        """
        results = self._execute_sql(sql, "get_metrics")
        return results[0] if results else {}
    
    def get_earnings_history(self, ticker: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Get recent earnings history for a ticker."""
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.EARNINGS_HISTORY
        WHERE TICKER = '{ticker}'
        ORDER BY REPORT_DATE DESC
        LIMIT {limit}
        """
        return self._execute_sql(sql, "get_earnings_history")
    
    def get_technical_indicators(self, ticker: str) -> Dict[str, Any]:
        """Get latest technical indicators for a ticker."""
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.TECHNICAL_INDICATORS
        WHERE TICKER = '{ticker}'
        ORDER BY INDICATOR_DATE DESC
        LIMIT 1
        """
        results = self._execute_sql(sql, "get_technical_indicators")
        return results[0] if results else {}
    
    def get_sentiment(self, ticker: str) -> Dict[str, Any]:
        """Get market sentiment for a ticker."""
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.MARKET_SENTIMENT
        WHERE TICKER = '{ticker}'
        ORDER BY SENTIMENT_DATE DESC
        LIMIT 1
        """
        results = self._execute_sql(sql, "get_sentiment")
        return results[0] if results else {}
    
    def get_insider_activity(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent insider transactions for a ticker."""
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.INSIDER_TRANSACTIONS
        WHERE TICKER = '{ticker}'
        ORDER BY TRANSACTION_DATE DESC
        LIMIT {limit}
        """
        return self._execute_sql(sql, "get_insider_activity")
    
    def get_institutional_holdings(self, ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top institutional holders for a ticker."""
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.INSTITUTIONAL_HOLDINGS
        WHERE TICKER = '{ticker}'
        ORDER BY VALUE_USD_MILLIONS DESC
        LIMIT {limit}
        """
        return self._execute_sql(sql, "get_institutional_holdings")
    
    def close(self):
        """Close the connection."""
        if self._connection and not self._connection.is_closed():
            self._connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_cortex_analyst():
    """Test the CortexAnalyst wrapper."""
    with CortexAnalyst() as analyst:
        # Test direct methods
        metrics = analyst.get_metrics("AAPL")
        print(f"AAPL Metrics: {metrics}")
        
        # Test natural language query
        result = analyst.ask("What are the top 3 stocks by P/E ratio?")
        print(f"Query Result: {result}")


if __name__ == "__main__":
    test_cortex_analyst()
