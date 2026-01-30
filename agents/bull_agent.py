"""
Bull Agent - Optimistic perspective advocating for buying.
"""
from typing import Dict, Any, List
from graph.state import DebateState, Argument
from agents.base import BaseAgent


class BullAgent(BaseAgent):
    """
    Bull agent with optimistic perspective.
    Focuses on growth potential, positive catalysts, and upside opportunities.
    """
    
    def __init__(self):
        super().__init__(
            name="Bull",
            persona="Optimistic investment analyst focused on growth opportunities"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are a BULL analyst - an optimistic investment professional who sees opportunity and growth potential.

Your role in this debate is to advocate for BUYING the stock. You must:

1. FOCUS ON POSITIVES:
   - Growth catalysts and expansion opportunities
   - Strong fundamentals and improving metrics
   - Competitive advantages and moat
   - Positive industry trends
   - Management quality and execution

2. INTERPRET DATA OPTIMISTICALLY:
   - High P/E? -> Investors willing to pay premium for growth
   - Recent dip? -> Buying opportunity
   - Mixed earnings? -> Focus on beats and guidance raises

3. COUNTER BEAR ARGUMENTS:
   - Acknowledge risks but explain why they're manageable
   - Provide alternative interpretations of negative data
   - Highlight overlooked positive factors

4. CITE EVIDENCE:
   - Reference specific data points, analyst reports, earnings transcripts
   - Use numbers to support your thesis
   - Quote management guidance when favorable

5. BE PERSUASIVE BUT FACTUAL:
   - Make compelling arguments backed by data
   - Don't invent facts - use the provided research
   - Maintain professional tone

Your goal is to make the strongest possible case for BUYING this stock.
Rate your confidence (0-1) based on the strength of evidence supporting your thesis."""
    
    def generate_argument(
        self,
        state: DebateState,
        opponent_argument: str = None,
    ) -> Argument:
        """Generate a bullish argument."""
        research_context = self.format_research_context(state.get("research_data", {}))
        debate_history = self.format_debate_history(state.get("arguments", []))
        
        ticker = state["ticker"]
        round_num = state.get("current_round", 1)
        
        if opponent_argument:
            prompt = f"""DEBATE ROUND {round_num}: Respond to the Bear's argument

STOCK: {ticker}

BEAR'S ARGUMENT TO COUNTER:
{opponent_argument}

RESEARCH DATA:
{research_context}

{debate_history}

Generate your BULL response. Counter the bear's points while making new bullish arguments.
Be specific, cite data, and explain why this stock is a BUY.

Format your response as:
ARGUMENT: [Your main argument]
EVIDENCE: [List 2-3 specific data points supporting your thesis]
CONFIDENCE: [0.0-1.0 based on evidence strength]
REBUTTAL: [Direct counter to bear's main points]"""
        else:
            prompt = f"""DEBATE ROUND {round_num}: Opening Bull Argument

STOCK: {ticker}

RESEARCH DATA:
{research_context}

Generate your opening BULL argument for why investors should BUY {ticker}.
Be specific, cite data, and make a compelling case.

Format your response as:
ARGUMENT: [Your main argument]
EVIDENCE: [List 2-3 specific data points supporting your thesis]
CONFIDENCE: [0.0-1.0 based on evidence strength]
KEY_CATALYSTS: [Upcoming events that could drive the stock higher]"""
        
        response = self.llm.complete(prompt, system_prompt=self.system_prompt)
        
        # Parse the response
        argument_content = response
        confidence = 0.7  # Default
        evidence = []
        
        # Try to extract structured parts
        lines = response.split("\n")
        for line in lines:
            if line.startswith("CONFIDENCE:"):
                try:
                    conf_str = line.replace("CONFIDENCE:", "").strip()
                    confidence = float(conf_str.split()[0])
                except:
                    pass
            elif line.startswith("EVIDENCE:"):
                evidence.append(line.replace("EVIDENCE:", "").strip())
        
        return Argument(
            agent="bull",
            content=argument_content,
            evidence=evidence,
            confidence=min(max(confidence, 0.0), 1.0),
        )
    
    def __call__(self, state: DebateState) -> Dict[str, Any]:
        """LangGraph node function."""
        # Get the last bear argument if exists
        bear_argument = None
        for arg in reversed(state.get("arguments", [])):
            if arg.get("agent") == "bear":
                bear_argument = arg.get("content")
                break
        
        argument = self.generate_argument(state, bear_argument)
        
        return {
            "arguments": [argument.to_dict()],
            "current_speaker": "moderator",
        }
