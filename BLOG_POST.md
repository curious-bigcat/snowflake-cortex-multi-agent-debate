# Building a Multi-Agent AI Debate System for Stock Analysis with Snowflake Cortex

## How I built an AI system where Bull and Bear agents argue investment positions using competitive reasoning, grounded by real financial data

---

In the world of AI-powered financial analysis, one of the biggest challenges isn't getting AI to give you an answer — it's getting AI to give you a **balanced, well-reasoned** answer that considers multiple perspectives.

Large Language Models (LLMs) are notorious for **hallucinating facts**, exhibiting **confirmation bias**, and providing one-sided analysis. Ask an LLM "Should I buy NVIDIA stock?" and you'll likely get either an overly bullish or bearish response, depending on how you phrase the question.

What if we could force AI to argue **both sides** of an investment thesis, fact-check its own claims, and then have a neutral judge weigh the evidence?

That's exactly what I built: a **Multi-Agent Debate System** powered by **Snowflake Cortex AI**.

**GitHub Repository:** [snowflake-cortex-multi-agent-debate](https://github.com/curious-bigcat/snowflake-cortex-multi-agent-debate)

---

## The Problem with Single-Agent Financial Analysis

Traditional AI financial assistants have a fundamental flaw: they operate as a single voice providing a single perspective. This leads to several issues:

### 1. Confirmation Bias
If you ask "Why should I buy Tesla stock?", the AI will find reasons to buy. Ask "Why should I sell Tesla stock?", and it will find reasons to sell. The framing of your question determines the answer.

### 2. Hallucinated Facts
LLMs confidently cite statistics, earnings figures, and market data that may be outdated or completely fabricated. Without grounding in real data, these "facts" are unreliable.

### 3. Missing Counterarguments
A single-agent system rarely volunteers information that contradicts its thesis. It won't say "Here's why I might be wrong" unless explicitly asked.

### 4. No Accountability
With no one to challenge its claims, an AI can make sweeping statements without evidence. There's no adversarial pressure to be accurate.

---

## The Solution: Competitive Reasoning Through Debate

The solution draws inspiration from how humans make better decisions: **structured debate**.

In courtrooms, we have prosecution and defense. In academic research, we have peer review. In financial markets, we have bulls and bears. The collision of opposing viewpoints, each trying to make the strongest case, leads to better outcomes than any single perspective.

My Multi-Agent Debate System implements this pattern with five specialized AI agents:

| Agent | Role | Perspective |
|-------|------|-------------|
| 🔬 **Researcher** | Gathers data from multiple sources | Neutral — fact-finding only |
| 🐂 **Bull Agent** | Advocates for buying the stock | Optimistic — finds growth catalysts |
| 🐻 **Bear Agent** | Advocates against buying | Skeptical — identifies risks |
| ⚖️ **Moderator** | Fact-checks claims in real-time | Neutral — ensures accuracy |
| 👨‍⚖️ **Judge** | Weighs arguments and delivers verdict | Balanced — considers all evidence |

The key insight is that **agents are grounded in real data**. They can't make claims without evidence, and their opponents will call out any unsupported statements.

---

## Architecture: How It All Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Streamlit Web UI                            │
├─────────────────────────────────────────────────────────────────────┤
│                      LangGraph Orchestration                        │
│         State Machine: Research → Bull → Bear → Judge               │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│  Researcher  │  Bull Agent  │  Bear Agent  │   Judge Agent         │
├──────────────┴──────────────┴──────────────┴───────────────────────┤
│                      Snowflake Cortex AI                            │
│  ┌────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Cortex Analyst │  │  Cortex Search  │  │  Cortex Complete    │  │
│  │ (Text-to-SQL)  │  │  (Semantic RAG) │  │  (llama3.1-70b)     │  │
│  └────────────────┘  └─────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      Snowflake Data Layer                           │
│  Structured: Metrics, Earnings, Technicals, Sentiment               │
│  Unstructured: Analyst Reports, Transcripts, SEC Filings            │
└─────────────────────────────────────────────────────────────────────┘
```

The system leverages three powerful Snowflake Cortex AI capabilities:

### 1. Cortex Analyst (Text-to-SQL)
Converts natural language questions into SQL queries against structured financial data. When the Researcher agent asks "What is NVIDIA's P/E ratio?", Cortex Analyst generates and executes the appropriate SQL.

### 2. Cortex Search (Semantic RAG)
Performs semantic search across unstructured documents like analyst reports, earnings call transcripts, and SEC filings. This grounds agent arguments in qualitative insights, not just numbers.

### 3. Cortex Complete (LLM)
Powers the reasoning capabilities of each agent using `llama3.1-70b`. Each agent has a carefully crafted system prompt that defines its perspective and argumentation style.

---

## The Debate Flow

Here's how a typical debate unfolds:

```
START
  │
  ▼
┌─────────────┐
│  Researcher │ ──► Gathers P/E ratios, earnings history,
└─────────────┘     analyst reports, sentiment data
  │
  ▼
┌─────────────┐
│ Bull Agent  │ ──► "NVIDIA's 122% revenue growth and AI
└─────────────┘     dominance justify the premium valuation..."
  │
  ▼
┌─────────────┐
│ Moderator   │ ──► Verifies: ✓ Revenue growth accurate
└─────────────┘     Flags: ⚠️ Didn't mention China risk
  │
  ▼
┌─────────────┐
│ Bear Agent  │ ──► "At 65x P/E, NVIDIA is priced for perfection.
└─────────────┘     Any demand slowdown could trigger a 40% decline..."
  │
  ▼
┌─────────────┐
│ Moderator   │ ──► Verifies: ✓ P/E ratio accurate
└─────────────┘     Flags: ⚠️ Ignored margin expansion
  │
  ▼ (Repeat for N rounds)
  │
┌─────────────┐
│   Judge     │ ──► Weighs arguments, scores each side,
└─────────────┘     delivers: "BUY with 72% confidence"
  │
  ▼
 END
```

Each round forces agents to respond to their opponent's strongest points. The Bear can't ignore the Bull's growth argument, and the Bull can't ignore the Bear's valuation concern.

---

## Deep Dive: Building the System End-to-End

Now let's go deep into how each component was built, from the Snowflake data layer all the way to the Docker runtime.

### Part 1: Snowflake Data Foundation

Everything starts with data. I designed a comprehensive financial data model in Snowflake with 11 tables split across two categories:

**Structured Data Tables** (for Cortex Analyst):

```sql
-- Core financial metrics for valuation analysis
CREATE TABLE INVESTMENT_METRICS (
    TICKER VARCHAR(10),
    COMPANY_NAME VARCHAR(200),
    METRIC_DATE DATE,
    -- Valuation ratios
    PE_RATIO FLOAT,
    FORWARD_PE FLOAT,
    PEG_RATIO FLOAT,
    PRICE_TO_BOOK FLOAT,
    PRICE_TO_SALES FLOAT,
    EV_TO_EBITDA FLOAT,
    -- Profitability metrics
    ROE_PCT FLOAT,
    ROA_PCT FLOAT,
    GROSS_MARGIN_PCT FLOAT,
    OPERATING_MARGIN_PCT FLOAT,
    NET_MARGIN_PCT FLOAT,
    -- Financial health
    DEBT_TO_EQUITY FLOAT,
    CURRENT_RATIO FLOAT,
    -- Growth metrics
    REVENUE_GROWTH_YOY_PCT FLOAT,
    EARNINGS_GROWTH_YOY_PCT FLOAT,
    -- Size metrics
    MARKET_CAP_BILLIONS FLOAT,
    ENTERPRISE_VALUE_BILLIONS FLOAT
);

-- Historical earnings for trend analysis
CREATE TABLE EARNINGS_HISTORY (
    TICKER VARCHAR(10),
    FISCAL_QUARTER VARCHAR(10),
    FISCAL_YEAR INTEGER,
    REPORT_DATE DATE,
    EPS_ACTUAL FLOAT,
    EPS_ESTIMATE FLOAT,
    EPS_SURPRISE_PCT FLOAT,
    REVENUE_ACTUAL_MILLIONS FLOAT,
    REVENUE_ESTIMATE_MILLIONS FLOAT,
    BEAT_MISS VARCHAR(10)  -- 'BEAT', 'MISS', 'MEET'
);

-- Technical indicators for momentum analysis
CREATE TABLE TECHNICAL_INDICATORS (
    TICKER VARCHAR(10),
    INDICATOR_DATE DATE,
    CLOSE_PRICE FLOAT,
    SMA_20 FLOAT,
    SMA_50 FLOAT,
    SMA_200 FLOAT,
    RSI_14 FLOAT,
    RSI_SIGNAL VARCHAR(20),  -- 'OVERBOUGHT', 'OVERSOLD', 'NEUTRAL'
    MACD FLOAT,
    MACD_SIGNAL FLOAT
);

-- Market sentiment from news and social media
CREATE TABLE MARKET_SENTIMENT (
    TICKER VARCHAR(10),
    SENTIMENT_DATE DATE,
    NEWS_SENTIMENT_SCORE FLOAT,      -- -1 to 1
    SOCIAL_MEDIA_SENTIMENT_SCORE FLOAT,
    OVERALL_SENTIMENT VARCHAR(20),   -- 'VERY_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH'
    BULLISH_PCT FLOAT,
    BEARISH_PCT FLOAT,
    ANALYST_RATING_AVG FLOAT,        -- 1-5 scale
    PRICE_TARGET_AVG FLOAT
);
```

**Unstructured Data Tables** (for Cortex Search):

```sql
-- Analyst reports with full text content
CREATE TABLE ANALYST_REPORTS (
    REPORT_ID VARCHAR(50),
    TICKER VARCHAR(10),
    COMPANY_NAME VARCHAR(200),
    FIRM VARCHAR(100),
    ANALYST_NAME VARCHAR(100),
    REPORT_DATE DATE,
    REPORT_TITLE VARCHAR(500),
    REPORT_TYPE VARCHAR(50),
    RATING VARCHAR(50),
    PRICE_TARGET FLOAT,
    REPORT_SUMMARY TEXT,
    REPORT_CONTENT TEXT  -- Full report text for semantic search
);

-- Earnings call transcripts
CREATE TABLE EARNINGS_TRANSCRIPTS (
    TRANSCRIPT_ID VARCHAR(50),
    TICKER VARCHAR(10),
    CALL_DATE TIMESTAMP,
    FISCAL_QUARTER VARCHAR(10),
    CEO_NAME VARCHAR(100),
    CFO_NAME VARCHAR(100),
    TRANSCRIPT_TITLE VARCHAR(500),
    TRANSCRIPT_SUMMARY TEXT,
    TRANSCRIPT_CONTENT TEXT,  -- Full transcript for semantic search
    OVERALL_TONE VARCHAR(20)
);

-- SEC filings (10-K, 10-Q, 8-K)
CREATE TABLE SEC_FILINGS (
    FILING_ID VARCHAR(50),
    TICKER VARCHAR(10),
    FILING_TYPE VARCHAR(20),
    FILING_DATE DATE,
    PERIOD_END_DATE DATE,
    FILING_CONTENT TEXT  -- Extracted text for semantic search
);
```

This schema design ensures agents have access to both **quantitative data** (numbers, ratios, trends) and **qualitative data** (management commentary, analyst opinions, risk disclosures).

---

### Part 2: Cortex Search Services for RAG

To enable semantic search over unstructured documents, I created **Cortex Search Services**:

```sql
-- Create search service for analyst reports
CREATE OR REPLACE CORTEX SEARCH SERVICE ANALYST_REPORTS_SEARCH
    ON REPORT_CONTENT
    ATTRIBUTES TICKER, COMPANY_NAME, FIRM, RATING, PRICE_TARGET, REPORT_DATE
    WAREHOUSE = DEBATE_WH
    TARGET_LAG = '1 day'
AS (
    SELECT 
        REPORT_ID,
        TICKER,
        COMPANY_NAME,
        FIRM,
        ANALYST_NAME,
        REPORT_DATE,
        REPORT_TITLE,
        RATING,
        PRICE_TARGET,
        REPORT_SUMMARY,
        REPORT_CONTENT
    FROM ANALYST_REPORTS
    WHERE REPORT_CONTENT IS NOT NULL
);

-- Create search service for earnings transcripts
CREATE OR REPLACE CORTEX SEARCH SERVICE EARNINGS_TRANSCRIPTS_SEARCH
    ON TRANSCRIPT_CONTENT
    ATTRIBUTES TICKER, COMPANY_NAME, FISCAL_QUARTER, FISCAL_YEAR, OVERALL_TONE
    WAREHOUSE = DEBATE_WH
    TARGET_LAG = '1 day'
AS (
    SELECT 
        TRANSCRIPT_ID,
        TICKER,
        COMPANY_NAME,
        CALL_DATE,
        FISCAL_QUARTER,
        FISCAL_YEAR,
        CEO_NAME,
        TRANSCRIPT_TITLE,
        TRANSCRIPT_SUMMARY,
        TRANSCRIPT_CONTENT,
        OVERALL_TONE
    FROM EARNINGS_TRANSCRIPTS
    WHERE TRANSCRIPT_CONTENT IS NOT NULL
);
```

The `ON REPORT_CONTENT` clause tells Cortex Search which column to build the semantic index on. The `ATTRIBUTES` clause specifies filterable metadata columns. When an agent searches for "NVDA growth outlook", Cortex Search:

1. Converts the query to a vector embedding
2. Finds semantically similar documents
3. Returns results with metadata for filtering

---

### Part 3: Semantic Model for Cortex Analyst

To enable natural language queries over structured data, I created a **semantic model** — a YAML file that teaches Cortex Analyst about our schema:

```yaml
name: financial_research_semantic_model
description: Semantic model for investment research and stock analysis

tables:
  - name: INVESTMENT_METRICS
    description: >
      Current valuation ratios, profitability metrics, and financial health 
      indicators for publicly traded companies. Use this for P/E ratio, 
      ROE, debt levels, and growth rates.
    base_table:
      database: FINANCIAL_RESEARCH
      schema: EQUITY_RESEARCH
      table: INVESTMENT_METRICS
    
    dimensions:
      - name: ticker
        expr: TICKER
        description: Stock ticker symbol (e.g., NVDA, AAPL)
        unique: true
      - name: company_name
        expr: COMPANY_NAME
        description: Full company name
    
    time_dimensions:
      - name: metric_date
        expr: METRIC_DATE
        description: Date of the metrics snapshot
    
    measures:
      - name: pe_ratio
        expr: PE_RATIO
        description: Price-to-Earnings ratio (trailing 12 months)
      - name: forward_pe
        expr: FORWARD_PE
        description: Forward P/E based on next year estimates
      - name: roe_pct
        expr: ROE_PCT
        description: Return on Equity percentage
      - name: revenue_growth_yoy_pct
        expr: REVENUE_GROWTH_YOY_PCT
        description: Year-over-year revenue growth percentage
      - name: debt_to_equity
        expr: DEBT_TO_EQUITY
        description: Debt-to-Equity ratio
      - name: market_cap_billions
        expr: MARKET_CAP_BILLIONS
        description: Market capitalization in billions USD

  - name: EARNINGS_HISTORY
    description: >
      Historical quarterly earnings results including EPS actuals vs estimates,
      revenue figures, and beat/miss status. Use for earnings trends.
    # ... similar structure

# Verified queries help Cortex Analyst understand intent
verified_queries:
  - name: get_stock_valuation
    question: "What is the P/E ratio for NVDA?"
    sql: >
      SELECT TICKER, PE_RATIO, FORWARD_PE, PEG_RATIO 
      FROM INVESTMENT_METRICS 
      WHERE TICKER = 'NVDA'
      ORDER BY METRIC_DATE DESC LIMIT 1
    
  - name: compare_growth_rates
    question: "Which stocks have the highest revenue growth?"
    sql: >
      SELECT TICKER, COMPANY_NAME, REVENUE_GROWTH_YOY_PCT
      FROM INVESTMENT_METRICS
      ORDER BY REVENUE_GROWTH_YOY_PCT DESC
      LIMIT 10
    
  - name: earnings_beats
    question: "How many quarters did AAPL beat earnings estimates?"
    sql: >
      SELECT COUNT(*) as beat_count
      FROM EARNINGS_HISTORY
      WHERE TICKER = 'AAPL' AND BEAT_MISS = 'BEAT'
```

The semantic model is uploaded to a Snowflake stage and referenced by Cortex Analyst:

```bash
# Upload to stage
PUT file://config/financial_research_semantic_model.yaml \
    @FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS \
    AUTO_COMPRESS=FALSE;
```

---

### Part 4: Cortex AI Tool Wrappers

I built Python wrapper classes that abstract the Snowflake Cortex APIs:

**CortexAnalyst** — Text-to-SQL for structured data:

```python
class CortexAnalyst:
    """Wrapper for Snowflake Cortex Analyst text-to-SQL."""
    
    def __init__(self, semantic_model_path: str = None):
        self.semantic_model_path = semantic_model_path or \
            "@FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS/financial_research_semantic_model.yaml"
        self._connection = None
        self.query_log = []  # Track queries for debugging
    
    def _get_connection(self):
        """Lazy connection using ~/.snowflake/config.toml credentials."""
        if self._connection is None:
            self._connection = snowflake.connector.connect(
                connection_name="default"  # Uses config.toml
            )
        return self._connection
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a natural language question, get SQL + results.
        
        Cortex Analyst converts the question to SQL using the semantic model,
        then executes the SQL and returns structured results.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Call Cortex Analyst via SQL function
        sql = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'analyst',
            OBJECT_CONSTRUCT(
                'semantic_model', '{self.semantic_model_path}',
                'question', '{question.replace("'", "''")}'
            )
        ) as response
        """
        
        cursor.execute(sql)
        result = cursor.fetchone()
        response = json.loads(result[0])
        
        generated_sql = response.get("sql", "")
        
        # Execute the generated SQL
        if generated_sql:
            cursor.execute(generated_sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            
            # Log for debugging
            self._log_query("analyst", generated_sql, results)
            
            return {
                "question": question,
                "sql": generated_sql,
                "results": results
            }
        
        return {"question": question, "sql": "", "results": []}
    
    def get_metrics(self, ticker: str) -> Dict[str, Any]:
        """Direct SQL query for investment metrics."""
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.INVESTMENT_METRICS
        WHERE TICKER = '{ticker}'
        ORDER BY METRIC_DATE DESC
        LIMIT 1
        """
        return self._execute_sql(sql, "get_metrics")
```

**CortexSearch** — Semantic search for unstructured data:

```python
class CortexSearch:
    """Wrapper for Snowflake Cortex Search semantic retrieval."""
    
    SEARCH_SERVICES = {
        "analyst_reports": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.ANALYST_REPORTS_SEARCH",
        "earnings_transcripts": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.EARNINGS_TRANSCRIPTS_SEARCH",
        "sec_filings": "FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEC_FILINGS_SEARCH",
    }
    
    def search_analyst_reports(
        self, 
        query: str, 
        ticker: str = None, 
        limit: int = 5
    ) -> List[Dict]:
        """
        Semantic search over analyst reports.
        
        Args:
            query: Natural language search query
            ticker: Optional filter by stock ticker
            limit: Maximum results to return
        """
        service = self.SEARCH_SERVICES["analyst_reports"]
        
        # Build Cortex Search query
        search_sql = f"""
        SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
            '{service}',
            OBJECT_CONSTRUCT(
                'query', '{query.replace("'", "''")}',
                'columns', ARRAY_CONSTRUCT(
                    'REPORT_CONTENT', 'REPORT_SUMMARY', 
                    'RATING', 'PRICE_TARGET', 'FIRM', 'TICKER'
                ),
                'filter', {{"@eq": {{"TICKER": "{ticker}"}}}} if ticker else {{}},
                'limit', {limit}
            )
        ) as results
        """
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(search_sql)
        
        result = cursor.fetchone()
        documents = json.loads(result[0]).get("results", [])
        
        # Log for debugging
        self._log_query("search", service, {"query": query, "ticker": ticker}, documents)
        
        return documents
    
    def search_all(self, ticker: str, query: str) -> Dict[str, List]:
        """Search across all document types for comprehensive research."""
        return {
            "analyst_reports": self.search_analyst_reports(query, ticker),
            "earnings_transcripts": self.search_earnings_transcripts(query, ticker),
            "sec_filings": self.search_sec_filings(query, ticker),
        }
```

**CortexLLM** — LLM completions for agent reasoning:

```python
class CortexLLM:
    """Wrapper for Snowflake Cortex Complete LLM."""
    
    def __init__(self, model: str = "llama3.1-70b"):
        self.model = model
        self._connection = None
    
    def complete(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate LLM completion using Cortex Complete.
        
        This powers all agent reasoning - the Bull making arguments,
        the Bear crafting rebuttals, the Judge weighing evidence.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build messages array for chat completion
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Call Cortex Complete
        sql = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{self.model}',
            {json.dumps(messages)},
            OBJECT_CONSTRUCT(
                'temperature', {temperature},
                'max_tokens', {max_tokens}
            )
        ) as response
        """
        
        cursor.execute(sql)
        result = cursor.fetchone()
        
        # Parse response
        response_data = json.loads(result[0])
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
```

---

### Part 5: Agent Architecture

Each agent inherits from a `BaseAgent` class that provides LLM access and common utilities:

```python
class BaseAgent:
    """Base class for all debate agents."""
    
    def __init__(self, name: str, persona: str):
        self.name = name
        self.persona = persona
        self.llm = CortexLLM(model="llama3.1-70b")
    
    @property
    def system_prompt(self) -> str:
        """Override in subclasses to define agent personality."""
        raise NotImplementedError
    
    def format_research_context(self, research_data: dict) -> str:
        """Format research data as context for LLM prompt."""
        context_parts = []
        
        # Format metrics
        if metrics := research_data.get("metrics", {}):
            context_parts.append(f"""
FINANCIAL METRICS:
- P/E Ratio: {metrics.get('PE_RATIO', 'N/A')}
- Forward P/E: {metrics.get('FORWARD_PE', 'N/A')}
- ROE: {metrics.get('ROE_PCT', 'N/A')}%
- Revenue Growth: {metrics.get('REVENUE_GROWTH_YOY_PCT', 'N/A')}%
- Debt/Equity: {metrics.get('DEBT_TO_EQUITY', 'N/A')}
""")
        
        # Format earnings history
        if earnings := research_data.get("earnings_history", []):
            context_parts.append("RECENT EARNINGS:")
            for e in earnings[:4]:
                context_parts.append(
                    f"  {e.get('FISCAL_QUARTER')} FY{e.get('FISCAL_YEAR')}: "
                    f"EPS ${e.get('EPS_ACTUAL')} vs ${e.get('EPS_ESTIMATE')} est "
                    f"({e.get('BEAT_MISS')})"
                )
        
        # Format analyst reports (from Cortex Search)
        if reports := research_data.get("analyst_reports", []):
            context_parts.append("\nANALYST REPORTS:")
            for r in reports[:3]:
                context_parts.append(
                    f"  [{r.get('FIRM')}] {r.get('RATING')} - "
                    f"PT ${r.get('PRICE_TARGET')}: {r.get('REPORT_SUMMARY', '')[:200]}..."
                )
        
        return "\n".join(context_parts)
    
    def generate_argument(
        self, 
        state: DebateState, 
        opponent_argument: str = None
    ) -> Argument:
        """Generate an argument using Cortex Complete."""
        research_context = self.format_research_context(state.get("research_data", {}))
        
        prompt = f"""STOCK: {state['ticker']}
QUESTION: {state['question']}

RESEARCH DATA:
{research_context}

{"OPPONENT'S ARGUMENT TO COUNTER:" + chr(10) + opponent_argument if opponent_argument else ""}

Generate your argument:"""
        
        response = self.llm.complete(prompt, system_prompt=self.system_prompt)
        
        return Argument(
            agent=self.name.lower(),
            content=response,
            confidence=self._extract_confidence(response)
        )
```

The **Bull Agent** specializes this for optimistic analysis:

```python
class BullAgent(BaseAgent):
    """Bull agent - advocates for buying the stock."""
    
    def __init__(self):
        super().__init__(
            name="Bull",
            persona="Optimistic growth investor"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are a BULLISH financial analyst in an investment debate.

Your role is to make the STRONGEST POSSIBLE CASE for BUYING this stock.

ARGUMENT STRATEGY:
1. GROWTH CATALYSTS: Highlight revenue/earnings growth drivers
2. COMPETITIVE MOAT: Emphasize sustainable competitive advantages  
3. VALUATION UPSIDE: Argue why current price undervalues the company
4. POSITIVE MOMENTUM: Cite improving trends, sentiment, analyst upgrades
5. COUNTER BEAR ARGUMENTS: Directly refute bearish concerns with evidence

RULES:
- ONLY cite data from the research provided - no hallucinating numbers
- Be specific: "P/E of 45x" not "reasonable valuation"
- Acknowledge risks but explain why they're manageable
- End with a clear, confident buy recommendation

Your goal is to PERSUADE the judge. Be compelling but factual."""
    
    def __call__(self, state: DebateState) -> Dict[str, Any]:
        """LangGraph node function."""
        # Get opponent's last argument for rebuttal
        opponent_arg = None
        for arg in reversed(state.get("arguments", [])):
            if arg.get("agent") == "bear":
                opponent_arg = arg.get("content")
                break
        
        argument = self.generate_argument(state, opponent_arg)
        
        return {
            "arguments": [argument.to_dict()],
            "current_speaker": "moderator",
        }
```

The **Bear Agent** mirrors this with a skeptical lens:

```python
class BearAgent(BaseAgent):
    """Bear agent - advocates against buying."""
    
    @property
    def system_prompt(self) -> str:
        return """You are a BEARISH financial analyst in an investment debate.

Your role is to make the STRONGEST POSSIBLE CASE AGAINST buying this stock.

ARGUMENT STRATEGY:
1. VALUATION CONCERNS: Highlight overvaluation risks (high P/E, P/S)
2. GROWTH RISKS: Question sustainability of growth rates
3. COMPETITIVE THREATS: Identify emerging competition, disruption risks
4. FINANCIAL WEAKNESSES: Point out debt, margin pressure, cash flow issues
5. COUNTER BULL ARGUMENTS: Directly refute bullish claims with evidence

RULES:
- ONLY cite data from the research provided - no hallucinating numbers
- Be specific: "At 65x P/E, the stock is priced for perfection"
- Present risks as material, not theoretical
- End with a clear recommendation to avoid or sell

Your goal is to PERSUADE the judge. Be compelling but factual."""
```

The **Judge Agent** synthesizes both perspectives:

```python
class Judge(BaseAgent):
    """Judge agent - delivers final verdict."""
    
    @property
    def system_prompt(self) -> str:
        return """You are an impartial JUDGE evaluating an investment debate.

Your role is to:
1. SCORE both Bull and Bear arguments (0-100 each)
2. IDENTIFY the strongest points from each side
3. WEIGH the evidence objectively
4. DELIVER a final recommendation: STRONG BUY, BUY, HOLD, SELL, or STRONG SELL
5. EXPLAIN your reasoning with specific reference to the arguments

Be fair, balanced, and grounded in the evidence presented."""
    
    def __call__(self, state: DebateState) -> Dict[str, Any]:
        # Compile all arguments for evaluation
        bull_args = [a for a in state["arguments"] if a["agent"] == "bull"]
        bear_args = [a for a in state["arguments"] if a["agent"] == "bear"]
        
        prompt = f"""INVESTMENT DEBATE JUDGMENT

STOCK: {state['ticker']}
QUESTION: {state['question']}

BULL'S ARGUMENTS:
{self._format_arguments(bull_args)}

BEAR'S ARGUMENTS:
{self._format_arguments(bear_args)}

RESEARCH DATA:
{self.format_research_context(state.get('research_data', {}))}

Deliver your verdict in this format:
BULL_SCORE: [0-100]
BEAR_SCORE: [0-100]
RECOMMENDATION: [STRONG BUY/BUY/HOLD/SELL/STRONG SELL]
CONFIDENCE: [0.0-1.0]
SUMMARY: [Your reasoning]"""
        
        response = self.llm.complete(prompt, system_prompt=self.system_prompt)
        verdict = self._parse_verdict(response)
        
        return {
            "verdict": verdict,
            "arguments": [Argument(agent="judge", content=response).to_dict()],
            "current_speaker": "end",
        }
```

---

### Part 6: LangGraph Orchestration

**LangGraph** is the orchestration framework that manages state flow between agents. Unlike simple sequential pipelines, LangGraph enables:

- **Stateful execution**: State persists and accumulates across nodes
- **Conditional routing**: Dynamic flow based on state
- **Cycles**: Agents can interact multiple rounds

```python
from langgraph.graph import StateGraph, END
from typing import Literal

def create_debate_graph() -> StateGraph:
    """Build the multi-agent debate workflow."""
    
    # Initialize agents (each becomes a graph node)
    researcher = Researcher()
    bull_agent = BullAgent()
    bear_agent = BearAgent()
    moderator = Moderator()
    judge = Judge()
    
    # Create graph with typed state
    graph = StateGraph(DebateState)
    
    # Add nodes (each agent is a node)
    graph.add_node("research", researcher)
    graph.add_node("bull", bull_agent)
    graph.add_node("bear", bear_agent)
    graph.add_node("moderator", moderator)
    graph.add_node("judge", judge)
    
    # Entry point: always start with research
    graph.set_entry_point("research")
    
    # Research → Bull (first argument)
    graph.add_edge("research", "bull")
    
    # Conditional routing based on debate state
    def route_after_bull(state: DebateState) -> Literal["moderator", "judge"]:
        """Route after Bull's argument."""
        if state["current_round"] >= state["max_rounds"]:
            return "judge"
        return "moderator"
    
    def route_after_moderator(state: DebateState) -> Literal["bull", "bear", "judge"]:
        """Route after Moderator's fact-check."""
        speaker = state.get("current_speaker", "bear")
        if speaker == "judge":
            return "judge"
        return speaker
    
    def route_after_bear(state: DebateState) -> Literal["moderator", "judge"]:
        """Route after Bear's argument."""
        if state["current_round"] >= state["max_rounds"]:
            return "judge"
        return "moderator"
    
    # Add conditional edges
    graph.add_conditional_edges("bull", route_after_bull)
    graph.add_conditional_edges("moderator", route_after_moderator)
    graph.add_conditional_edges("bear", route_after_bear)
    
    # Judge always ends the graph
    graph.add_edge("judge", END)
    
    # Compile to executable graph
    return graph.compile()
```

The **DebateState** is a TypedDict that flows through all nodes:

```python
from typing import TypedDict, List, Optional, Annotated, Literal
import operator

def add_arguments(left: List[dict], right: List[dict]) -> List[dict]:
    """Reducer: append new arguments to existing list."""
    return left + right

class DebateState(TypedDict):
    """Shared state for the debate workflow."""
    
    # Input
    ticker: str
    question: Optional[str]
    
    # Research data (populated by Researcher)
    research_data: Optional[dict]
    
    # Debate flow control
    current_round: int
    max_rounds: int
    current_speaker: Literal["research", "bull", "bear", "moderator", "judge", "end"]
    
    # Argument history (uses reducer to accumulate)
    arguments: Annotated[List[dict], add_arguments]
    
    # Final verdict (populated by Judge)
    verdict: Optional[dict]
    
    # Debug logs
    _analyst_log: Optional[List[dict]]
    _search_log: Optional[List[dict]]
```

The `Annotated[List[dict], add_arguments]` syntax tells LangGraph to **accumulate** arguments rather than replace them — essential for building debate history.

---

### Part 7: Docker Containerization

The entire application is containerized for easy deployment:

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  debate-app:
    build: .
    container_name: multi-agent-debate
    ports:
      - "8501:8501"
    volumes:
      # Mount Snowflake credentials (read-only)
      - ~/.snowflake:/root/.snowflake:ro
    environment:
      - SNOWFLAKE_DEFAULT_CONNECTION_NAME=default
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

The key insight is mounting `~/.snowflake` as a read-only volume — this lets the container use your local Snowflake credentials without baking secrets into the image.

**Makefile** for convenience:

```makefile
.PHONY: build run stop logs shell clean

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker exec -it multi-agent-debate /bin/bash

clean:
	docker-compose down -v --rmi all
```

---

### Part 8: Streamlit UI with Debug View

The Streamlit app streams debate events in real-time and provides a **debug view** showing all Cortex queries:

```python
def run_debate(ticker: str, rounds: int, question: str = None):
    """Run debate and stream results to UI."""
    from graph.workflow import create_simple_debate_graph
    from graph.state import create_initial_state
    
    initial_state = create_initial_state(
        ticker=ticker,
        question=question,
        max_rounds=rounds,
    )
    
    graph = create_simple_debate_graph()
    
    results = {
        "ticker": ticker,
        "arguments": [],
        "verdict": None,
        "query_logs": {"analyst": [], "search": []},
    }
    
    # Stream graph execution
    for event in graph.stream(initial_state):
        for node_name, node_output in event.items():
            if node_name == "research":
                results["research_data"] = node_output.get("research_data")
                # Capture query logs for debug view
                results["query_logs"]["analyst"] = node_output.get("_analyst_log", [])
                results["query_logs"]["search"] = node_output.get("_search_log", [])
                yield {"type": "research", "data": results["research_data"]}
                
            elif node_name == "bull":
                args = node_output.get("arguments", [])
                results["arguments"].extend(args)
                yield {"type": "bull", "data": args[-1]}
                
            elif node_name == "bear":
                args = node_output.get("arguments", [])
                results["arguments"].extend(args)
                yield {"type": "bear", "data": args[-1]}
                
            elif node_name == "judge":
                results["verdict"] = node_output.get("verdict")
                yield {"type": "judge", "data": results["verdict"]}
    
    yield {"type": "complete", "data": results}
```

The debug view renders query logs as expandable sections:

```python
def display_query_logs(query_logs: dict):
    """Render Cortex query logs in debug panel."""
    
    analyst_logs = query_logs.get("analyst", [])
    if analyst_logs:
        st.markdown("#### Cortex Analyst Queries")
        for log in analyst_logs:
            with st.expander(f"{log['type']} - {log['timestamp'][:19]}"):
                st.markdown("**Generated SQL:**")
                st.code(log.get("sql", "N/A"), language="sql")
                
                st.markdown("**Results:**")
                st.dataframe(log.get("results", []))
    
    search_logs = query_logs.get("search", [])
    if search_logs:
        st.markdown("#### Cortex Search Queries")
        for log in search_logs:
            with st.expander(f"{log['type']} - {log['timestamp'][:19]}"):
                st.markdown(f"**Service:** `{log.get('service')}`")
                st.markdown(f"**Query:** {log.get('request', {}).get('query')}")
                st.markdown(f"**Results:** {len(log.get('results', []))} documents")
```

This transparency lets users verify that agents are citing real data, not hallucinating.

---

## The Streamlit Interface

The web UI provides real-time visibility into the debate:

Key features:

1. **Live Streaming**: Watch arguments appear as they're generated
2. **Research Summary**: See the data agents are working with
3. **Debug View**: Inspect raw SQL queries and search requests
4. **Verdict Display**: Clear recommendation with confidence score

The debug view is particularly useful for understanding how agents ground their arguments:

```
┌─────────────────────────────────────────────────────┐
│ Debug View: Raw Queries & Data                      │
├─────────────────────────────────────────────────────┤
│ ▼ Cortex Analyst Queries                           │
│   ├─ get_metrics - 2024-01-30T10:23:45            │
│   │   SQL: SELECT * FROM INVESTMENT_METRICS...     │
│   │   Results: PE_RATIO: 65.2, ROE_PCT: 85.2...   │
│   ├─ get_earnings_history - 2024-01-30T10:23:46   │
│   │   SQL: SELECT * FROM EARNINGS_HISTORY...       │
│   └─ ...                                           │
│                                                     │
│ ▼ Cortex Search Queries                            │
│   ├─ analyst_reports - 2024-01-30T10:23:47        │
│   │   Service: ANALYST_REPORTS_SEARCH              │
│   │   Query: "NVDA outlook growth risks"           │
│   │   Results: 5 documents                         │
│   └─ ...                                           │
└─────────────────────────────────────────────────────┘
```

---

## Setting Up Your Own Instance

### Prerequisites

- Snowflake account with Cortex AI enabled
- Docker and Docker Compose
- Snowflake CLI configured

### Step 1: Clone the Repository

```bash
git clone https://github.com/curious-bigcat/snowflake-cortex-multi-agent-debate.git
cd snowflake-cortex-multi-agent-debate
```

### Step 2: Set Up Snowflake Objects

```bash
# Create database, tables, and search services
snowsql -f sql/setup_all.sql

# Upload the semantic model for Cortex Analyst
snowsql -q "PUT file://config/financial_research_semantic_model.yaml \
  @FINANCIAL_RESEARCH.EQUITY_RESEARCH.SEMANTIC_MODELS \
  AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

# Load sample data
snowsql -f sql/sample_data.sql
```

### Step 3: Run with Docker

```bash
# Build and start
docker-compose up -d --build

# Access at http://localhost:8501
```

That's it! You now have a fully functional multi-agent debate system.

---

## Results and Observations

After running dozens of debates across different stocks, here are my observations:

### What Works Well

1. **Balanced Analysis**: The debate format consistently produces more nuanced recommendations than single-agent systems

2. **Reduced Hallucinations**: Grounding in Cortex Analyst and Search dramatically reduces made-up statistics

3. **Transparent Reasoning**: The argument structure makes it clear *why* the system reached its conclusion

4. **Educational Value**: Watching the debate unfold teaches you to think about stocks from multiple angles

### Interesting Patterns

- **High-momentum stocks** (like NVDA) generate the most vigorous debates, with strong arguments on both sides

- **Value stocks** often see the Bear struggle to find compelling sell arguments beyond "it's boring"

- **Controversial stocks** (like TSLA) produce the longest debates, with neither side able to definitively win

### Limitations

- **Data dependency**: The system is only as good as the underlying data. Empty tables = weak arguments

- **LLM consistency**: Sometimes agents make the same point multiple times or miss obvious counterarguments

- **No real-time data**: The system uses historical data, not live market feeds

---

## Future Enhancements

Here's what I'm planning to add:

### 1. Real-Time Data Integration
Connect to live market data APIs for up-to-the-minute analysis.

### 2. Specialized Agents
Add domain-specific agents like:
- **Technical Analyst**: Focuses purely on chart patterns
- **Macro Analyst**: Considers broader economic factors
- **Risk Manager**: Quantifies downside scenarios

### 3. Portfolio Context
Allow the system to consider your existing holdings when making recommendations.

### 4. Historical Backtesting
Track recommendations over time to measure accuracy.

### 5. Multi-Stock Comparison
Enable debates comparing multiple investment options.

---

## Conclusion

The Multi-Agent Debate System demonstrates a powerful pattern for AI-assisted decision making: **competitive reasoning with data grounding**.

By forcing AI agents to argue opposing positions and cite real evidence, we get:

- More balanced analysis
- Fewer hallucinations
- Transparent reasoning
- Better decisions

This pattern isn't limited to financial analysis. It could apply to:

- **Legal research**: Prosecution vs. Defense perspectives
- **Product decisions**: Build vs. Buy debates
- **Medical diagnosis**: Differential diagnosis through debate
- **Policy analysis**: Pro vs. Con arguments

The code is open source and ready for you to experiment with. I'd love to see what you build on top of it.

**GitHub:** [snowflake-cortex-multi-agent-debate](https://github.com/curious-bigcat/snowflake-cortex-multi-agent-debate)

---

*If you found this useful, give the repo a ⭐ and follow me for more AI engineering content.*

*Have questions or ideas? Drop a comment below or open an issue on GitHub.*

---

### Tags
`#AI` `#MachineLearning` `#Snowflake` `#LLM` `#MultiAgent` `#FinancialAnalysis` `#Python` `#LangGraph` `#CortexAI`
