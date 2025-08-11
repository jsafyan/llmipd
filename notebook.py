import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import axelrod as axl
    import os
    from llm_player import LLMPlayer
    import logging
    import io

    # This is a demonstration notebook for the LLMPlayer.
    # To run this, you need to have an LLM provider's API key set as an
    # environment variable (e.g., ANTHROPIC_API_KEY, OPENAI_API_KEY).
    return axl, io, LLMPlayer, logging, mo, os


@app.cell
def __(mo):
    mo.md(
        """
        # Demonstrating the `LLMPlayer` for `axelrod`

        This notebook shows how to use the `LLMPlayer`, which uses `litellm`
        to connect to various Large Language Models to play the Iterated
        Prisoner's Dilemma.
        """
    )
    return


@app.cell
def __(LLMPlayer, mo):
    # Instantiate the player with the default settings
    # It will use the default prompt and a Claude Haiku model.
    default_player = LLMPlayer()

    mo.md(f"**Default Player:** `{default_player.name}`")
    return default_player,


@app.cell
def __(LLMPlayer, mo):
    # You can customize the player with a different model and a custom name.
    custom_player = LLMPlayer(model="gpt-4o-mini", name="My GPT Player")

    mo.md(f"**Custom Player:** `{custom_player.name}`")
    return custom_player,


@app.cell
def __(LLMPlayer, axl, default_player, mo):
    # Run a small tournament against some classic strategies
    opponents = [axl.Cooperator(), axl.Defector(), axl.TitForTat()]
    players = opponents + [default_player]

    tournament = axl.Tournament(players, turns=5, repetitions=1)
    results = tournament.play(progress_bar=False)

    mo.md(
        f"""
        ### Tournament Results (Default Player)

        {results.summarise().to_markdown()}
        """
    )
    return opponents, players, results, tournament


@app.cell
def __(LLMPlayer, axl, custom_player, mo):
    # Run another tournament with the custom player
    opponents = [axl.Cooperator(), axl.Defector(), axl.TitForTat()]
    players = opponents + [custom_player]

    tournament = axl.Tournament(players, turns=5, repetitions=1)
    results = tournament.play(progress_bar=False)

    mo.md(
        f"""
        ### Tournament Results (Custom Player)

        {results.summarise().to_markdown()}
        """
    )
    return


@app.cell
def __(LLMPlayer, io, logging, mo):
    mo.md(
        """
        ## Logging LLM Responses

        You can pass a logger to the `LLMPlayer` to capture the raw
        responses from the LLM.
        """
    )

    # Set up a logger that writes to a string buffer
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger("notebook_logger")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Create a player with the logger
    logged_player = LLMPlayer(logger=logger)
    return handler, log_stream, logged_player, logger


@app.cell
def __(axl, logged_player, log_stream, mo, results):
    # Run a single match to generate a log
    match = axl.Match((logged_player, axl.Defector()), turns=2)
    results = match.play()

    mo.md(
        f"""
        The following logs were captured from the LLM interaction:

        ```
        {log_stream.getvalue()}
        ```
        """
    )
    return match,


if __name__ == "__main__":
    app.run()
