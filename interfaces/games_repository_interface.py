from abc import ABC, abstractmethod
from db.models.games import Game

class GamesRepositoryInterface(ABC):
    @abstractmethod
    def insert_games(self, game: Game) -> list[dict]:
        pass

    @abstractmethod 
    def get_game(self, game_id: int, sport_key: str) -> Game:
        pass