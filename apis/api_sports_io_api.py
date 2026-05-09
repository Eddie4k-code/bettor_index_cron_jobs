from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import SportsStatsApiTeamResponse, TeamSchema


class SportsIOAPI(SportsStatsAPIInterface):
    def __init__(self, api_config: APIConfig, http_client: HTTPClient):
        self.api_key = api_config.get_api_key()
        self.http_client = http_client

    def get_teams(self, sport: str) -> SportsStatsApiTeamResponse:
        """
        Fetch teams for a given sport from the Sports IO API.
        Args:
            sport (str): The sport for which to fetch teams (e.g., 'basketball_nba').
        Returns:
            SportsStatsApiTeamResponse: Response containing a list of teams.
        """
        response = self.http_client.get(f"https://v2.nba.api-sports.io/teams", headers={"x-apisports-key": self.api_key})
        data = response.json()
        teams = [TeamSchema(**team) for team in data.get("response", [])]
        return SportsStatsApiTeamResponse(teams=teams)


        