"""
Multi-Agent Debate System - Streamlit App

A financial analysis tool that uses Bull and Bear agents to debate
investment decisions, grounded by Snowflake Cortex AI services.
"""
import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Bull vs Bear Debate",
    page_icon="🐂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "debate_history" not in st.session_state:
    st.session_state.debate_history = []
if "current_debate" not in st.session_state:
    st.session_state.current_debate = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "show_debug" not in st.session_state:
    st.session_state.show_debug = False


def get_snowflake_connection():
    """Get Snowflake connection using st.connection or fallback."""
    try:
        return st.connection("snowflake")
    except Exception:
        from config import get_snowflake_connection as get_conn
        return get_conn()


def run_debate(ticker: str, rounds: int, question: str = None):
    """Run the debate and stream results."""
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
        "question": question or f"Should we buy or sell {ticker}?",
        "rounds": rounds,
        "arguments": [],
        "verdict": None,
        "research_data": None,
        "query_logs": {"analyst": [], "search": []},
        "timestamp": datetime.now().isoformat(),
    }
    
    for event in graph.stream(initial_state):
        for node_name, node_output in event.items():
            if node_output:
                if node_name == "research":
                    results["research_data"] = node_output.get("research_data", {})
                    # Capture query logs from research phase
                    analyst_log = node_output.get("_analyst_log", [])
                    search_log = node_output.get("_search_log", [])
                    if analyst_log:
                        results["query_logs"]["analyst"].extend(analyst_log)
                    if search_log:
                        results["query_logs"]["search"].extend(search_log)
                    yield {"type": "research", "data": results["research_data"]}
                    
                elif node_name in ["bull_1", "bull_2", "bull"]:
                    args = node_output.get("arguments", [])
                    if args:
                        results["arguments"].extend(args)
                        yield {"type": "bull", "data": args[-1]}
                        
                elif node_name in ["bear_1", "bear_2", "bear"]:
                    args = node_output.get("arguments", [])
                    if args:
                        results["arguments"].extend(args)
                        yield {"type": "bear", "data": args[-1]}
                        
                elif node_name == "judge":
                    verdict = node_output.get("verdict", {})
                    results["verdict"] = verdict
                    args = node_output.get("arguments", [])
                    if args:
                        results["arguments"].extend(args)
                    yield {"type": "judge", "data": verdict}
    
    yield {"type": "complete", "data": results}


def display_research_summary(research_data: dict):
    """Display research data in a compact format."""
    if not research_data:
        return
    
    metrics = research_data.get("metrics", {})
    sentiment = research_data.get("sentiment", {})
    technical = research_data.get("technical_indicators", {})
    
    # KPI Row
    with st.container(border=True):
        st.subheader("Research Summary")
        
        cols = st.columns(4)
        with cols[0]:
            pe = metrics.get("PE_RATIO", "N/A")
            st.metric("P/E Ratio", f"{pe}")
        with cols[1]:
            roe = metrics.get("ROE_PCT", "N/A")
            st.metric("ROE", f"{roe}%")
        with cols[2]:
            overall = sentiment.get("OVERALL_SENTIMENT", "N/A")
            st.metric("Sentiment", overall)
        with cols[3]:
            rsi = technical.get("RSI_14", "N/A")
            st.metric("RSI (14)", f"{rsi}")


def display_argument(arg: dict, agent_type: str):
    """Display a single argument."""
    if agent_type == "bull":
        icon = "🐂"
        color = "green"
        title = "BULL"
    else:
        icon = "🐻"
        color = "red"
        title = "BEAR"
    
    content = arg.get("content", "")
    confidence = arg.get("confidence", 0.5)
    
    with st.chat_message(title.lower(), avatar=icon):
        st.markdown(f"**{title}** *(confidence: {confidence:.0%})*")
        st.write(content)


def display_verdict(verdict: dict):
    """Display the judge's verdict."""
    if not verdict:
        return
    
    rec = verdict.get("recommendation", "HOLD")
    confidence = verdict.get("confidence", 0.5)
    summary = verdict.get("summary", "")
    bull_score = verdict.get("bull_score", 50)
    bear_score = verdict.get("bear_score", 50)
    
    # Color based on recommendation
    rec_colors = {
        "STRONG BUY": "green",
        "BUY": "green",
        "HOLD": "orange",
        "SELL": "red",
        "STRONG SELL": "red",
    }
    color = rec_colors.get(rec, "blue")
    
    with st.container(border=True):
        st.subheader("Final Verdict")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"### :{color}[{rec}]")
            st.caption(f"Confidence: {confidence:.0%}")
        with col2:
            st.metric("Bull Score", f"{bull_score}/100")
        with col3:
            st.metric("Bear Score", f"{bear_score}/100")
        
        if summary:
            st.markdown("---")
            st.write(summary)


def display_query_logs(query_logs: dict):
    """Display query logs from Cortex Analyst and Search."""
    if not query_logs:
        return
    
    analyst_logs = query_logs.get("analyst", [])
    search_logs = query_logs.get("search", [])
    
    if not analyst_logs and not search_logs:
        st.info("No query logs captured for this debate.")
        return
    
    # Cortex Analyst queries
    if analyst_logs:
        st.markdown("#### Cortex Analyst Queries")
        for i, log in enumerate(analyst_logs):
            with st.expander(f"{log.get('type', 'query')} - {log.get('timestamp', '')[:19]}"):
                st.markdown("**SQL:**")
                st.code(log.get("sql", "N/A"), language="sql")
                
                results = log.get("results", [])
                if isinstance(results, list) and results:
                    st.markdown("**Results:**")
                    if len(results) == 1 and isinstance(results[0], dict):
                        # Single row - display as key-value pairs
                        for k, v in results[0].items():
                            st.write(f"**{k}:** {v}")
                    else:
                        # Multiple rows - display as table
                        st.dataframe(results, use_container_width=True)
                elif isinstance(results, dict):
                    if "error" in results:
                        st.error(f"Error: {results['error']}")
                    else:
                        st.json(results)
    
    # Cortex Search queries
    if search_logs:
        st.markdown("#### Cortex Search Queries")
        for i, log in enumerate(search_logs):
            with st.expander(f"{log.get('type', 'search')} - {log.get('timestamp', '')[:19]}"):
                st.markdown("**Service:**")
                st.code(log.get("service", "N/A"))
                
                st.markdown("**Request:**")
                st.json(log.get("request", {}))
                
                results = log.get("results", [])
                if isinstance(results, list) and results:
                    st.markdown(f"**Results ({len(results)} documents):**")
                    for j, doc in enumerate(results[:3]):  # Show first 3
                        with st.container(border=True):
                            # Show key fields
                            for key in ["TICKER", "FIRM", "RATING", "PRICE_TARGET", "REPORT_TITLE"]:
                                if key in doc:
                                    st.write(f"**{key}:** {doc[key]}")
                            # Show content preview
                            for content_key in ["REPORT_CONTENT", "TRANSCRIPT_CONTENT", "FILING_CONTENT"]:
                                if content_key in doc and doc[content_key]:
                                    content = str(doc[content_key])
                                    preview = content[:500] + "..." if len(content) > 500 else content
                                    st.markdown(f"**{content_key} (preview):**")
                                    st.text(preview)
                                    break
                    if len(results) > 3:
                        st.caption(f"... and {len(results) - 3} more results")
                elif isinstance(results, dict) and "error" in results:
                    st.error(f"Error: {results['error']}")


# Sidebar
with st.sidebar:
    st.title("🐂 vs 🐻")
    st.markdown("**Multi-Agent Debate System**")
    st.markdown("---")
    
    # Ticker input
    ticker = st.text_input(
        "Stock Ticker",
        value="NVDA",
        max_chars=10,
        help="Enter a stock ticker symbol (e.g., NVDA, AAPL, MSFT)",
    ).upper()
    
    # Debate settings
    rounds = st.slider(
        "Debate Rounds",
        min_value=1,
        max_value=5,
        value=2,
        help="Number of Bull-Bear exchange rounds",
    )
    
    # Custom question
    custom_question = st.text_area(
        "Custom Question (optional)",
        placeholder="Should we buy this stock?",
        help="Leave empty for default buy/sell analysis",
    )
    
    # Run button
    run_button = st.button(
        "Start Debate",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.is_running,
    )
    
    st.markdown("---")
    
    # Debug toggle
    st.session_state.show_debug = st.checkbox(
        "Show Debug View",
        value=st.session_state.show_debug,
        help="Display raw SQL queries and API calls from Cortex tools",
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app uses **Snowflake Cortex AI** to power a multi-agent debate system:
    
    - **Research Agent**: Gathers data from Cortex Analyst & Search
    - **Bull Agent**: Advocates for buying
    - **Bear Agent**: Advocates for selling  
    - **Judge**: Delivers final verdict
    
    The competitive reasoning pattern reduces factual hallucinations by grounding arguments in real data.
    """)

# Main content
st.title("Multi-Agent Debate System")
st.markdown("**AI-powered investment analysis through competitive reasoning**")

# Run debate
if run_button and ticker:
    st.session_state.is_running = True
    
    # Progress container
    progress_container = st.empty()
    
    with progress_container.container():
        st.info(f"Analyzing **{ticker}**...")
        
        # Create placeholders for each phase
        research_placeholder = st.empty()
        debate_container = st.container()
        verdict_placeholder = st.empty()
        
        try:
            question = custom_question if custom_question else None
            
            for event in run_debate(ticker, rounds, question):
                event_type = event["type"]
                data = event["data"]
                
                if event_type == "research":
                    with research_placeholder:
                        display_research_summary(data)
                
                elif event_type == "bull":
                    with debate_container:
                        display_argument(data, "bull")
                
                elif event_type == "bear":
                    with debate_container:
                        display_argument(data, "bear")
                
                elif event_type == "judge":
                    with verdict_placeholder:
                        display_verdict(data)
                
                elif event_type == "complete":
                    st.session_state.current_debate = data
                    st.session_state.debate_history.append(data)
            
            st.success("Debate complete!")
            
            # Show debug view if enabled
            if st.session_state.show_debug:
                with st.expander("Debug View: Raw Queries & Data", expanded=True):
                    display_query_logs(st.session_state.current_debate.get("query_logs", {}))
            
        except Exception as e:
            st.error(f"Error during debate: {str(e)}")
        
        finally:
            st.session_state.is_running = False

# Display current debate if exists
elif st.session_state.current_debate:
    debate = st.session_state.current_debate
    
    st.markdown(f"### Latest Analysis: **{debate['ticker']}**")
    st.caption(f"*{debate['question']}*")
    
    # Research summary
    if debate.get("research_data"):
        display_research_summary(debate["research_data"])
    
    # Arguments
    st.markdown("### Debate")
    for arg in debate.get("arguments", []):
        agent = arg.get("agent", "")
        if agent in ["bull", "bear"]:
            display_argument(arg, agent)
    
    # Verdict
    if debate.get("verdict"):
        display_verdict(debate["verdict"])
    
    # Debug view
    if st.session_state.show_debug and debate.get("query_logs"):
        with st.expander("Debug View: Raw Queries & Data", expanded=False):
            display_query_logs(debate.get("query_logs", {}))

else:
    # Welcome screen
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📊 Research")
            st.write("Gathers financial metrics, earnings data, analyst reports, and market sentiment from Snowflake.")
    
    with col2:
        with st.container(border=True):
            st.markdown("### 💬 Debate")
            st.write("Bull and Bear agents argue opposing positions, citing evidence from research data.")
    
    with col3:
        with st.container(border=True):
            st.markdown("### ⚖️ Verdict")
            st.write("Judge weighs arguments and delivers a recommendation with confidence score.")
    
    st.markdown("---")
    st.markdown("**Enter a ticker in the sidebar and click 'Start Debate' to begin.**")

# History tab (collapsible)
if st.session_state.debate_history:
    with st.expander(f"Debate History ({len(st.session_state.debate_history)} debates)"):
        for i, debate in enumerate(reversed(st.session_state.debate_history)):
            verdict = debate.get("verdict", {})
            rec = verdict.get("recommendation", "N/A")
            conf = verdict.get("confidence", 0)
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{debate['ticker']}**")
            with col2:
                st.write(f"{rec} ({conf:.0%})")
            with col3:
                if st.button("View", key=f"view_{i}"):
                    st.session_state.current_debate = debate
                    st.rerun()
