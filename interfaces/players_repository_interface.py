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

    @abstractmethod
    def get_players(self, sport: str):
        """
        Fetch all players for a given sport.
        Args:
            sport (str): The sport key to filter players by.
        Returns:
            list[Player]: List of Player objects for the sport.
        """
        pass

    @abstractmethod
    def get_player_by_name(self, first_name: str, last_name: str, sport: str):
        """
        Fetch a player by their first name, last name, and sport.
        Args:
            first_name (str): The player's first name.
            last_name (str): The player's last name.
            sport (str): The sport key to filter players by.
        Returns:
            list[Player]: List of Player objects matching the name and sport.
        """
        pass

    @abstractmethod
    def get_player_by_id(self, player_id: int, sport: str):
        """
        Fetch a player by their ID and sport.
        Args:
            player_id (int): The player ID.
            sport (str): The sport key to filter players by.
        Returns:
            Player | None: The matching player object, if found.
        """
        pass
