"""
Configuration for Snowflake connection and Cortex services.
"""
import os
from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class SnowflakeConfig:
    """Snowflake connection configuration."""
    account: str = ""
    user: str = ""
    password: str = ""
    warehouse: str = "COMPUTE_WH"
    database: str = "FINANCIAL_RESEARCH"
    schema: str = "EQUITY_RESEARCH"
    role: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "SnowflakeConfig":
        """Load configuration from environment variables."""
        return cls(
            account=os.getenv("SNOWFLAKE_ACCOUNT", ""),
            user=os.getenv("SNOWFLAKE_USER", ""),
            password=os.getenv("SNOWFLAKE_PASSWORD", ""),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "FINANCIAL_RESEARCH"),
            schema=os.getenv("SNOWFLAKE_SCHEMA", "EQUITY_RESEARCH"),
            role=os.getenv("SNOWFLAKE_ROLE"),
        )
    
    def get_connection_params(self) -> dict:
        """Get connection parameters for snowflake-connector-python."""
        params = {
            "account": self.account,
            "user": self.user,
            "password": self.password,
            "warehouse": self.warehouse,
            "database": self.database,
            "schema": self.schema,
        }
        if self.role:
            params["role"] = self.role
        return params


@dataclass
class CortexConfig:
    """Configuration for Cortex AI services."""
    # Semantic model for Cortex Analyst
    semantic_model_path: str = "@FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS/financial_research_semantic_model.yaml"
    
    # LLM model for CORTEX.COMPLETE
    model: str = "llama3.1-70b"
    
    # Debate settings
    max_debate_rounds: int = 3
    max_tokens: int = 1024
    temperature: float = 0.7
    
    # Cortex Search services
    search_services: Dict[str, str] = field(default_factory=lambda: {
        "analyst_reports": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.ANALYST_REPORTS_SEARCH",
        "annual_reports": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.ANNUAL_REPORTS_SEARCH",
        "earnings_transcripts": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.EARNINGS_TRANSCRIPTS_SEARCH",
        "sec_filings": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEC_FILINGS_SEARCH",
    })


# Default configurations
SNOWFLAKE_CONFIG = SnowflakeConfig.from_env()
CORTEX_CONFIG = CortexConfig()


def get_snowflake_connection():
    """
    Get a Snowflake connection using the CLI's default connection.
    Falls back to environment variables if CLI connection not available.
    """
    import snowflake.connector
    
    try:
        # Try to use Snowflake CLI default connection
        conn = snowflake.connector.connect(
            connection_name="default",
            database="FINANCIAL_RESEARCH",
            schema="EQUITY_RESEARCH",
        )
        return conn
    except Exception:
        # Fall back to environment variables
        config = SnowflakeConfig.from_env()
        return snowflake.connector.connect(**config.get_connection_params())
