from schemas.sports_stats_api_responses import SportsStatsAPIGamesResponse, GamesSchema
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import SportsStatsApiTeamResponse, TeamSchema, GamesSchema, SportsStatsAPIGamesResponse
from datetime import datetime


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
    

    def get_games(self, sport: str, season: int, team_id: int) -> SportsStatsAPIGamesResponse:
            """
            Fetch games for a given sport from the Sports IO API and transform to GamesSchema.
            Args:
                sport (str): The sport for which to fetch games (e.g., 'basketball_nba').
            Returns:
                SportsStatsAPIGamesResponse: Response containing a list of games.
            """
            response = self.http_client.get(
                f"https://v2.nba.api-sports.io/games",
                headers={"x-apisports-key": self.api_key}
            , params={"season": season, "team": team_id}
            )
            data = response.json()
            games = []
            for game in data.get("response", []):
                games.append(GamesSchema(
                    id=game["id"],
                    season=game["season"],
                    date=datetime.fromisoformat(game["date"]["start"].replace("Z", "+00:00")),
                    status=game["status"]["long"],
                    home_team=game["teams"]["home"]["name"],
                    home_team_id=game["teams"]["home"]["id"],
                    away_team=game["teams"]["visitors"]["name"],
                    away_team_id=game["teams"]["visitors"]["id"],
                    home_team_score=game["scores"]["home"]["points"],
                    away_team_score=game["scores"]["visitors"]["points"]
                ))

            return SportsStatsAPIGamesResponse(games=games)
