"""
Moderator Agent - Fact-checks arguments and ensures balanced debate.
"""
from typing import Dict, Any, List
from graph.state import DebateState, Argument
from agents.base import BaseAgent


class Moderator(BaseAgent):
    """
    Moderator agent that fact-checks arguments and ensures debate quality.
    Neutral perspective focused on accuracy and fairness.
    """
    
    def __init__(self):
        super().__init__(
            name="Moderator",
            persona="Neutral fact-checker ensuring debate accuracy"
        )
    
    @property
    def system_prompt(self) -> str:
        return """You are a neutral MODERATOR and fact-checker for an investment debate.

Your role is to:

1. VERIFY CLAIMS:
   - Check if cited data matches the research provided
   - Flag any exaggerated or misleading statements
   - Note when opinions are presented as facts

2. ENSURE BALANCE:
   - Highlight if either side ignored key data
   - Point out one-sided interpretations
   - Suggest overlooked perspectives

3. ASSESS ARGUMENT QUALITY:
   - Rate the logical coherence of each argument
   - Evaluate evidence quality and relevance
   - Note rhetorical techniques vs substantive points

4. PROVIDE BRIEF FEEDBACK:
   - Keep your analysis concise (2-3 key points)
   - Be objective and professional
   - Don't take sides - just assess accuracy

Your goal is to ensure the debate is grounded in facts and both sides are held accountable."""
    
    def fact_check(
        self,
        state: DebateState,
        argument_to_check: dict,
    ) -> Dict[str, Any]:
        """Fact-check a single argument."""
        research_context = self.format_research_context(state.get("research_data", {}))
        
        agent = argument_to_check.get("agent", "unknown")
        content = argument_to_check.get("content", "")
        
        prompt = f"""FACT-CHECK REQUEST

{agent.upper()}'S ARGUMENT:
{content}

AVAILABLE RESEARCH DATA:
{research_context}

Analyze this argument for accuracy. Provide:
1. ACCURACY_SCORE: [0.0-1.0] How well does this argument align with the data?
2. VERIFIED_CLAIMS: [List claims that are supported by data]
3. QUESTIONABLE_CLAIMS: [List claims that are exaggerated, misleading, or unsupported]
4. MISSING_CONTEXT: [Important data the argument ignored]
5. BRIEF_ASSESSMENT: [1-2 sentence summary]"""
        
        response = self.llm.complete(prompt, system_prompt=self.system_prompt)
        
        # Parse accuracy score
        accuracy = 0.7
        for line in response.split("\n"):
            if "ACCURACY_SCORE:" in line:
                try:
                    accuracy = float(line.split(":")[1].strip().split()[0])
                except:
                    pass
        
        return {
            "agent_checked": agent,
            "accuracy_score": accuracy,
            "feedback": response,
        }
    
    def generate_argument(
        self,
        state: DebateState,
        opponent_argument: str = None,
    ) -> Argument:
        """Generate moderator feedback (implements abstract method)."""
        # Get the last two arguments (bull and bear)
        recent_args = state.get("arguments", [])[-2:] if state.get("arguments") else []
        
        research_context = self.format_research_context(state.get("research_data", {}))
        
        args_text = ""
        for arg in recent_args:
            args_text += f"\n[{arg.get('agent', 'unknown').upper()}]:\n{arg.get('content', '')[:500]}...\n"
        
        prompt = f"""MODERATOR ROUND SUMMARY

RECENT ARGUMENTS:
{args_text}

RESEARCH DATA:
{research_context}

Provide a brief, neutral summary:
1. BULL_ACCURACY: [0.0-1.0] and brief note
2. BEAR_ACCURACY: [0.0-1.0] and brief note
3. KEY_CONTENTION: What's the main point of disagreement?
4. OVERLOOKED_DATA: Any important data neither side addressed?
5. ROUND_QUALITY: [0.0-1.0] Overall quality of arguments"""
        
        response = self.llm.complete(prompt, system_prompt=self.system_prompt)
        
        return Argument(
            agent="moderator",
            content=response,
            confidence=0.9,  # Moderator is confident in observations
        )
    
    def __call__(self, state: DebateState) -> Dict[str, Any]:
        """LangGraph node function."""
        argument = self.generate_argument(state)
        
        # Fact check the last two arguments
        fact_checks = []
        for arg in state.get("arguments", [])[-2:]:
            if arg.get("agent") in ["bull", "bear"]:
                check = self.fact_check(state, arg)
                fact_checks.append(check)
        
        # Determine next speaker
        current_round = state.get("current_round", 1)
        max_rounds = state.get("max_rounds", 3)
        
        if current_round >= max_rounds:
            next_speaker = "judge"
        else:
            next_speaker = "bull"  # Bull starts next round
        
        return {
            "arguments": [argument.to_dict()],
            "fact_checks": fact_checks,
            "current_speaker": next_speaker,
        }
