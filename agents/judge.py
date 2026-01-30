"""
Judge Agent - Makes final investment recommendation after debate.
"""
from typing import Dict, Any, List
from graph.state import DebateState, Argument, Verdict
from agents.base import BaseAgent


class Judge(BaseAgent):
    """
    Judge agent that evaluates the debate and makes final recommendation.
    Weighs both sides' arguments and delivers a verdict.
    """
    
    def __init__(self):
        super().__init__(
            name="Judge",
            persona="Impartial investment committee making final decision"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are the JUDGE - an impartial investment committee evaluating a bull vs bear debate.

Your role is to:

1. WEIGH BOTH SIDES:
   - Consider the strength of each argument
   - Evaluate evidence quality from both perspectives
   - Account for fact-checker feedback

2. MAKE A DECISION:
   - STRONG BUY: Bull case overwhelming, minimal risks
   - BUY: Bull case stronger, acceptable risk/reward
   - HOLD: Arguments balanced, no clear edge
   - SELL: Bear case stronger, risks outweigh potential
   - STRONG SELL: Bear case overwhelming, significant risks

3. SCORE THE DEBATE:
   - Bull Score (0-100): How compelling was the bull case?
   - Bear Score (0-100): How compelling was the bear case?

4. PROVIDE RATIONALE:
   - Explain what swayed your decision
   - Acknowledge the strongest points from the losing side
   - List key factors and risks

5. ASSIGN CONFIDENCE:
   - 0.0-0.3: Low confidence, could go either way
   - 0.4-0.6: Moderate confidence
   - 0.7-0.8: High confidence
   - 0.9-1.0: Very high confidence, clear decision

Be decisive but fair. Your recommendation will guide investment decisions."""
    
    def generate_argument(
        self,
        state: DebateState,
        opponent_argument: str = None,
    ) -> Argument:
        """Generate judgment (implements abstract method)."""
        verdict = self.generate_verdict(state)
        return Argument(
            agent="judge",
            content=verdict.summary,
            confidence=verdict.confidence,
        )
    
    def generate_verdict(self, state: DebateState) -> Verdict:
        """Generate final verdict after evaluating the debate."""
        ticker = state["ticker"]
        research_context = self.format_research_context(state.get("research_data", {}))
        debate_history = self.format_debate_history(state.get("arguments", []))
        
        # Get fact-check summaries
        fact_checks = state.get("fact_checks", [])
        fact_check_summary = ""
        for fc in fact_checks:
            fact_check_summary += f"\n{fc.get('agent_checked', 'unknown').upper()}: "
            fact_check_summary += f"Accuracy {fc.get('accuracy_score', 'N/A')}"
        
        prompt = f"""FINAL JUDGMENT REQUIRED

STOCK: {ticker}

RESEARCH DATA:
{research_context}

{debate_history}

FACT-CHECK RESULTS:
{fact_check_summary if fact_check_summary else "No fact-checks available"}

You must now render your verdict. Analyze all arguments and provide:

RECOMMENDATION: [STRONG BUY / BUY / HOLD / SELL / STRONG SELL]
CONFIDENCE: [0.0-1.0]
BULL_SCORE: [0-100]
BEAR_SCORE: [0-100]
SUMMARY: [2-3 sentence summary of your decision]
KEY_FACTORS: [List 3-5 factors that influenced your decision]
RISKS_TO_MONITOR: [List 2-3 key risks even if recommending buy]

Be decisive. Explain your reasoning clearly."""
        
        response = self.llm.complete(prompt, system_prompt=self.system_prompt)
        
        # Parse the response
        recommendation = "HOLD"
        confidence = 0.5
        bull_score = 50.0
        bear_score = 50.0
        summary = response
        key_factors = []
        risks = []
        
        lines = response.split("\n")
        for line in lines:
            line_upper = line.upper()
            if "RECOMMENDATION:" in line_upper:
                rec_text = line.split(":", 1)[1].strip().upper()
                for rec in ["STRONG BUY", "STRONG SELL", "BUY", "SELL", "HOLD"]:
                    if rec in rec_text:
                        recommendation = rec
                        break
            elif "CONFIDENCE:" in line_upper:
                try:
                    confidence = float(line.split(":")[1].strip().split()[0])
                except:
                    pass
            elif "BULL_SCORE:" in line_upper:
                try:
                    bull_score = float(line.split(":")[1].strip().split()[0])
                except:
                    pass
            elif "BEAR_SCORE:" in line_upper:
                try:
                    bear_score = float(line.split(":")[1].strip().split()[0])
                except:
                    pass
            elif "SUMMARY:" in line_upper:
                summary = line.split(":", 1)[1].strip() if ":" in line else summary
            elif "KEY_FACTORS:" in line_upper or "KEY FACTORS:" in line_upper:
                # Try to extract factors from following lines
                pass
            elif line.strip().startswith("-") and len(key_factors) < 5:
                key_factors.append(line.strip("- "))
        
        if not key_factors:
            key_factors = ["See detailed analysis in summary"]
        
        if not risks:
            risks = ["Market volatility", "Execution risk"]
        
        return Verdict(
            recommendation=recommendation,
            confidence=min(max(confidence, 0.0), 1.0),
            summary=summary,
            bull_score=min(max(bull_score, 0.0), 100.0),
            bear_score=min(max(bear_score, 0.0), 100.0),
            key_factors=key_factors[:5],
            risks=risks[:3],
        )
    
    def __call__(self, state: DebateState) -> Dict[str, Any]:
        """LangGraph node function."""
        verdict = self.generate_verdict(state)
        
        # Also create an argument for the transcript
        argument = Argument(
            agent="judge",
            content=f"""VERDICT: {verdict.recommendation}

{verdict.summary}

Bull Score: {verdict.bull_score}/100
Bear Score: {verdict.bear_score}/100
Confidence: {verdict.confidence:.0%}

Key Factors:
{chr(10).join('- ' + f for f in verdict.key_factors)}

Risks to Monitor:
{chr(10).join('- ' + r for r in verdict.risks)}""",
            confidence=verdict.confidence,
        )
        
        return {
            "arguments": [argument.to_dict()],
            "verdict": verdict.to_dict(),
            "current_speaker": "end",
        }
