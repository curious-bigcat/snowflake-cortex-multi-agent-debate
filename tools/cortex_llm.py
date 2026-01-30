"""
Cortex LLM wrapper using SNOWFLAKE.CORTEX.COMPLETE function.
"""
import json
from typing import Optional, List, Dict, Any
import snowflake.connector
from config import CORTEX_CONFIG, get_snowflake_connection


class CortexLLM:
    """
    Wrapper for Snowflake CORTEX.COMPLETE function.
    Provides LLM capabilities for agent reasoning.
    """
    
    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        self.model = model or CORTEX_CONFIG.model
        self.temperature = temperature or CORTEX_CONFIG.temperature
        self.max_tokens = max_tokens or CORTEX_CONFIG.max_tokens
        self._connection = None
    
    def _get_connection(self):
        """Get or create Snowflake connection."""
        if self._connection is None or self._connection.is_closed():
            self._connection = get_snowflake_connection()
        return self._connection
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Generate completion using CORTEX.COMPLETE.
        
        Args:
            prompt: The user prompt/question
            system_prompt: Optional system prompt for context
            conversation_history: Optional list of previous messages
            
        Returns:
            Generated text response
        """
        # Build messages array
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": prompt})
        
        # Build the SQL query using dollar quoting to avoid escaping issues
        messages_json = json.dumps(messages)
        options_json = json.dumps({
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        })
        
        sql = f"""SELECT SNOWFLAKE.CORTEX.COMPLETE('{self.model}', PARSE_JSON($${messages_json}$$), PARSE_JSON($${options_json}$$)) as response"""
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                response_data = json.loads(result[0])
                # Extract the generated text from the response
                if isinstance(response_data, dict):
                    return response_data.get("choices", [{}])[0].get("messages", response_data.get("message", str(response_data)))
                return str(response_data)
            return ""
        finally:
            cursor.close()
    
    def complete_simple(self, prompt: str) -> str:
        """
        Simple completion without conversation history.
        Uses the simpler single-prompt syntax.
        """
        escaped_prompt = prompt.replace("'", "''")
        
        sql = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{self.model}',
            '{escaped_prompt}'
        ) as response
        """
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result[0] if result else ""
        finally:
            cursor.close()
    
    def close(self):
        """Close the connection."""
        if self._connection and not self._connection.is_closed():
            self._connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def test_cortex_llm():
    """Test the CortexLLM wrapper."""
    with CortexLLM() as llm:
        response = llm.complete_simple("What is 2 + 2? Answer in one word.")
        print(f"Response: {response}")


if __name__ == "__main__":
    test_cortex_llm()
