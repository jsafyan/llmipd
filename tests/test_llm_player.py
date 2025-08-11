import io
import logging
import pathlib
import unittest
from unittest.mock import PropertyMock, patch

import axelrod as axl
from pydantic import BaseModel, Field

from llm_player import DefaultResponse, LLMPlayer


class TestLLMPlayer(unittest.TestCase):
    def test_initialization(self):
        """Test that the player initializes correctly with default values."""
        player = LLMPlayer()
        self.assertIsInstance(player, axl.Player)
        self.assertEqual(player.model, "gemini/gemini-2.5-flash-lite")
        self.assertEqual(player.response_model, DefaultResponse)
        self.assertEqual(player.name, "LLM Player (gemini/gemini-2.5-flash-lite)")
        # Check that the default prompt is loaded
        self.assertIn("Iterated Prisoner's Dilemma", player.prompt_template)

    def test_initialization_with_custom_args(self):
        """Test initialization with a custom model and other arguments."""
        player = LLMPlayer(model="gpt-4-turbo", name="CustomGPTPlayer")
        self.assertEqual(player.model, "gpt-4-turbo")
        self.assertEqual(player.name, "CustomGPTPlayer")

    def test_invalid_move_field_raises_error(self):
        """Test that a ValueError is raised if the move_field is not in the model."""
        with self.assertRaises(ValueError):
            LLMPlayer(move_field="non_existent_field")

    @patch("llm_player.litellm.completion")
    def test_strategy_cooperates(self, mock_completion):
        """Test that the player returns Cooperate when the LLM suggests it."""
        mock_response = DefaultResponse(
            move="C", rationale="Cooperation is the best strategy here."
        )
        mock_completion.return_value = mock_response

        player = LLMPlayer()
        opponent = axl.Cooperator()
        self.assertEqual(player.strategy(opponent), axl.Action.C)
        mock_completion.assert_called_once()

    @patch("llm_player.litellm.completion")
    def test_strategy_defects(self, mock_completion):
        """Test that the player returns Defect when the LLM suggests it."""
        mock_response = DefaultResponse(
            move="D", rationale="Defection is the best strategy here."
        )
        mock_completion.return_value = mock_response

        player = LLMPlayer()
        opponent = axl.Cooperator()
        self.assertEqual(player.strategy(opponent), axl.Action.D)

    @patch("llm_player.litellm.completion")
    def test_strategy_with_custom_pydantic_model(self, mock_completion):
        """Test the player's strategy with a custom Pydantic response model."""

        class CustomMove(BaseModel):
            action: str = Field(...)
            comment: str = Field(...)

        mock_response = CustomMove(
            action="D", comment="Using a custom model to defect."
        )
        mock_completion.return_value = mock_response

        player = LLMPlayer(response_model=CustomMove, move_field="action")
        opponent = axl.Cooperator()

        self.assertEqual(player.strategy(opponent), axl.Action.D)

        _, kwargs = mock_completion.call_args
        self.assertEqual(kwargs.get("response_model"), CustomMove)

    @patch("llm_player.litellm.completion")
    def test_fallback_strategy_on_llm_error(self, mock_completion):
        """Test that the player uses its fallback strategy if the LLM call fails."""
        mock_completion.side_effect = Exception("LLM API is unavailable")

        player = LLMPlayer()
        opponent = axl.Cooperator()

        with patch.object(
            LLMPlayer, "history", new_callable=PropertyMock
        ) as mock_history:
            # First move, history is empty
            mock_history.return_value = []
            self.assertEqual(player.strategy(opponent), axl.Action.C)

            # Subsequent move, history is not empty
            mock_history.return_value = [axl.Action.C]
            self.assertEqual(player.strategy(opponent), axl.Action.D)

    def test_prompt_generation(self):
        """Test prompt generation with the default file-based prompt."""
        player = LLMPlayer()
        opponent = axl.Cooperator()

        prompt_path = (
            pathlib.Path(__file__).parent.parent / "prompts" / "llm_player_prompt.md"
        )
        expected_template = prompt_path.read_text()

        with (
            patch.object(
                LLMPlayer, "history", new_callable=PropertyMock
            ) as mock_player_history,
            patch.object(
                axl.Cooperator, "history", new_callable=PropertyMock
            ) as mock_opponent_history,
        ):
            mock_player_history.return_value = [axl.Action.C, axl.Action.D]
            mock_opponent_history.return_value = [axl.Action.D, axl.Action.C]

            expected_prompt = expected_template.format(
                history="CD", opponent_history="DC"
            )
            self.assertEqual(player._generate_prompt(opponent), expected_prompt)

    def test_prompt_generation_at_start_of_game(self):
        """Test prompt generation at the start of the game."""
        player = LLMPlayer()
        opponent = axl.Cooperator()

        prompt_path = (
            pathlib.Path(__file__).parent.parent / "prompts" / "llm_player_prompt.md"
        )
        expected_template = prompt_path.read_text()

        with (
            patch.object(
                LLMPlayer, "history", new_callable=PropertyMock
            ) as mock_player_history,
            patch.object(
                axl.Cooperator, "history", new_callable=PropertyMock
            ) as mock_opponent_history,
        ):
            mock_player_history.return_value = []
            mock_opponent_history.return_value = []

            expected_prompt = expected_template.format(
                history="None", opponent_history="None"
            )
            self.assertEqual(player._generate_prompt(opponent), expected_prompt)

    def test_custom_prompt_template(self):
        """Test that a custom prompt template can be used."""
        custom_prompt = (
            "Your history: {history}. Opponent: {opponent_history}. Your move?"
        )
        player = LLMPlayer(prompt_template=custom_prompt)
        opponent = axl.Cooperator()

        with (
            patch.object(
                LLMPlayer, "history", new_callable=PropertyMock
            ) as mock_player_history,
            patch.object(
                axl.Cooperator, "history", new_callable=PropertyMock
            ) as mock_opponent_history,
        ):
            mock_player_history.return_value = ["C"]
            mock_opponent_history.return_value = ["D"]

            expected_prompt = "Your history: C. Opponent: D. Your move?"
            self.assertEqual(player._generate_prompt(opponent), expected_prompt)

    def test_logging(self):
        """Test that LLM responses and errors are logged."""
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        # Use a unique logger name to avoid conflicts
        logger = logging.getLogger("llm_player_test_logger")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        # Test successful response logging
        with patch("llm_player.litellm.completion") as mock_completion:
            mock_response = DefaultResponse(move="C", rationale="Test log.")
            mock_completion.return_value = mock_response

            player = LLMPlayer(logger=logger)
            opponent = axl.Cooperator()
            player.strategy(opponent)

            log_contents = log_stream.getvalue()
            self.assertIn("LLM response", log_contents)
            self.assertIn("Test log", log_contents)

        # Clear the stream for the next test
        log_stream.truncate(0)
        log_stream.seek(0)

        # Test error logging
        with patch("llm_player.litellm.completion") as mock_completion:
            mock_completion.side_effect = Exception("Test error")

            player = LLMPlayer(logger=logger)
            opponent = axl.Cooperator()
            player.strategy(opponent)

            log_contents = log_stream.getvalue()
            self.assertIn("Error calling LLM", log_contents)
            self.assertIn("Test error", log_contents)


    @patch("llm_player.litellm.completion")
    def test_api_key_is_passed(self, mock_completion):
        """Test that the api_key is correctly passed to litellm."""
        mock_response = DefaultResponse(move="C")
        mock_completion.return_value = mock_response

        api_key = "sk-test-key"
        player = LLMPlayer(api_key=api_key)
        opponent = axl.Cooperator()
        player.strategy(opponent)

        mock_completion.assert_called_once()
        _, kwargs = mock_completion.call_args
        self.assertEqual(kwargs.get("api_key"), api_key)


    @patch("llm_player.litellm.completion")
    def test_fallback_on_invalid_llm_move(self, mock_completion):
        """Test that the player falls back if the LLM returns an invalid move."""
        mock_response = DefaultResponse(
            move="Invalid", rationale="Test invalid move."
        )
        mock_completion.return_value = mock_response

        player = LLMPlayer()
        opponent = axl.Cooperator()

        # The fallback is to Cooperate on the first turn.
        self.assertEqual(player.strategy(opponent), axl.Action.C)


if __name__ == "__main__":
    unittest.main()
