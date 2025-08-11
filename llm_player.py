import logging
import pathlib
from typing import Any

import axelrod as axl
import litellm
from pydantic import BaseModel, Field


# Define the default Pydantic model for the response
class DefaultResponse(BaseModel):
    move: str = Field(
        ...,
        description="The player's move, either 'C' for Cooperate or 'D' for Defect.",
    )
    rationale: str = Field("", description="The rationale behind the player's move.")


class LLMPlayer(axl.Player):
    """
    A player that uses a Large Language Model (LLM) to make decisions,
    leveraging the `litellm` library to support various model providers.
    It uses Pydantic models to enforce structured responses from the LLM.
    """

    name = "LLM Player"
    classifier = {
        "memory_depth": float("inf"),
        "stochastic": True,
        "makes_use_of": {"length"},
        "long_run_time": True,
        "inspects_source": False,
        "manipulates_source": False,
        "manipulates_state": False,
    }

    def __init__(
        self,
        model: str = "gemini/gemini-2.5-flash-lite",
        prompt_template: str | None = None,
        response_model: type[BaseModel] = DefaultResponse,
        move_field: str = "move",
        logger: logging.Logger | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ):
        """
        Initializes the LLMPlayer.

        Args:
            model: The name of the LLM model to use via `litellm`.
            prompt_template: A template for the prompt. If None, the default
                             prompt is loaded from a file.
            response_model: A Pydantic model to structure the LLM's response.
            move_field: The name of the field in the Pydantic model that
                        contains the move ('C' or 'D').
            logger: An optional logger instance to log LLM responses.
            api_key: An optional API key for the LLM provider. If not
                     provided, `litellm` will attempt to find it from
                     environment variables.
            **kwargs: Additional keyword arguments to pass to `litellm.completion`.
        """
        super().__init__()

        name = kwargs.pop("name", None)
        if name:
            self.name = name
        else:
            # Create a default name if one isn't provided.
            self.name = f"LLM Player ({model})"

        self.model = model
        self.api_key = api_key
        self.logger = logger or logging.getLogger(__name__).addHandler(
            logging.NullHandler()
        )

        if prompt_template is None:
            # Load the default prompt from the file
            prompt_path = (
                pathlib.Path(__file__).parent / "prompts" / "llm_player_prompt.md"
            )
            self.prompt_template = prompt_path.read_text()
        else:
            self.prompt_template = prompt_template

        self.response_model = response_model
        self.move_field = move_field
        self.litellm_kwargs = kwargs

        if self.move_field not in self.response_model.model_fields:
            raise ValueError(
                f"`{self.move_field}` is not a valid field in "
                f"`{self.response_model.__name__}`."
            )

    def _generate_prompt(self, opponent: axl.Player) -> str:
        """Formats the prompt with the current game history."""
        history_str = "".join(str(move) for move in self.history)
        opponent_history_str = "".join(str(move) for move in opponent.history)
        return self.prompt_template.format(
            history=history_str or "None",
            opponent_history=opponent_history_str or "None",
        )

    def strategy(self, opponent: axl.Player) -> axl.Action:
        """
        Queries the LLM for the next move based on the game history.
        """
        prompt = self._generate_prompt(opponent)
        try:
            # Use litellm's structured output feature with the Pydantic model
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_model=self.response_model,
                api_key=self.api_key,
                **self.litellm_kwargs,
            )

            if self.logger:
                self.logger.info(f"LLM response for player {self.name}: {response}")

            # Extract the move from the Pydantic object
            move_str = getattr(response, self.move_field)

            if str(move_str).lower() == "c":
                return axl.Action.C
            if str(move_str).lower() == "d":
                return axl.Action.D

            # Fallback if the response is not 'C' or 'D'
            return self._fallback_strategy()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calling LLM for player {self.name}: {e}")
            # Fallback in case of API errors or other exceptions
            return self._fallback_strategy()

    def _fallback_strategy(self) -> axl.Action:
        """A default strategy in case of LLM failure."""
        # A simple fallback: cooperate on the first move, then defect.
        return axl.Action.C if not self.history else axl.Action.D
