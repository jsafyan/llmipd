import marimo

__generated_with = "0.10.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import axelrod as axl
    import os
    from groq_player import GroqPlayer, DEFAULT_SYSTEM_INSTRUCTIONS
    from anthropic_player import AnthropicPlayer
    import random
    import textwrap
    return (
        AnthropicPlayer,
        DEFAULT_SYSTEM_INSTRUCTIONS,
        GroqPlayer,
        axl,
        mo,
        os,
        random,
        textwrap,
    )


@app.cell
def _(mo, os):
    # Check if API keys are set
    def check_env_var(var_name):
        if var_name not in os.environ:
            return False
        return True


    mo.md(f"""
    API keys found in env: \n
    - Groq: {check_env_var("GROQ_API_KEY")} \n
    - Anthropic: {check_env_var("ANTHROPIC_API_KEY")}""")
    return (check_env_var,)


@app.cell
def _(mo):
    # Load and show default system prompt
    with open("prompts/system_prompt.txt", "r") as f:
        system_prompt = f.read()
    mo.md(f"### Default system prompt: \n {system_prompt}")
    return f, system_prompt


@app.cell
def _(AnthropicPlayer, axl):
    # Create a player with the default system prompt
    llm_player = AnthropicPlayer(model="claude-3-5-haiku-20241022", max_retries=3)

    # Set up some opponents
    opponents = [axl.TitForTat()]
    return llm_player, opponents


@app.cell
def _(axl, random):
    # Function to run a small tournament
    def run_tournament(players, seed=42):
        random.seed(seed)
        tournament = axl.Tournament(
            players,
            turns=5,  # Shorter game for demonstration
            repetitions=1,
            seed=seed,
        )
        results = tournament.play(processes=1, progress_bar=True)
        return results
    return (run_tournament,)


@app.cell
def _(llm_player, opponents, run_tournament):
    players = opponents + [llm_player]
    results = run_tournament(players)
    return players, results


@app.cell
def _(results):
    results.ranked_names
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
