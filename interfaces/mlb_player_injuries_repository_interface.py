from abc import ABC, abstractmethod

from db.models.mlb_player_injuries import MLBPlayerInjuries


class MLBPlayerInjuriesRepositoryInterface(ABC):
    @abstractmethod
    def insert_player_injury(self, player_injury: MLBPlayerInjuries):
        pass