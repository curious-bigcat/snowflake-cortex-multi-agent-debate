#!/usr/bin/env python3
"""
Multi-Agent Debate System CLI

A financial analysis tool that uses Bull and Bear agents to debate
investment decisions, grounded by Snowflake Cortex AI services.
"""
import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
import json

app = typer.Typer(
    name="debate",
    help="Multi-Agent Debate System for Financial Analysis",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    ticker: str = typer.Argument(..., help="Stock ticker to analyze (e.g., NVDA, AAPL)"),
    rounds: int = typer.Option(3, "--rounds", "-r", help="Number of debate rounds"),
    question: Optional[str] = typer.Option(None, "--question", "-q", help="Specific question to debate"),
    simple: bool = typer.Option(False, "--simple", "-s", help="Use simplified debate flow"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save results to JSON file"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
):
    """
    Run a multi-agent debate on a stock ticker.
    
    Example:
        python main.py NVDA --rounds 3
        python main.py AAPL -q "Is this a good long-term investment?"
    """
    from graph.workflow import run_debate, create_simple_debate_graph
    from graph.state import create_initial_state
    
    console.print(Panel(
        f"[bold cyan]Multi-Agent Debate System[/bold cyan]\n\n"
        f"🎯 Analyzing: [bold green]{ticker.upper()}[/bold green]\n"
        f"🔄 Rounds: {rounds}\n"
        f"📝 Question: {question or 'Should we buy or sell this stock?'}",
        title="🐂 Bull vs Bear 🐻",
        border_style="cyan"
    ))
    
    try:
        if simple:
            # Use simplified graph
            console.print("\n[yellow]Using simplified debate flow...[/yellow]\n")
            graph = create_simple_debate_graph()
            initial_state = create_initial_state(
                ticker=ticker,
                question=question,
                max_rounds=rounds,
            )
            
            final_state = None
            for event in graph.stream(initial_state):
                for node_name, node_output in event.items():
                    if not quiet:
                        display_node_output(node_name, node_output)
                    if node_output:
                        if final_state is None:
                            final_state = dict(initial_state)
                        for key, value in node_output.items():
                            if key == "arguments":
                                final_state["arguments"] = final_state.get("arguments", []) + value
                            else:
                                final_state[key] = value
        else:
            # Use full debate with moderation
            final_state = run_debate(
                ticker=ticker,
                question=question,
                max_rounds=rounds,
                verbose=not quiet,
            )
        
        # Display final summary
        if final_state:
            display_final_summary(final_state)
            
            # Save to file if requested
            if output:
                save_results(final_state, output)
                console.print(f"\n[green]Results saved to {output}[/green]")
        
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def research(
    ticker: str = typer.Argument(..., help="Stock ticker to research"),
):
    """
    Run only the research phase to see available data.
    
    Example:
        python main.py research NVDA
    """
    from agents.researcher import Researcher
    from graph.state import create_initial_state
    
    console.print(f"\n[cyan]Researching {ticker.upper()}...[/cyan]\n")
    
    researcher = Researcher()
    state = create_initial_state(ticker=ticker)
    result = researcher(state)
    
    research_data = result.get("research_data", {})
    
    # Display research results
    table = Table(title=f"Research Data for {ticker.upper()}")
    table.add_column("Category", style="cyan")
    table.add_column("Data Points", style="green")
    
    for key, value in research_data.items():
        if value:
            if isinstance(value, list):
                table.add_row(key, f"{len(value)} items")
            elif isinstance(value, dict):
                table.add_row(key, f"{len(value)} fields")
            else:
                table.add_row(key, str(value)[:100])
    
    console.print(table)
    
    # Show sample data
    if research_data.get("analyst_reports"):
        console.print("\n[yellow]Sample Analyst Report:[/yellow]")
        console.print(research_data["analyst_reports"][0][:500] + "...")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    service: str = typer.Option("all", "--service", "-s", 
                                help="Search service (analyst, earnings, sec, annual, all)"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of results"),
):
    """
    Search Cortex Search services directly.
    
    Example:
        python main.py search "NVIDIA growth outlook" --service analyst
    """
    from tools.cortex_search import CortexSearch
    
    search_tool = CortexSearch()
    
    console.print(f"\n[cyan]Searching: {query}[/cyan]\n")
    
    service_map = {
        "analyst": search_tool.search_analyst_reports,
        "earnings": search_tool.search_earnings_transcripts,
        "sec": search_tool.search_sec_filings,
        "annual": search_tool.search_annual_reports,
        "all": search_tool.search_all,
    }
    
    search_func = service_map.get(service, search_tool.search_all)
    results = search_func(query, limit=limit)
    
    if results:
        for i, result in enumerate(results, 1):
            console.print(Panel(
                result[:500] + "..." if len(result) > 500 else result,
                title=f"Result {i}",
                border_style="green"
            ))
    else:
        console.print("[yellow]No results found.[/yellow]")


@app.command()
def ask(
    question: str = typer.Argument(..., help="Natural language question about the data"),
):
    """
    Ask Cortex Analyst a question (text-to-SQL).
    
    Example:
        python main.py ask "What is NVDA's current P/E ratio?"
    """
    from tools.cortex_analyst import CortexAnalyst
    
    analyst = CortexAnalyst()
    
    console.print(f"\n[cyan]Question: {question}[/cyan]\n")
    
    result = analyst.ask(question)
    
    if result:
        console.print(Panel(
            str(result),
            title="Cortex Analyst Response",
            border_style="green"
        ))
    else:
        console.print("[yellow]No answer available.[/yellow]")


@app.command()
def test_connection():
    """
    Test the Snowflake connection and Cortex services.
    """
    from config import get_snowflake_connection, SNOWFLAKE_CONFIG, CORTEX_CONFIG
    
    console.print("\n[cyan]Testing Snowflake Connection...[/cyan]\n")
    
    try:
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
        user, role, warehouse = cursor.fetchone()
        
        table = Table(title="Connection Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("User", user)
        table.add_row("Role", role)
        table.add_row("Warehouse", warehouse)
        table.add_row("Database", SNOWFLAKE_CONFIG.database)
        table.add_row("Schema", SNOWFLAKE_CONFIG.schema)
        
        console.print(table)
        
        # Test Cortex Search
        console.print("\n[cyan]Testing Cortex Search Services...[/cyan]")
        search_columns = {
            "ANALYST_REPORTS_SEARCH": "REPORT_CONTENT",
            "ANNUAL_REPORTS_SEARCH": "REPORT_CONTENT",
            "EARNINGS_TRANSCRIPTS_SEARCH": "TRANSCRIPT_CONTENT",
            "SEC_FILINGS_SEARCH": "FILING_CONTENT",
        }
        for service in CORTEX_CONFIG.search_services.values():
            service_name = service.split('.')[-1]
            col = search_columns.get(service_name, "REPORT_CONTENT")
            cursor.execute(f"""
                SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    '{service}',
                    '{{"query": "test", "columns": ["{col}"], "limit": 1}}'
                )
            """)
            console.print(f"  ✅ {service_name}")
        
        # Test Cortex Complete
        console.print("\n[cyan]Testing Cortex Complete...[/cyan]")
        cursor.execute(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{CORTEX_CONFIG.model}',
                'Say hello in one word'
            )
        """)
        console.print(f"  ✅ {CORTEX_CONFIG.model} model available")
        
        cursor.close()
        conn.close()
        
        console.print("\n[bold green]All systems operational! ✅[/bold green]")
        
    except Exception as e:
        console.print(f"\n[red]Connection Error: {e}[/red]")
        raise typer.Exit(1)


def display_node_output(node_name: str, output: dict):
    """Display formatted output for a node."""
    icons = {
        "research": "📊",
        "bull_1": "🐂",
        "bull_2": "🐂",
        "bull": "🐂",
        "bear_1": "🐻",
        "bear_2": "🐻",
        "bear": "🐻",
        "moderator": "⚖️",
        "judge": "👨‍⚖️",
    }
    
    colors = {
        "research": "yellow",
        "bull_1": "green",
        "bull_2": "green",
        "bull": "green",
        "bear_1": "red",
        "bear_2": "red",
        "bear": "red",
        "moderator": "blue",
        "judge": "magenta",
    }
    
    icon = icons.get(node_name, "▶")
    color = colors.get(node_name, "white")
    
    console.print(f"\n[{color}]{icon} {node_name.upper()}[/{color}]")
    
    if node_name == "judge" and output.get("verdict"):
        verdict = output["verdict"]
        rec = verdict.get("recommendation", "HOLD")
        conf = verdict.get("confidence", 0.5)
        console.print(Panel(
            f"[bold]{rec}[/bold] (Confidence: {conf:.0%})\n\n"
            f"{verdict.get('summary', '')}",
            title="Final Verdict",
            border_style="magenta"
        ))
    elif output.get("arguments"):
        args = output["arguments"]
        if args:
            content = args[-1].get("content", "")
            console.print(Panel(
                content[:600] + "..." if len(content) > 600 else content,
                border_style=color
            ))


def display_final_summary(state: dict):
    """Display the final debate summary."""
    console.print("\n" + "="*60)
    console.print("[bold cyan]DEBATE SUMMARY[/bold cyan]")
    console.print("="*60 + "\n")
    
    ticker = state.get("ticker", "N/A")
    arguments = state.get("arguments", [])
    verdict = state.get("verdict", {})
    
    # Argument summary
    bull_args = [a for a in arguments if a.get("agent") == "bull"]
    bear_args = [a for a in arguments if a.get("agent") == "bear"]
    
    table = Table(title=f"Debate Statistics for {ticker}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Total Arguments", str(len(arguments)))
    table.add_row("Bull Arguments", str(len(bull_args)))
    table.add_row("Bear Arguments", str(len(bear_args)))
    
    if verdict:
        table.add_row("Recommendation", verdict.get("recommendation", "N/A"))
        table.add_row("Confidence", f"{verdict.get('confidence', 0):.0%}")
        table.add_row("Bull Score", f"{verdict.get('bull_score', 0)}/100")
        table.add_row("Bear Score", f"{verdict.get('bear_score', 0)}/100")
    
    console.print(table)
    
    # Key factors
    if verdict.get("key_factors"):
        console.print("\n[yellow]Key Factors:[/yellow]")
        for factor in verdict["key_factors"]:
            console.print(f"  • {factor}")


def save_results(state: dict, filename: str):
    """Save debate results to JSON file."""
    # Convert to serializable format
    output = {
        "ticker": state.get("ticker"),
        "question": state.get("question"),
        "verdict": state.get("verdict"),
        "arguments": [
            {
                "agent": arg.get("agent"),
                "content": arg.get("content"),
                "round": arg.get("round"),
            }
            for arg in state.get("arguments", [])
        ],
        "research_summary": {
            k: str(v)[:500] if v else None
            for k, v in state.get("research_data", {}).items()
        }
    }
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    app()
