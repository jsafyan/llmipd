import unittest
from unittest.mock import patch

import axelrod as axl

from llm_player import LLMPlayer


def mock_tft_completion(model, messages, response_model, api_key, **kwargs):
    """
    A mock for litellm.completion that simulates a Tit-for-Tat strategy.
    It inspects the prompt to find the opponent's last move.
    """
    prompt = messages[0]["content"]
    move = "C"  # Default to cooperate

    # This is a simplified parser for debugging the integration test.
    if "Opponent's history: C" in prompt:
        move = "C"
    elif "Opponent's history: D" in prompt:
        move = "D"
    # This mock will only work for single-character histories, but that's
    # enough to test the first few rounds of TFT vs TFT.

    return response_model(move=move, rationale="Mocked TFT response.")


class TestLLMPlayerIntegration(unittest.TestCase):
    @patch("llm_player.litellm.completion", side_effect=mock_tft_completion)
    def test_match_with_tit_for_tat(self, mock_completion):
        """
        Tests the LLMPlayer in a full match against TitForTat.
        The mocked LLM is designed to also play TitForTat, so the expected
        outcome is mutual cooperation.
        """
        player = LLMPlayer()
        opponent = axl.TitForTat()

        match = axl.Match((player, opponent), turns=5)
        results = match.play()

        # Since the mocked LLM plays TFT, and it's playing against TFT,
        # they should cooperate for all rounds.
        expected_history = [
            (axl.Action.C, axl.Action.C),
            (axl.Action.C, axl.Action.C),
            (axl.Action.C, axl.Action.C),
            (axl.Action.C, axl.Action.C),
            (axl.Action.C, axl.Action.C),
        ]
        self.assertEqual(results, expected_history)
        self.assertEqual(match.final_score_per_turn(), (3, 3))


if __name__ == "__main__":
    unittest.main()
