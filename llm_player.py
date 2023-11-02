"""An abstract class for an Axelrod Player that uses an LLM to play."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from axelrod import Player, Action


class LLMPlayer(Player, ABC):
    """
    An abstract base class for players in Axelrod's tournament that interact with Large Language Models (LLMs).

    Attributes:
        model_type (str): The type or name of the LLM.
        prompt_template (str): A template for the prompt to be sent to the LLM.
        config (Dict[str, Any]): Additional configuration parameters for the LLM.
    """

    def __init__(self, model_type: str, prompt_template: str, **config: Dict[str, Any]) -> None:
        """
        Initialize the LLM player.

        Args:
            model_type (str): The type or name of the LLM.
            prompt_template (str): A template for the prompt to be sent to the LLM.
            **config: Additional configuration parameters for the LLM.
        """
        super().__init__()
        self.model_type = model_type
        self.prompt_template = prompt_template
        self.config = config

    @abstractmethod
    def strategy(self, opponent: Player) -> Action:
        """
        Determine the next move in the game based on the history of moves.

        Args:
            opponent (Player): The opponent player.

        Returns:
            Action: The next move (Action.C for cooperate or Action.D for defect).
        """
        prompt = self.prepare_prompt(self.history, opponent.history)
        response = self.prompt_llm(prompt)
        move = self.parse_response(response)
        return move

    @abstractmethod
    def prepare_prompt(self, player_history: List[Action], opponent_history: List[Action]) -> str:
        """
        Prepare the prompt to be sent to the LLM based on the history of moves.

        Args:
            player_history (List[Action]): The history of moves of the player.
            opponent_history (List[Action]): The history of moves of the opponent.

        Returns:
            str: The prepared prompt.
        """

    @abstractmethod
    def prompt_llm(self, prompt: str) -> str:
        """
        Send the prompt to the LLM and receive the response.

        Args:
            prompt (str): The prompt to be sent to the LLM.

        Returns:
            str: The response from the LLM.
        """

    @abstractmethod
    def parse_response(self, response: str) -> Action:
        """
        Parse the response from the LLM to extract the next move.

        Args:
            response (str): The response from the LLM.

        Returns:
            Action: The next move (Action.C for cooperate or Action.D for defect).
        """
