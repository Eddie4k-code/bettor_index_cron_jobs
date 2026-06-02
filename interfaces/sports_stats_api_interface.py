from abc import abstractmethod, ABC
from typing import Optional

from schemas.sports_stats_api_responses import BallDontLieMLBGamesResponse, SportsStatsAPIGamesResponse

class SportsStatsAPIInterface(ABC):
    @abstractmethod
    def get_teams(self, sport: str) -> dict:
        pass

    @abstractmethod
    def get_games(self, sport: str, season: int) -> BallDontLieMLBGamesResponse | SportsStatsAPIGamesResponse:
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

    @abstractmethod
    def get_player_stats(self, player_id: int, season: int):
        """
        Fetch stats for a given player and season.
        Args:
            player_id (int): The player ID.
            season (int): The season year.
        Returns:
            SportsStatsAPIPlayerStatsResponse: Response containing player stats.
        """
        pass