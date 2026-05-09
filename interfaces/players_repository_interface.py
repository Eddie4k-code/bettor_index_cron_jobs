from abc import ABC, abstractmethod
from db.models.player import Player

class PlayersRepositoryInterface(ABC):
    @abstractmethod
    def insert_player(self, player: Player):
        """
        Insert a player into the database.
        Args:
            player (Player): The Player object to insert.
        """
        pass
