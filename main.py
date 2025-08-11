"""
A basic example of how to use the LLMPlayer.

This script runs a single match between the LLMPlayer and TitForTat and
prints the results.

To run this, you must have an LLM provider's API key set as an environment
variable, for example:
export OPENAI_API_KEY="your-key-here"
"""
import axelrod as axl
from llm_player import LLMPlayer


def main():
    # Instantiate the LLMPlayer. It will use the default model and prompt.
    llm_player = LLMPlayer()

    # Create an opponent
    opponent = axl.TitForTat()

    # Set up and run the match
    match = axl.Match((llm_player, opponent), turns=10)
    results = match.play()

    print(f"Running a {match.turns}-turn match between {llm_player.name} and {opponent.name}.")
    print("History:")
    for p1_move, p2_move in results:
        print(f"  Player 1: {p1_move}, Player 2: {p2_move}")

    print("\nFinal Score:")
    print(f"  {llm_player.name}: {match.final_score_per_turn()[0]}")
    print(f"  {opponent.name}: {match.final_score_per_turn()[1]}")


if __name__ == "__main__":
    main()
