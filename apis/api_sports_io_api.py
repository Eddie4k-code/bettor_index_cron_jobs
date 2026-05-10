from schemas.sports_stats_api_responses import SportsStatsAPIGamesResponse, GamesSchema
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import SportsStatsApiTeamResponse, TeamSchema, GamesSchema, SportsStatsAPIGamesResponse
from datetime import datetime
from schemas.sports_stats_api_responses import PlayersSchema, SportsStatsAPIPlayersResponse
from schemas.sports_stats_api_responses import PlayerStatsSchemaNBA, SportsStatsAPIPlayerStatsResponse

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


    def get_players(self, team_id: int, season: int):
            """
            Fetch players for a given team and season from the Sports IO API and transform to PlayersSchema.
            Args:
                team_id (int): The team ID.
                season (int): The season year.
            Returns:
                SportsStatsAPIPlayersResponse: Response containing a list of players.
            """
            response = self.http_client.get(
                f"https://v2.nba.api-sports.io/players",
                headers={"x-apisports-key": self.api_key},
                params={"team": team_id, "season": season}
            )
            data = response.json()
            players = [PlayersSchema(
                id=player["id"],
                firstname=player["firstname"],
                lastname=player["lastname"]
            ) for player in data.get("response", [])]
            return SportsStatsAPIPlayersResponse(players=players)
    

    def get_player_stats(self, player_id: int, season: int, sport: str):
        """
        Fetch stats for a given player and season from the Sports IO API.
        Args:
            player_id (int): The player ID.
            season (int): The season year.
        Returns:
            SportsStatsAPIPlayerStatsResponse: Response containing player stats.
        """
        response = self.http_client.get(
            f"https://v2.nba.api-sports.io/players/statistics",
            headers={"x-apisports-key": self.api_key},
            params={"id": player_id, "season": season}
        )
        data = response.json()
        stats_data = data.get("response", [])

        stats_list = []
        for game in stats_data:
            stats = PlayerStatsSchemaNBA(
                player_id=game.get("player", {}).get("id"),
                firstname=game.get("player", {}).get("firstname"),
                lastname=game.get("player", {}).get("lastname"),
                team_id=game.get("team", {}).get("id"),
                game_id=game.get("game", {}).get("id"),
                season=season,
                min=game.get("min"),
                points=game.get("points"),
                pos=game.get("pos"),
                fgm=game.get("fgm"),
                fga=game.get("fga"),
                fgp=game.get("fgp"),
                ftm=game.get("ftm"),
                fta=game.get("fta"),
                ftp=game.get("ftp"),
                tpm=game.get("tpm"),
                tpa=game.get("tpa"),
                tpp=game.get("tpp"),
                offReb=game.get("offReb"),
                defReb=game.get("defReb"),
                totReb=game.get("totReb"),
                assists=game.get("assists"),
                pFouls=game.get("pFouls"),
                steals=game.get("steals"),
                turnovers=game.get("turnovers"),
                blocks=game.get("blocks")
            )
            stats_list.append(stats)

        return SportsStatsAPIPlayerStatsResponse(stats=stats_list)


