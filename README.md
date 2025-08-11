# LLM-based Players for the Axelrod Library

This project provides a flexible player for the `axelrod` library that uses Large Language Models (LLMs) to determine its strategy in the Iterated Prisoner's Dilemma.

It features a single `LLMPlayer` class that leverages the `litellm` library, allowing it to be configured to use a wide variety of LLM providers (e.g., OpenAI, Anthropic, Google Gemini, Groq, etc.).

## Features

-   **Multi-Provider LLM Support**: Uses `litellm` to connect to any supported LLM.
-   **Reliable Move Parsing**: Enforces structured JSON output for moves.
-   **Customizable Prompts**: A detailed default prompt is provided, which can be easily customized.
-   **Response Logging**: Includes an optional logger to store LLM responses.
-   **Resumable Tournament Example**: A script is provided to run long tournaments that can be resumed.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/llmipd.git
    cd llmipd
    ```

2.  Create a virtual environment and install the dependencies. This project uses `uv` for fast dependency management.
    ```bash
    uv venv
    uv pip install -r requirements.txt
    ```

3.  Set the API key for your chosen LLM provider as an environment variable. For example:
    ```bash
    export OPENAI_API_KEY="your-sk-..."
    ```
    Alternatively, you can pass the `api_key` directly to the `LLMPlayer` constructor.

## Quick Start: A Simple Match

The `main.py` script provides a simple example of running a single 10-turn match between the `LLMPlayer` (using the default model, `gemini/gemini-2.5-flash-lite`) and the classic `TitForTat` strategy.

```bash
python main.py
```
This will print the history of the match and the final scores.

## Advanced Usage: Running a Tournament

For more serious experiments, the `examples/run_tournament.py` script provides a way to run a round-robin tournament.

This script:
-   Plays every strategy against every other strategy in a defined list.
-   Runs each pairing as an individual `axelrod.Match`.
-   Saves the results of each match to a CSV file (`tournament_results.csv` by default) as soon as it's finished.
-   If the script is stopped and restarted, it will read the existing CSV and automatically skip any matches that have already been played.

### To run the tournament:

```bash
python examples/run_tournament.py
```

You can customize the tournament with command-line arguments:

-   `--model`: Specify a different LLM model string (e.g., `gpt-4o-mini`).
-   `--turns`: Set the number of turns for each match.
-   `--output-csv`: Specify a different file to save the results.
-   `--log-file`: Specify a file to save the raw LLM responses.

For example:
```bash
python examples/run_tournament.py --model gpt-4o-mini --turns 100 --output-csv my_tournament.csv
```

## Using `LLMPlayer` in your own code

You can easily import and use the `LLMPlayer` in your own `axelrod` experiments.

```python
import axelrod as axl
from llm_player import LLMPlayer

# Create a player with a specific model
my_llm_player = LLMPlayer(model="groq/llama3-70b-8192")

# Use it in a tournament
players = [axl.TitForTat(), axl.Grudger(), my_llm_player]
tournament = axl.Tournament(players, turns=50, repetitions=5)
results = tournament.play()
print(results.summary)
```

## Analyzing Tournament Results

After running a tournament with the `examples/run_tournament.py` script, you will have a `tournament_results.csv` file. You can use this file to analyze the performance of the `LLMPlayer`.

### Player Rankings

To get a simple ranking of the players, you can use a simple python script with `pandas`:

```python
import pandas as pd

# Load the results
df = pd.read_csv("tournament_results.csv")

# Calculate total scores for each player
scores = {}
for index, row in df.iterrows():
    p1 = row["player1"]
    p2 = row["player2"]
    s1 = row["player1_score"]
    s2 = row["player2_score"]

    scores[p1] = scores.get(p1, 0) + s1
    scores[p2] = scores.get(p2, 0) + s2

# Create a ranked list
ranked_players = sorted(scores.items(), key=lambda item: item[1], reverse=True)

print("Player Rankings:")
for player, score in ranked_players:
    print(f"- {player}: {score}")
```

