from abc import ABC, abstractmethod
from db.models.games import Game

class GamesRepositoryInterface(ABC):
    @abstractmethod
    def insert_games(self, game: Game) -> list[dict]:
        pass