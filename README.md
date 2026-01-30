# Multi-Agent Debate System for Financial Analysis

A sophisticated financial analysis application using **Snowflake Cortex AI** to power competitive reasoning between Bull and Bear agents for investment decisions. Built with LangGraph for orchestration and Streamlit for the web interface.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Step-by-Step Setup Guide](#step-by-step-setup-guide)
6. [Running the Application](#running-the-application)
7. [Using the Application](#using-the-application)
8. [Snowflake Objects Reference](#snowflake-objects-reference)
9. [Configuration](#configuration)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)
12. [Extending the System](#extending-the-system)

---

## Overview

This system implements a **multi-agent debate pattern** for financial analysis where AI agents with opposing viewpoints analyze stocks and debate their investment merit:

| Agent | Role | Perspective |
|-------|------|-------------|
| **Researcher** | Gathers data from multiple sources | Neutral - fact-finding |
| **Bull Agent** | Advocates for buying the stock | Optimistic - finds growth potential |
| **Bear Agent** | Advocates against buying | Skeptical - identifies risks |
| **Moderator** | Fact-checks arguments | Neutral - ensures accuracy |
| **Judge** | Delivers final verdict | Balanced - weighs all evidence |

### Why Multi-Agent Debate?

- **Reduces hallucinations** by grounding arguments in real financial data
- **Competitive reasoning** forces agents to counter opposing viewpoints
- **Fact-checking** ensures claims are supported by actual data
- **Balanced analysis** presents both bullish and bearish perspectives

### Snowflake Cortex AI Components Used

| Component | Purpose | How It's Used |
|-----------|---------|---------------|
| **Cortex Analyst** | Text-to-SQL | Converts natural language to SQL queries for structured financial data |
| **Cortex Search** | Semantic RAG | Searches analyst reports, earnings transcripts, SEC filings |
| **Cortex Complete** | LLM Chat | Powers agent reasoning and argument generation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Streamlit Web UI                            │
│              http://localhost:8501 (Docker Container)               │
├─────────────────────────────────────────────────────────────────────┤
│                      LangGraph Orchestration                        │
│         State Machine: Research → Bull → Bear → Judge               │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│  Researcher  │  Bull Agent  │  Bear Agent  │   Judge Agent         │
│  (Data)      │  (Buy Case)  │  (Sell Case) │   (Verdict)           │
├──────────────┴──────────────┴──────────────┴───────────────────────┤
│                      Snowflake Cortex AI                            │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Cortex Analyst │  │  Cortex Search  │  │  Cortex Complete    │  │
│  │ (Text-to-SQL)  │  │  (Semantic RAG) │  │  (llama3.1-70b)     │  │
│  └────────────────┘  └─────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      Snowflake Data Layer                           │
│                                                                     │
│  Structured Data (Cortex Analyst)    Unstructured Data (Search)    │
│  ├── Investment Metrics              ├── Analyst Reports           │
│  ├── Earnings History                ├── Earnings Transcripts      │
│  ├── Technical Indicators            ├── SEC Filings               │
│  ├── Market Sentiment                └── Annual Reports            │
│  ├── Insider Transactions                                          │
│  └── Institutional Holdings                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Debate Flow

```
START
  │
  ▼
┌─────────────┐
│  Researcher │ ─── Gathers financial data via Cortex Analyst & Search
└─────────────┘
  │
  ▼
┌─────────────┐
│ Bull Agent  │ ─── Makes bullish case using research data
└─────────────┘
  │
  ▼
┌─────────────┐
│ Moderator   │ ─── Fact-checks bull's claims
└─────────────┘
  │
  ▼
┌─────────────┐
│ Bear Agent  │ ─── Makes bearish case, counters bull
└─────────────┘
  │
  ▼
┌─────────────┐
│ Moderator   │ ─── Fact-checks bear's claims
└─────────────┘
  │
  ▼ (Repeat for N rounds)
  │
┌─────────────┐
│   Judge     │ ─── Weighs arguments, delivers verdict
└─────────────┘
  │
  ▼
 END (BUY / HOLD / SELL recommendation)
```

---

## Prerequisites

Before starting, ensure you have:

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 20.10+ | Container runtime |
| Docker Compose | 2.0+ | Multi-container orchestration |
| Snowflake CLI (snowsql) | Latest | Database setup |
| Python | 3.11+ | Local development (optional) |

### Snowflake Requirements

- Snowflake account with **Cortex AI enabled**
- Appropriate role permissions (ACCOUNTADMIN or custom role)
- Warehouse for compute (e.g., `COMPUTE_WH`)
- Snowflake CLI configured at `~/.snowflake/config.toml`

### Check Your Snowflake CLI Configuration

```bash
# Verify config file exists
cat ~/.snowflake/config.toml

# Expected format:
# [connections.default]
# account = "YOUR_ACCOUNT"
# user = "YOUR_USER"
# password = "YOUR_PASSWORD"
# warehouse = "COMPUTE_WH"
# role = "ACCOUNTADMIN"
```

---

## Project Structure

```
Multi-Agent-Debate/
│
├── agents/                          # AI Agent Implementations
│   ├── __init__.py                  # Agent exports
│   ├── base.py                      # BaseAgent class with Cortex LLM
│   ├── researcher.py                # Research agent (data gathering)
│   ├── bull_agent.py                # Bull agent (buy advocate)
│   ├── bear_agent.py                # Bear agent (sell advocate)
│   ├── moderator.py                 # Moderator (fact-checker)
│   └── judge.py                     # Judge agent (final verdict)
│
├── tools/                           # Snowflake Cortex AI Wrappers
│   ├── __init__.py                  # Tool exports
│   ├── cortex_analyst.py            # Text-to-SQL via semantic model
│   ├── cortex_search.py             # Semantic search across documents
│   └── cortex_llm.py                # LLM wrapper (Cortex Complete)
│
├── graph/                           # LangGraph Workflow
│   ├── __init__.py                  # Graph exports
│   ├── state.py                     # DebateState TypedDict definition
│   └── workflow.py                  # Graph construction and execution
│
├── config/                          # Configuration Files
│   └── financial_research_semantic_model.yaml   # Cortex Analyst semantic model
│
├── sql/                             # Snowflake SQL Scripts
│   ├── setup_all.sql                # Complete database setup (tables, search services, stage)
│   └── sample_data.sql              # Sample financial data for testing
│
├── config.py                        # Application configuration (DB, schema, warehouse)
├── main.py                          # CLI entry point
├── streamlit_app.py                 # Streamlit web UI with debug view
├── requirements.txt                 # Python dependencies
│
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Docker services configuration
├── Makefile                         # Convenience commands
└── .dockerignore                    # Docker build exclusions
```

---

## Step-by-Step Setup Guide

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd Multi-Agent-Debate

# Or download and extract the zip file
```

### Step 2: Configure Snowflake Connection

Ensure your `~/.snowflake/config.toml` file is properly configured:

```toml
[connections.default]
account = "YOUR_ACCOUNT_IDENTIFIER"    # e.g., "abc12345.us-east-1"
user = "YOUR_USERNAME"
password = "YOUR_PASSWORD"
warehouse = "COMPUTE_WH"               # Must exist in your account
role = "ACCOUNTADMIN"                  # Or role with required permissions
```

**Test the connection:**
```bash
snowsql -q "SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();"
```

### Step 3: Create Snowflake Database Objects

Run the complete setup script to create all required objects:

```bash
# This creates: database, schema, tables, search services, stage
snowsql -f sql/setup_all.sql
```

**What this creates:**

| Object Type | Name | Purpose |
|-------------|------|---------|
| Database | `FINANCIAL_RESEARCH` | Main database |
| Schema | `EQUITY_RESEARCH` | Schema for all objects |
| Warehouse | `DEBATE_WH` | Compute warehouse (XSMALL) |
| Role | `DEBATE_APP_ROLE` | Application role |
| Tables | 11 tables | Financial data storage |
| Search Services | 4 services | Semantic search |
| Stage | `SEMANTIC_MODELS` | Semantic model storage |

### Step 4: Upload the Semantic Model

The semantic model defines how Cortex Analyst interprets natural language queries:

```bash
# Upload semantic model to Snowflake stage
snowsql -q "PUT file://$(pwd)/config/financial_research_semantic_model.yaml @FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

# Verify upload
snowsql -q "LIST @FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS;"
```

### Step 5: Load Sample Data (Optional but Recommended)

Load test data to verify the system works:

```bash
snowsql -f sql/sample_data.sql
```

This loads sample data for 10 major stocks: NVDA, AAPL, MSFT, GOOGL, AMZN, TSLA, META, AMD, NFLX, CRM.

### Step 6: Verify Setup

Test that everything is working:

```bash
# Check tables have data
snowsql -q "SELECT TICKER, COMPANY_NAME FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.INVESTMENT_METRICS;"

# Check search services
snowsql -q "SHOW CORTEX SEARCH SERVICES IN SCHEMA FINANCIAL_RESEARCH.EQUITY_RESEARCH;"

# Test Cortex Analyst (if semantic model uploaded)
snowsql -q "
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-8b',
    'Say hello in one word'
) as response;
"
```

---

## Running the Application

### Option A: Docker (Recommended)

```bash
# Build the Docker image
make build

# Start the application
make run

# View logs
make logs

# Stop the application
make stop
```

**Or using docker-compose directly:**

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option B: Local Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py

# Or run CLI
python main.py run NVDA --rounds 2
```

### Access the Application

Open your browser to: **http://localhost:8501**

---

## Using the Application

### Web Interface (Streamlit)

1. **Enter Stock Ticker**: Type a ticker symbol (e.g., `NVDA`, `AAPL`, `TSLA`)

2. **Configure Debate**:
   - **Rounds**: Number of bull-bear exchanges (1-5, default: 2)
   - **Custom Question**: Optional specific question to analyze

3. **Start Debate**: Click the button to begin analysis

4. **View Results**:
   - Research phase shows gathered data
   - Bull and Bear arguments displayed
   - Final verdict with recommendation

5. **Debug View**: Enable "Show Debug View" in sidebar to see:
   - Raw SQL queries generated by Cortex Analyst
   - Search queries sent to Cortex Search
   - LLM prompts and responses

### Command Line Interface

```bash
# Run a full debate
python main.py run NVDA --rounds 2

# With custom question
python main.py run AAPL --rounds 3 --question "Should I buy Apple for dividend income?"

# Search analyst reports
python main.py search TSLA "growth outlook"

# Query structured data
python main.py ask "What is NVDA's P/E ratio?"

# Test Snowflake connection
python main.py test-connection
```

### Docker CLI Access

```bash
# Enter container shell
make shell

# Run CLI commands inside container
python main.py run NVDA --rounds 2

# Or run directly
make cli CMD='run NVDA --rounds 2'
```

---

## Snowflake Objects Reference

### Tables

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `INVESTMENT_METRICS` | Valuation ratios and financial metrics | PE_RATIO, ROE_PCT, DEBT_TO_EQUITY |
| `EARNINGS_HISTORY` | Quarterly earnings results | EPS_ACTUAL, EPS_ESTIMATE, BEAT_MISS |
| `TECHNICAL_INDICATORS` | Price and volume indicators | RSI_14, SMA_50, SMA_200, MACD |
| `MARKET_SENTIMENT` | News and social sentiment | SENTIMENT_SCORE, BULLISH_PCT |
| `INSIDER_TRANSACTIONS` | Insider trading activity | TRANSACTION_TYPE, SHARES, VALUE |
| `INSTITUTIONAL_HOLDINGS` | 13F institutional ownership | SHARES_HELD, PCT_OUTSTANDING |
| `ANALYST_REPORTS` | Research reports (for search) | REPORT_CONTENT, RATING, PRICE_TARGET |
| `EARNINGS_TRANSCRIPTS` | Call transcripts (for search) | TRANSCRIPT_CONTENT, OVERALL_TONE |
| `SEC_FILINGS` | Regulatory filings (for search) | FILING_CONTENT, FILING_TYPE |
| `ANNUAL_REPORTS` | Annual reports (for search) | REPORT_CONTENT, FISCAL_YEAR |
| `COMPETITOR_ANALYSIS` | Competitive positioning | MARKET_SHARE, COMPETITIVE_ADVANTAGE |

### Cortex Search Services

| Service | Source Table | Search Column | Filters |
|---------|--------------|---------------|---------|
| `ANALYST_REPORTS_SEARCH` | ANALYST_REPORTS | REPORT_CONTENT | TICKER, FIRM, RATING |
| `EARNINGS_TRANSCRIPTS_SEARCH` | EARNINGS_TRANSCRIPTS | TRANSCRIPT_CONTENT | TICKER, FISCAL_YEAR |
| `SEC_FILINGS_SEARCH` | SEC_FILINGS | FILING_CONTENT | TICKER, FILING_TYPE |
| `ANNUAL_REPORTS_SEARCH` | ANNUAL_REPORTS | REPORT_CONTENT | TICKER, FISCAL_YEAR |

### Semantic Model

The semantic model (`config/financial_research_semantic_model.yaml`) defines:

- **Tables**: Schema definitions for Cortex Analyst
- **Dimensions**: Categorical columns (TICKER, COMPANY_NAME)
- **Measures**: Numeric columns (PE_RATIO, REVENUE_GROWTH_YOY_PCT)
- **Time Dimensions**: Date columns (METRIC_DATE, REPORT_DATE)
- **Verified Queries**: Sample questions with expected SQL

---

## Configuration

### Application Configuration (config.py)

```python
# Database settings
SNOWFLAKE_DATABASE = "FINANCIAL_RESEARCH"
SNOWFLAKE_SCHEMA = "EQUITY_RESEARCH"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"

# Cortex AI settings
LLM_MODEL = "llama3.1-70b"  # Options: llama3.1-8b, llama3.1-70b, mistral-large

# Semantic model path
SEMANTIC_MODEL_PATH = "@FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS/financial_research_semantic_model.yaml"

# Cortex Search services
SEARCH_SERVICES = {
    "analyst_reports": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.ANALYST_REPORTS_SEARCH",
    "earnings_transcripts": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.EARNINGS_TRANSCRIPTS_SEARCH",
    "sec_filings": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEC_FILINGS_SEARCH",
    "annual_reports": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.ANNUAL_REPORTS_SEARCH",
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SNOWFLAKE_CONNECTION_NAME` | `default` | Connection name in config.toml |
| `SNOWFLAKE_DATABASE` | `FINANCIAL_RESEARCH` | Database name |
| `SNOWFLAKE_SCHEMA` | `EQUITY_RESEARCH` | Schema name |
| `SNOWFLAKE_WAREHOUSE` | `COMPUTE_WH` | Warehouse name |
| `LLM_MODEL` | `llama3.1-70b` | Cortex LLM model |

---

## API Reference

### Tools Module

#### CortexAnalyst (tools/cortex_analyst.py)

```python
from tools.cortex_analyst import CortexAnalyst

analyst = CortexAnalyst()

# Ask a question (returns SQL result)
result = analyst.ask("What is NVDA's P/E ratio?")

# Get query log for debugging
queries = analyst.get_query_log()

# Clear query log
analyst.clear_query_log()
```

#### CortexSearch (tools/cortex_search.py)

```python
from tools.cortex_search import CortexSearch

search = CortexSearch()

# Search analyst reports
results = search.search_analyst_reports("NVDA", "growth outlook", limit=5)

# Search earnings transcripts
results = search.search_earnings_transcripts("AAPL", "AI strategy")

# Search all sources
results = search.search_all("TSLA", "autonomous driving")
```

#### CortexLLM (tools/cortex_llm.py)

```python
from tools.cortex_llm import CortexLLM

llm = CortexLLM(model="llama3.1-70b")

# Generate completion
response = llm.complete(
    prompt="Analyze NVDA stock",
    system_prompt="You are a financial analyst"
)
```

### Agents Module

```python
from agents import BullAgent, BearAgent, Judge, Researcher

# Create agents
researcher = Researcher()
bull = BullAgent()
bear = BearAgent()
judge = Judge()

# Run debate workflow
from graph.workflow import run_debate

result = run_debate(
    ticker="NVDA",
    question="Should I buy NVIDIA?",
    max_rounds=2,
    verbose=True
)

print(result["verdict"])
# {'recommendation': 'BUY', 'confidence': 0.85, 'summary': '...'}
```

---

## Troubleshooting

### Connection Issues

**Error: "Connection refused" or "Could not connect"**

```bash
# Check Snowflake CLI config
cat ~/.snowflake/config.toml

# Test connection
snowsql -q "SELECT CURRENT_USER();"

# Ensure warehouse is running
snowsql -q "ALTER WAREHOUSE COMPUTE_WH RESUME;"
```

**Error: "Authentication failed"**

- Verify username/password in config.toml
- Check if password contains special characters (may need quoting)
- Ensure account identifier format is correct (e.g., `abc12345.us-east-1`)

### Cortex AI Issues

**Error: "Cortex Search service not found"**

```sql
-- List available search services
SHOW CORTEX SEARCH SERVICES IN SCHEMA FINANCIAL_RESEARCH.EQUITY_RESEARCH;

-- Recreate if missing (run setup_all.sql)
```

**Error: "Semantic model not found"**

```bash
# Check if model is uploaded
snowsql -q "LIST @FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS;"

# Re-upload if missing
snowsql -q "PUT file://$(pwd)/config/financial_research_semantic_model.yaml @FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
```

**Error: "LLM rate limit exceeded"**

- Reduce number of debate rounds
- Use smaller model: `llama3.1-8b` instead of `llama3.1-70b`
- Add delays between requests

### Docker Issues

**Error: "Cannot connect to Docker daemon"**

```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

**Error: "Port 8501 already in use"**

```bash
# Find process using port
lsof -i :8501

# Kill process or use different port
docker-compose up -d -e STREAMLIT_PORT=8502
```

### Data Issues

**Error: "No data found for ticker"**

```bash
# Load sample data
snowsql -f sql/sample_data.sql

# Verify data exists
snowsql -q "SELECT DISTINCT TICKER FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.INVESTMENT_METRICS;"
```

---

## Extending the System

### Adding New Data Sources

1. **Create table** (add to `sql/setup_all.sql`):
   ```sql
   CREATE TABLE NEW_DATA_SOURCE (
       TICKER VARCHAR(10),
       DATA_DATE DATE,
       -- your columns
   );
   ```

2. **Update semantic model** (edit `config/financial_research_semantic_model.yaml`):
   ```yaml
   tables:
     - name: NEW_DATA_SOURCE
       description: "Your new data source"
       columns:
         - name: TICKER
           data_type: VARCHAR
   ```

3. **Create search service** (if unstructured):
   ```sql
   CREATE CORTEX SEARCH SERVICE NEW_DATA_SEARCH
   ON CONTENT_COLUMN
   WAREHOUSE = DEBATE_WH
   TARGET_LAG = '1 day'
   AS SELECT * FROM NEW_DATA_SOURCE;
   ```

4. **Update tools** to query new data source

### Customizing Agents

Edit agent prompts in `agents/` directory:

```python
# agents/bull_agent.py
class BullAgent(BaseAgent):
    @property
    def system_prompt(self) -> str:
        return """You are a BULLISH financial analyst...
        
        # Add custom instructions here
        """
```

### Adding New Analysis Types

Create new agent classes:

```python
# agents/risk_analyst.py
from agents.base import BaseAgent

class RiskAnalyst(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Risk Analyst",
            persona="Risk-focused analyst identifying potential downsides"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are a RISK ANALYST focused on identifying:
        - Regulatory risks
        - Competitive threats
        - Financial vulnerabilities
        - Market risks
        """
```

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

- Built with [Snowflake Cortex AI](https://www.snowflake.com/en/data-cloud/cortex/)
- Orchestration by [LangGraph](https://github.com/langchain-ai/langgraph)
- UI powered by [Streamlit](https://streamlit.io/)
