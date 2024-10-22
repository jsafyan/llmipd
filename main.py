import argparse
import datetime
import random

import axelrod as axl

from groq_player import GroqPlayer


def main():
    parser = argparse.ArgumentParser(
        description="Run Axelrod tournament with GroqPlayer"
    )
    parser.add_argument(
        "--model", default="llama-3.1-8b-instant", help="Groq model name"
    )
    parser.add_argument("--output_file", help="Output file name for tournament results")
    parser.add_argument(
        "--max_retries",
        type=int,
        default=5,
        help="Maximum number of retries for getting a move",
    )
    args = parser.parse_args()

    seed = 201  # Set a fixed seed for reproducibility
    random.seed(seed)  # Set seed for Python's random module
    groq_player = GroqPlayer(model=args.model, max_retries=args.max_retries)

    # Famous strategies
    famous_strategies = [axl.TitForTat(), axl.Grudger()]

    # Top players
    top_players = [
        axl.EvolvedLookerUp2_2_2(),
        axl.EvolvedHMM5(),
        axl.EvolvedANN5(),
        axl.EvolvedFSM16(),
        axl.EvolvedFSM16Noise05(),
        axl.PSOGambler2_2_2(),
        axl.PSOGamblerMem1(),
        axl.PSOGambler1_1_1(),
        axl.OmegaTFT(3, 8),
    ]

    players = famous_strategies + top_players + [groq_player]

    tournament = axl.Tournament(players, turns=50, repetitions=5, seed=seed)

    # Play the tournament with progress bar and parameterized output filename
    output_filename = (
        args.output_file
        or f"strategy_prompt_groq_{args.model}_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
    )
    results = tournament.play(filename=output_filename, processes=1, progress_bar=True)

    # Print summary
    print("\nTournament Results:")
    print("Ranked Names:", results.ranked_names)
    print("\nSummary:")
    print(results.summarise())


if __name__ == "__main__":
    main()
