"""
Bear Agent - Pessimistic perspective advocating for selling or avoiding.
"""
from typing import Dict, Any, List
from graph.state import DebateState, Argument
from agents.base import BaseAgent


class BearAgent(BaseAgent):
    """
    Bear agent with pessimistic/cautious perspective.
    Focuses on risks, overvaluation concerns, and downside scenarios.
    """
    
    def __init__(self):
        super().__init__(
            name="Bear",
            persona="Cautious investment analyst focused on risk management"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are a BEAR analyst - a cautious investment professional who identifies risks and challenges.

Your role in this debate is to advocate for SELLING or AVOIDING the stock. You must:

1. FOCUS ON RISKS:
   - Valuation concerns and overpricing
   - Competitive threats and market share risks
   - Execution challenges and operational issues
   - Macro headwinds and sector risks
   - Management concerns or governance issues

2. INTERPRET DATA CAUTIOUSLY:
   - High P/E? -> Overvalued, limited upside
   - Recent run-up? -> Due for correction
   - Beat earnings? -> Already priced in, unsustainable

3. COUNTER BULL ARGUMENTS:
   - Challenge optimistic assumptions
   - Highlight ignored or downplayed risks
   - Question sustainability of growth

4. CITE EVIDENCE:
   - Reference specific data points, analyst reports, insider selling
   - Use numbers to support your thesis
   - Quote cautious analyst opinions

5. BE PERSUASIVE BUT FACTUAL:
   - Make compelling arguments backed by data
   - Don't invent facts - use the provided research
   - Maintain professional tone

Your goal is to make the strongest possible case for SELLING or AVOIDING this stock.
Rate your confidence (0-1) based on the strength of evidence supporting your thesis."""
    
    def generate_argument(
        self,
        state: DebateState,
        opponent_argument: str = None,
    ) -> Argument:
        """Generate a bearish argument."""
        research_context = self.format_research_context(state.get("research_data", {}))
        debate_history = self.format_debate_history(state.get("arguments", []))
        
        ticker = state["ticker"]
        round_num = state.get("current_round", 1)
        
        if opponent_argument:
            prompt = f"""DEBATE ROUND {round_num}: Respond to the Bull's argument

STOCK: {ticker}

BULL'S ARGUMENT TO COUNTER:
{opponent_argument}

RESEARCH DATA:
{research_context}

{debate_history}

Generate your BEAR response. Counter the bull's points while making new bearish arguments.
Be specific, cite data, and explain why investors should SELL or AVOID this stock.

Format your response as:
ARGUMENT: [Your main argument]
EVIDENCE: [List 2-3 specific data points supporting your thesis]
CONFIDENCE: [0.0-1.0 based on evidence strength]
REBUTTAL: [Direct counter to bull's main points]"""
        else:
            prompt = f"""DEBATE ROUND {round_num}: Opening Bear Argument

STOCK: {ticker}

RESEARCH DATA:
{research_context}

Generate your opening BEAR argument for why investors should SELL or AVOID {ticker}.
Be specific, cite data, and make a compelling case for caution.

Format your response as:
ARGUMENT: [Your main argument]
EVIDENCE: [List 2-3 specific data points supporting your thesis]
CONFIDENCE: [0.0-1.0 based on evidence strength]
KEY_RISKS: [Major risks that could drive the stock lower]"""
        
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
            agent="bear",
            content=argument_content,
            evidence=evidence,
            confidence=min(max(confidence, 0.0), 1.0),
        )
    
    def __call__(self, state: DebateState) -> Dict[str, Any]:
        """LangGraph node function."""
        # Get the last bull argument
        bull_argument = None
        for arg in reversed(state.get("arguments", [])):
            if arg.get("agent") == "bull":
                bull_argument = arg.get("content")
                break
        
        argument = self.generate_argument(state, bull_argument)
        
        # Determine next speaker based on round
        current_round = state.get("current_round", 1)
        max_rounds = state.get("max_rounds", 3)
        
        if current_round >= max_rounds:
            next_speaker = "judge"
        else:
            next_speaker = "moderator"
        
        return {
            "arguments": [argument.to_dict()],
            "current_speaker": next_speaker,
            "current_round": current_round + 1,
        }
