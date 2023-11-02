"""An Axelrod Player that uses OpenAI's GPT models to play."""
from typing import List, Dict, Any
import openai
from axelrod import Action

from llm_player import LLMPlayer


class GPTPlayer(LLMPlayer):
    """
    An class for a GPT-based player using OpenAI's API.

    Attributes:
        model_type (str): The type or name of the model.
        prompt_template (str): A template for the prompt to be sent to the LLM.
        api_key (str): The user's OpenAI API key.
        config (Dict[str, Any]): Additional configuration parameters for the LLM.
    """

    def __init__(self, model_type: str, prompt_template: str, api_key: str, **config: Dict[str, Any]) -> None:
        """
        Initialize the GPT-based LLM player.

        Args:
            model_type (str): The type or name of the GPT model (e.g., "text-davinci-003" or "gpt-3.5-turbo").
            prompt_template (str): A template for the prompt to be sent to the LLM.
            api_key (str): OpenAI API key for authentication.
            **config: Additional configuration parameters for the LLM.
        """
        super().__init__(model_type, prompt_template, **config)
        self.api_key = api_key
        openai.api_key = self.api_key

    def prepare_prompt(self, player_history: List[Action], opponent_history: List[Action]) -> str:
        """
        Prepare the prompt to be sent to the LLM based on the history of moves.

        Args:
            player_history (List[Action]): The history of moves of the player.
            opponent_history (List[Action]): The history of moves of the opponent.

        Returns:
            str: The prepared prompt.
        """
        prompt = self.prompt_template.format(
            player_history=player_history, opponent_history=opponent_history)
        return prompt

    def prompt_llm(self, prompt: str) -> str:
        """
        Send the prompt to the OpenAI API and receive the response.

        Args:
            prompt (str): The prompt to be sent to the LLM.

        Returns:
            str: The response from the LLM.
        """
        response = openai.Completion.create(
            model=self.model_type,
            prompt=prompt,
            **self.config
        )
        return response.choices[0].text.strip()

    def parse_response(self, response: str) -> Action:
        """
        Parse the response from the LLM to extract the next move.

        Args:
            response (str): The response from the LLM.

        Returns:
            Action: The next move (Action.C for cooperate or Action.D for defect).
        """
        if response.endswith("C"):
            return Action.C
        elif response.endswith("D"):
            return Action.D
        else:
            # Default to cooperation if parsing fails. TODO: add better parsing logic.
            return Action.C
