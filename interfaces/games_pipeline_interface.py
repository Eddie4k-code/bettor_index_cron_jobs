from abc import ABC, abstractmethod

class GamesPipelineInterface(ABC):
    @abstractmethod
    def get_games(self, sport: str, season: int) -> list[dict]:
        pass