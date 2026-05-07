from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import SportsStatsApiTeamResponse, TeamSchema


class SportsIOAPI(SportsStatsAPIInterface):
    def __init__(self, api_config: APIConfig, http_client: HTTPClient):
        self.api_key = api_config.get_api_key()
        self.http_client = http_client

    def get_teams(self, sport: str, season: int = None) -> SportsStatsApiTeamResponse:
        """
        Fetch teams for a given sport and season from the Sports IO API.
        Args:
            sport (str): The sport for which to fetch teams (e.g., 'basketball_nba').
            season (int, optional): The season year (e.g., 2023). If None, fetches current season teams.
        Returns:
            SportsStatsApiTeamResponse: Response containing a list of teams.
        """
        # ...existing code...
        response = self.http_client.get(f"https://v2.nba-api-sports.io/teams", headers={"x-apisports-key": self.api_key})
        data = response.json()
        teams = [TeamSchema(**team) for team in data.get("teams", [])]
        return SportsStatsApiTeamResponse(teams=teams)


        