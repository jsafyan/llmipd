import json
import os
import traceback
from typing import List, Tuple

import axelrod as axl
import anthropic
from anthropic.types import ContentBlock

from llm_player import LLMPlayer

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable")

client = anthropic.Anthropic()

# Load default system prompt
with open("prompts/system_prompt.txt", "r") as f:
    DEFAULT_SYSTEM_INSTRUCTIONS = f.read()

PROMPT_TEMPLATE = """Think step-by-step about the match thus far, your strategy, and your reasoning for your move. Current match history: {history}

Your response must be a valid JSON object with exactly two fields:
1. "analysis": A string containing your reasoning
2. "move": Either "C" or "D"

Example response:
{{"analysis": "Based on the empty history, I will cooperate on the first move to establish trust", "move": "C"}}

Ensure your response is a single line of valid JSON. Do not include any other text before or after the JSON."""


class AnthropicPlayer(LLMPlayer):
    def __init__(
        self,
        model="claude-3-haiku-20241022",
        max_retries: int = 5,
        system_instructions: str = None,
    ):
        super().__init__(
            model=model,
            name="Claude Player",
            max_retries=max_retries,
            system_instructions=system_instructions or DEFAULT_SYSTEM_INSTRUCTIONS,
        )

    def get_move(self, history: List[Tuple[str, str]], opponent_name: str) -> str:
        error_message = ""
        additional_info = ""
        try:
            history_str = [
                (str(my_move), str(opp_move)) for my_move, opp_move in history
            ]
            prompt = PROMPT_TEMPLATE.format(history=history_str)

            # Create system message properly structured for caching
            system_content = [
                {
                    "type": "text",
                    "text": self.system_instructions,
                    "cache_control": {"type": "ephemeral"},
                }
            ]

            response = client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0,
                system=system_content,
                messages=[{"role": "user", "content": prompt}],
            )

            result = json.loads(response.content[0].text)
            move_str = result["move"].upper()
            additional_info = response.content[0].text

            if move_str == "C":
                move = axl.Action.C
            elif move_str == "D":
                move = axl.Action.D
            else:
                error_message = f"Invalid move received from API: {move_str}"
                move = axl.Action.C

            self._log_api_call(
                opponent_name, history, move, error_message, additional_info
            )
            return move

        except anthropic.APIError as e:
            error_message = f"API error: {e}"
            raise
        except Exception as e:
            error_message = f"Error getting move: {str(e)}\n{traceback.format_exc()}"
            move = axl.Action.C
            self._log_api_call(
                opponent_name, history, move, error_message, additional_info
            )
            return move
