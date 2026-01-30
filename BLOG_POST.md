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

## Deep Dive: The Agent Implementation

Let's look at how the Bull Agent is implemented:

```python
class BullAgent(BaseAgent):
    """
    Bull agent - advocates for buying the stock.
    Focuses on growth potential, competitive advantages, and upside catalysts.
    """
    
    def __init__(self):
        super().__init__(
            name="Bull",
            persona="Optimistic investor focused on growth and opportunity"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are a BULLISH financial analyst in an investment debate.

Your role is to make the STRONGEST POSSIBLE CASE for BUYING this stock.

ARGUMENT STRATEGY:
1. GROWTH CATALYSTS: Identify revenue/earnings growth drivers
2. COMPETITIVE MOAT: Highlight sustainable advantages
3. VALUATION UPSIDE: Find reasons the stock is undervalued
4. POSITIVE MOMENTUM: Cite improving trends and sentiment
5. COUNTER BEAR ARGUMENTS: Directly refute bearish concerns

RULES:
- ONLY cite data from the research provided
- Be specific with numbers (P/E of 45x, revenue growth of 122%)
- Acknowledge risks but explain why they're manageable
- End with a clear, confident buy recommendation

Your goal is to PERSUADE the judge that this stock is a compelling buy."""
```

The key design principles:

1. **Clear Role Definition**: The agent knows it's arguing one side
2. **Structured Argumentation**: Five specific areas to address
3. **Data Grounding**: Must cite research data, not hallucinate
4. **Adversarial Awareness**: Must counter opponent's arguments
5. **Persuasion Goal**: Optimizing for convincing the judge

---

## Grounding in Real Data: The Research Phase

The magic happens in the Research phase, where we gather data from multiple Snowflake sources:

```python
class Researcher:
    def __init__(self):
        self.analyst = CortexAnalyst()  # Text-to-SQL
        self.search = CortexSearch()    # Semantic RAG
    
    def gather_research(self, ticker: str) -> ResearchData:
        research = ResearchData(ticker=ticker)
        
        # Structured data via Cortex Analyst
        research.metrics = self.analyst.get_metrics(ticker)
        research.earnings_history = self.analyst.get_earnings_history(ticker)
        research.technical_indicators = self.analyst.get_technical_indicators(ticker)
        research.sentiment = self.analyst.get_sentiment(ticker)
        
        # Unstructured data via Cortex Search
        research.analyst_reports = self.search.search_analyst_reports(
            f"{ticker} outlook growth risks",
            ticker=ticker,
            limit=5
        )
        research.earnings_transcripts = self.search.search_earnings_transcripts(
            f"{ticker} guidance outlook",
            ticker=ticker
        )
        
        return research
```

The Cortex Analyst wrapper generates SQL from natural language:

```python
class CortexAnalyst:
    def get_metrics(self, ticker: str) -> Dict[str, Any]:
        sql = f"""
        SELECT * FROM FINANCIAL_RESEARCH.EQUITY_RESEARCH.INVESTMENT_METRICS
        WHERE TICKER = '{ticker}'
        ORDER BY METRIC_DATE DESC
        LIMIT 1
        """
        results = self._execute_sql(sql)
        return results[0] if results else {}
```

And Cortex Search finds relevant documents semantically:

```python
class CortexSearch:
    def search_analyst_reports(self, query: str, ticker: str = None, limit: int = 5):
        search_query = {
            "query": query,
            "columns": ["REPORT_CONTENT", "REPORT_SUMMARY", "RATING", "PRICE_TARGET"],
            "filter": {"@eq": {"TICKER": ticker}} if ticker else {},
            "limit": limit
        }
        
        return self._execute_search("ANALYST_REPORTS_SEARCH", search_query)
```

---

## Orchestration with LangGraph

The debate flow is orchestrated using **LangGraph**, a framework for building stateful, multi-agent workflows:

```python
from langgraph.graph import StateGraph, END

def create_debate_graph() -> StateGraph:
    # Initialize agents
    researcher = Researcher()
    bull_agent = BullAgent()
    bear_agent = BearAgent()
    moderator = Moderator()
    judge = Judge()
    
    # Create the state graph
    graph = StateGraph(DebateState)
    
    # Add nodes
    graph.add_node("research", researcher)
    graph.add_node("bull", bull_agent)
    graph.add_node("bear", bear_agent)
    graph.add_node("moderator", moderator)
    graph.add_node("judge", judge)
    
    # Define flow
    graph.set_entry_point("research")
    graph.add_edge("research", "bull")
    graph.add_conditional_edges("bull", route_next_speaker)
    graph.add_conditional_edges("bear", route_next_speaker)
    graph.add_edge("judge", END)
    
    return graph.compile()
```

The state flows through each node, accumulating arguments and research data:

```python
class DebateState(TypedDict):
    ticker: str
    question: Optional[str]
    research_data: Optional[dict]
    current_round: int
    max_rounds: int
    current_speaker: Literal["research", "bull", "bear", "moderator", "judge"]
    arguments: Annotated[List[dict], add_arguments]  # Accumulates
    verdict: Optional[dict]
```

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
