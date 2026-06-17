from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import (
    BallDontLieMLBInjurySchema, BallDontLieMLBInjuriesResponse,
    BallDontLieMLBTeamSchema, BallDontLieMLBTeamResponse,
    BallDontLieMLBGameSchema, BallDontLieMLBGamesResponse,
    BallDontLieMLBPlayerStatsSchema, BallDontLieMLBPlayerStatsResponse,
    PlayersSchema, SportsStatsAPIPlayersResponse,
)


class BallDontLieMlbAPI(SportsStatsAPIInterface):
    BASE_URL = "https://api.balldontlie.io"

    def __init__(self, api_config: APIConfig, http_client: HTTPClient):
        self.api_key = api_config.get_api_key()
        self.http_client = http_client

    def _fetch_all_pages(self, endpoint: str, base_params: dict) -> list[dict]:
        all_items = []
        cursor = None

        while True:
            params = dict(base_params)
            params["per_page"] = 100
            if cursor is not None:
                params["cursor"] = cursor

            response = self.http_client.get(
                endpoint,
                headers={"Authorization": self.api_key},
                params=params,
            )
            payload = response.json()
            all_items.extend(payload.get("data", []))

            next_cursor = payload.get("meta", {}).get("next_cursor")
            if next_cursor is None:
                break

            cursor = next_cursor

        return all_items

    def get_teams(self, sport: str) -> BallDontLieMLBTeamResponse:
        response = self.http_client.get(
            f"{self.BASE_URL}/mlb/v1/teams",
            headers={"Authorization": self.api_key},
        )
        data = response.json()
        teams = [
            BallDontLieMLBTeamSchema(
                id=team["id"],
                abbreviation=team["abbreviation"],
                display_name=team["display_name"],
                name=team["display_name"],
                location=team["location"],
                league=team["league"],
                division=team["division"],
            )
            for team in data.get("data", [])
        ]
        return BallDontLieMLBTeamResponse(teams=teams)

    def get_games(self, sport: str, season: int, team_id: int) -> BallDontLieMLBGamesResponse:
        games_data = self._fetch_all_pages(
            f"{self.BASE_URL}/mlb/v1/games",
            {"team_ids[]": team_id, "seasons[]": season},
        )
        games = [
            BallDontLieMLBGameSchema(
                id=game["id"],
                season=game["season"],
                date=game.get("date"),
                status=game.get("status"),
                home_team_name=game["home_team"]["name"],
                home_team_id=game["home_team"]["id"],
                away_team_name=game["away_team"]["name"],
                away_team_id=game["away_team"]["id"],
                home_runs=game.get("home_team_data", {}).get("runs"),
                away_runs=game.get("away_team_data", {}).get("runs"),
            )
            for game in games_data
        ]
        return BallDontLieMLBGamesResponse(games=games)

    def get_players(self, team_id: int, season: int) -> SportsStatsAPIPlayersResponse:
        _ = season
        players_data = self._fetch_all_pages(
            f"{self.BASE_URL}/mlb/v1/players",
            {"team_ids[]": team_id},
        )
        players = [
            PlayersSchema(
                id=player["id"],
                firstname=player["first_name"],
                lastname=player["last_name"],
            )
            for player in players_data
        ]
        return SportsStatsAPIPlayersResponse(players=players)

    def get_player_stats(self, player_id: int, season: int, sport: str) -> BallDontLieMLBPlayerStatsResponse:
        _ = sport
        stats_data = self._fetch_all_pages(
            f"{self.BASE_URL}/mlb/v1/stats",
            {"player_ids[]": player_id, "seasons[]": season},
        )
        stats_list = []
        for stat in stats_data:
            player = stat.get("player", {})
            stats_list.append(BallDontLieMLBPlayerStatsSchema(
                player_id=player.get("id"),
                firstname=player.get("first_name"),
                lastname=player.get("last_name"),
                team_name=player.get("team", {}).get("name"),
                game_id=stat.get("game_id"),
                season=season,
                at_bats=stat.get("at_bats"),
                hits=stat.get("hits"),
                hr=stat.get("hr"),
                rbi=stat.get("rbi"),
                bb=stat.get("bb"),
                k=stat.get("k"),
                avg=stat.get("avg"),
                obp=stat.get("obp"),
                slg=stat.get("slg"),
                doubles=stat.get("doubles"),
                triples=stat.get("triples"),
                stolen_bases=stat.get("stolen_bases"),
                plate_appearances=stat.get("plate_appearances"),
                total_bases=stat.get("total_bases"),
                ip=stat.get("ip"),
                p_k=stat.get("p_k"),
                p_bb=stat.get("p_bb"),
                er=stat.get("er"),
                era=stat.get("era"),
                pitch_count=stat.get("pitch_count"),
                wins=stat.get("wins"),
                losses=stat.get("losses"),
                saves=stat.get("saves"),
                games_started=stat.get("games_started"),
            ))

        return BallDontLieMLBPlayerStatsResponse(stats=stats_list)

    def get_injuries(self, team_id: int) -> BallDontLieMLBInjuriesResponse:
        injuries_data = self._fetch_all_pages(
            f"{self.BASE_URL}/mlb/v1/player_injuries",
            {"team_ids[]": team_id},
        )
        injuries = [
            BallDontLieMLBInjurySchema(**injury)
            for injury in injuries_data
        ]
        return BallDontLieMLBInjuriesResponse(injuries=injuries)
