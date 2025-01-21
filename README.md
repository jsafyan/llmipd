# llmipd

LLM Iterated Prisoner's Dilemma - Exploring how different models play the iterated prisoner's dilemma.

## Overview
This project uses various LLM APIs (e.g, Groq, Anthropic) to create players for the [Axelrod](https://axelrod.readthedocs.io/) library's implementation of the Iterated Prisoner's Dilemma.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jsafyan/llmipd.git
cd llmipd
```

2. Install dependencies:
```bash
uv pip install -r pyproject.toml
```

3. Set up API keys:
```bash
export GROQ_API_KEY='your-groq-api-key'
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

## Usage

### Interactive Notebook
The project includes a Marimo notebook for interactive experimentation:

```bash
marimo edit notebook.py
```

This will open a browser window where you can:
- View the system prompts being used
- Run tournaments with different LLM players
- See the results of matches

### Custom Players
The project includes two LLM-based players:
- `GroqPlayer`: Uses Groq's API
- `AnthropicPlayer`: Uses Anthropic's Claude API

Both inherit from the base `LLMPlayer` class and can be customized with different prompts and parameters.

## Project Structure
- `notebook.py`: Marimo notebook for interactive experiments
- `llm_player.py`: Base class for LLM-based players
- `groq_player.py`: Implementation using Groq's API
- `anthropic_player.py`: Implementation using Anthropic's API
- `prompts/`: Directory containing system prompts