"""
An advanced, resumable tournament runner.

This script runs a round-robin tournament between the LLMPlayer and a set of
other strategies. It is designed to be robust to interruptions.

Key features:
- Runs a tournament as a series of individual matches.
- Saves the results of each match to a CSV file as it completes.
- Automatically resumes the tournament from where it left off if the script
  is stopped and restarted.
- Demonstrates how to configure the LLMPlayer with a custom model, prompt,
  and logger.

To run this, you must have an LLM provider's API key set as an environment
variable, for example:
export OPENAI_API_KEY="your-key-here"
"""
import argparse
import itertools
import logging
import os
import random

import axelrod as axl
import pandas as pd
from llm_player import LLMPlayer


def get_strategies(llm_model, llm_prompt_file, logger):
    """Returns the list of strategies for the tournament."""
    prompt_template = None
    if llm_prompt_file:
        with open(llm_prompt_file) as f:
            prompt_template = f.read()

    llm_player = LLMPlayer(
        model=llm_model, prompt_template=prompt_template, logger=logger
    )

    # A selection of famous and effective strategies from the Axelrod library
    strategies = [
        axl.Cooperator(),
        axl.Defector(),
        axl.TitForTat(),
        axl.Grudger(),
        axl.Random(),
        axl.EvolvedLookerUp2_2_2(),
        axl.EvolvedFSM16(),
        axl.PSOGambler2_2_2(),
        llm_player,
    ]
    return strategies


def run_resumable_tournament(
    strategies, turns, repetitions, output_file, seed
):
    """
    Runs a round-robin tournament, saving results after each match.
    """
    # Create a list of all unique pairs of strategies
    player_pairs = list(itertools.combinations(strategies, 2))

    # Check if the output file exists to resume
    try:
        results_df = pd.read_csv(output_file)
        print(f"Resuming tournament from existing results file: {output_file}")
    except FileNotFoundError:
        results_df = pd.DataFrame(
            columns=["player1", "player2", "player1_score", "player2_score"]
        )

    for p1_class, p2_class in player_pairs:
        # Check if this match result already exists
        if (
            not results_df.empty
            and not results_df[
                (results_df["player1"] == p1_class.name)
                & (results_df["player2"] == p2_class.name)
            ].empty
        ):
            print(f"Skipping existing match: {p1_class.name} vs {p2_class.name}")
            continue

        print(f"Running match: {p1_class.name} vs {p2_class.name}")
        # Instantiate players for the match
        p1 = p1_class()
        p2 = p2_class()

        match = axl.Match((p1, p2), turns=turns, seed=seed)
        match.play()

        # Append result to the DataFrame and save
        new_result = pd.DataFrame(
            [
                {
                    "player1": p1.name,
                    "player2": p2.name,
                    "player1_score": match.final_score_per_turn()[0],
                    "player2_score": match.final_score_per_turn()[1],
                }
            ]
        )
        results_df = pd.concat([results_df, new_result], ignore_index=True)
        results_df.to_csv(output_file, index=False)

    print("\nTournament complete.")
    print("Final Results:")
    print(results_df)


def main():
    parser = argparse.ArgumentParser(description="Run a resumable tournament.")
    parser.add_argument(
        "--model",
        default="gemini/gemini-2.5-flash-lite",
        help="LLM model name for the LLMPlayer.",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Path to a custom prompt file for the LLMPlayer.",
    )
    parser.add_argument(
        "--log-file",
        default="llm_responses.log",
        help="File to write LLM response logs to.",
    )
    parser.add_argument(
        "--output-csv",
        default="tournament_results.csv",
        help="CSV file to save tournament results.",
    )
    parser.add_argument(
        "--turns", type=int, default=50, help="Number of turns per match."
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=5,
        help="Number of repetitions (not used in this script, but common).",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
    )
    logger = logging.getLogger("LLMPlayerLogger")

    # Set seed for reproducibility
    if args.seed:
        random.seed(args.seed)
        axl.seed(args.seed)

    strategies = get_strategies(args.model, args.prompt, logger)
    run_resumable_tournament(
        strategies, args.turns, args.repetitions, args.output_csv, args.seed
    )


if __name__ == "__main__":
    main()
