from abc import abstractmethod, ABC
from typing import Optional

class SportsStatsAPIInterface(ABC):
    @abstractmethod
    def get_teams(self, sport: str) -> dict:
        pass

    @abstractmethod
    def get_games(self, sport: str, season: int) -> dict:
        pass
    
    @abstractmethod
    def get_players(self, team_id: int, season: int):
        """
        Fetch players for a given team and season.
        Args:
            team_id (int): The team ID.
            season (int): The season year.
        Returns:
            SportsStatsAPIPlayersResponse: Response containing a list of players.
        """
        pass