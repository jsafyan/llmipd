import csv
import datetime
from typing import List, Tuple

import axelrod as axl
from tenacity import retry, stop_after_attempt, wait_exponential


class LLMPlayer(axl.Player):
    def __init__(self, model: str, name: str = "LLM Player", max_retries: int = 5):
        super().__init__()
        self.model = model
        self.match_seed = None
        self.name = name
        self.max_retries = max_retries
        self.log_file = f"llm_api_log_{datetime.datetime.now().strftime('%Y%m%d')}.csv"
        self._initialize_log_file()

    def set_seed(self, seed):
        self.match_seed = seed

    def strategy(self, opponent: axl.Player) -> str:
        history = list(zip(self.history, opponent.history))
        move = self.get_move(history, opponent.name)
        return move

    @retry(
        stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=64)
    )
    def get_move(self, history: List[Tuple[str, str]], opponent_name: str) -> str:
        raise NotImplementedError("Subclasses should implement get_move method")

    def _initialize_log_file(self):
        with open(self.log_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "date",
                    "opponent_name",
                    "match_history",
                    "model_name",
                    "llm_move",
                    "error",
                    "additional_info",
                ]
            )

    def _log_api_call(
        self,
        opponent_name: str,
        history: List[Tuple[str, str]],
        move: str,
        error: str = "",
        additional_info: str = "",
    ):
        with open(self.log_file, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    datetime.datetime.now().isoformat(),
                    opponent_name,
                    str(history),
                    self.model,
                    move,
                    error,
                    additional_info,
                ]
            )
