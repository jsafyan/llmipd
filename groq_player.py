import json
import os
import traceback
from typing import List, Tuple

import axelrod as axl
from groq import Groq, RateLimitError

from llm_player import LLMPlayer

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Please set the GROQ_API_KEY environment variable")

client = Groq(api_key=GROQ_API_KEY)

with open("prompts/system_prompt.txt", "r") as f:
    SYSTEM_INSTRUCTIONS = f.read()

PROMPT_TEMPLATE = """
Take a deep breath and think step-by-step about the match thus far, your strategy, and your reasoning for your move.

Current match history: {history}

Respond with your analysis and next move in the following JSON format:
{{
  "analysis": "Your step-by-step reasoning here",
  "move": "C or D"
}}
"""


class GroqPlayer(LLMPlayer):
    def __init__(self, model="llama-3.1-8b-instant", max_retries: int = 5):
        super().__init__(model=model, name="Groq Player", max_retries=max_retries)

    def get_move(self, history: List[Tuple[str, str]], opponent_name: str) -> str:
        error_message = ""
        additional_info = ""
        try:
            history_str = [
                (str(my_move), str(opp_move)) for my_move, opp_move in history
            ]
            prompt = PROMPT_TEMPLATE.format(history=history_str)

            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                temperature=0,
                max_tokens=1000,
                response_format={"type": "json_object"},
                seed=self.match_seed,
            )

            result = json.loads(response.choices[0].message.content)
            move_str = result["move"].upper()
            additional_info = response.choices[0].message.content

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

        except RateLimitError as e:
            error_message = f"Rate limit reached: {e}"
            raise
        except Exception as e:
            error_message = f"Error getting move: {str(e)}\n{traceback.format_exc()}"
            move = axl.Action.C
            self._log_api_call(
                opponent_name, history, move, error_message, additional_info
            )
            return move
