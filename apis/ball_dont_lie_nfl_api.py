from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import (
    BallDontLieNFLInjuriesResponse,
    BallDontLieNFLInjuryPlayerSchema,
    BallDontLieNFLInjurySchema,
    BallDontLieNFLInjuryTeamSchema,
    BallDontLieNFLGameSchema,
    BallDontLieNFLGamesResponse,
    BallDontLieNFLPlayerStatsSchema,
    BallDontLieNFLPlayerStatsResponse,
    BallDontLieNFLTeamSchema,
    BallDontLieNFLTeamResponse,
    PlayersSchema,
    SportsStatsAPIPlayersResponse,
)


class BallDontLieNflAPI(SportsStatsAPIInterface):
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

    def get_teams(self, sport: str) -> BallDontLieNFLTeamResponse:
        _ = sport
        response = self.http_client.get(
            f"{self.BASE_URL}/nfl/v1/teams",
            headers={"Authorization": self.api_key},
        )
        data = response.json()
        teams = [
            BallDontLieNFLTeamSchema(
                id=team["id"],
                abbreviation=team["abbreviation"],
                full_name=team["full_name"],
                name=team["name"],
                location=team["location"],
                conference=team["conference"],
                division=team["division"],
            )
            for team in data.get("data", [])
        ]
        return BallDontLieNFLTeamResponse(teams=teams)

    def get_games(self, sport: str, season: int, team_id: int) -> BallDontLieNFLGamesResponse:
        _ = sport
        games_data = self._fetch_all_pages(
            f"{self.BASE_URL}/nfl/v1/games",
            {"team_ids[]": team_id, "seasons[]": season},
        )
        games = [
            BallDontLieNFLGameSchema(
                id=game["id"],
                season=game["season"],
                week=game.get("week"),
                date=game.get("date"),
                status=game.get("status"),
                postseason=game.get("postseason"),
                home_team_name=game["home_team"]["full_name"],
                home_team_id=game["home_team"]["id"],
                away_team_name=game["visitor_team"]["full_name"],
                away_team_id=game["visitor_team"]["id"],
                home_team_score=game.get("home_team_score"),
                away_team_score=game.get("visitor_team_score"),
            )
            for game in games_data
        ]
        return BallDontLieNFLGamesResponse(games=games)

    def get_players(self, team_id: int, season: int) -> SportsStatsAPIPlayersResponse:
        _ = season
        players_data = self._fetch_all_pages(
            f"{self.BASE_URL}/nfl/v1/players",
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

    def get_player_stats(self, player_id: int, season: int, sport: str) -> BallDontLieNFLPlayerStatsResponse:
        _ = sport
        stats_data = self._fetch_all_pages(
            f"{self.BASE_URL}/nfl/v1/stats",
            {"player_ids[]": player_id, "seasons[]": season},
        )
        stats_list = []
        for stat in stats_data:
            player = stat.get("player", {})
            game = stat.get("game", {})
            stats_list.append(BallDontLieNFLPlayerStatsSchema(
                player_id=player.get("id"),
                firstname=player.get("first_name"),
                lastname=player.get("last_name"),
                team_name=player.get("team", {}).get("full_name"),
                game_id=game.get("id"),
                season=game.get("season", season),
                passing_completions=stat.get("passing_completions"),
                passing_attempts=stat.get("passing_attempts"),
                passing_yards=stat.get("passing_yards"),
                yards_per_pass_attempt=stat.get("yards_per_pass_attempt"),
                passing_touchdowns=stat.get("passing_touchdowns"),
                passing_interceptions=stat.get("passing_interceptions"),
                sacks=stat.get("sacks"),
                sacks_loss=stat.get("sacks_loss"),
                qbr=stat.get("qbr"),
                qb_rating=stat.get("qb_rating"),
                rushing_attempts=stat.get("rushing_attempts"),
                rushing_yards=stat.get("rushing_yards"),
                yards_per_rush_attempt=stat.get("yards_per_rush_attempt"),
                rushing_touchdowns=stat.get("rushing_touchdowns"),
                long_rushing=stat.get("long_rushing"),
                receptions=stat.get("receptions"),
                receiving_yards=stat.get("receiving_yards"),
                yards_per_reception=stat.get("yards_per_reception"),
                receiving_touchdowns=stat.get("receiving_touchdowns"),
                long_reception=stat.get("long_reception"),
                receiving_targets=stat.get("receiving_targets"),
                fumbles=stat.get("fumbles"),
                fumbles_lost=stat.get("fumbles_lost"),
                fumbles_recovered=stat.get("fumbles_recovered"),
                total_tackles=stat.get("total_tackles"),
                defensive_sacks=stat.get("defensive_sacks"),
                solo_tackles=stat.get("solo_tackles"),
                tackles_for_loss=stat.get("tackles_for_loss"),
                passes_defended=stat.get("passes_defended"),
                qb_hits=stat.get("qb_hits"),
                fumbles_touchdowns=stat.get("fumbles_touchdowns"),
                defensive_interceptions=stat.get("defensive_interceptions"),
                interception_yards=stat.get("interception_yards"),
                interception_touchdowns=stat.get("interception_touchdowns"),
                kick_returns=stat.get("kick_returns"),
                kick_return_yards=stat.get("kick_return_yards"),
                yards_per_kick_return=stat.get("yards_per_kick_return"),
                long_kick_return=stat.get("long_kick_return"),
                kick_return_touchdowns=stat.get("kick_return_touchdowns"),
                punt_returns=stat.get("punt_returns"),
                punt_return_yards=stat.get("punt_return_yards"),
                yards_per_punt_return=stat.get("yards_per_punt_return"),
                long_punt_return=stat.get("long_punt_return"),
                punt_return_touchdowns=stat.get("punt_return_touchdowns"),
                field_goal_attempts=stat.get("field_goal_attempts"),
                field_goals_made=stat.get("field_goals_made"),
                field_goal_pct=stat.get("field_goal_pct"),
                long_field_goal_made=stat.get("long_field_goal_made"),
                extra_points_made=stat.get("extra_points_made"),
                total_points=stat.get("total_points"),
                punts=stat.get("punts"),
                punt_yards=stat.get("punt_yards"),
                gross_avg_punt_yards=stat.get("gross_avg_punt_yards"),
                touchbacks=stat.get("touchbacks"),
                punts_inside_20=stat.get("punts_inside_20"),
                long_punt=stat.get("long_punt"),
            ))

        return BallDontLieNFLPlayerStatsResponse(stats=stats_list)

    def get_injuries(self, team_ids: list[int]) -> BallDontLieNFLInjuriesResponse:
        injuries_data = self._fetch_all_pages(
            f"{self.BASE_URL}/nfl/v1/player_injuries",
            {"team_ids[]": team_ids},
        )
        injuries = []
        for injury in injuries_data:
            player_data = injury.get("player", {})
            team_data = player_data.get("team", {})
            injuries.append(BallDontLieNFLInjurySchema(
                player=BallDontLieNFLInjuryPlayerSchema(
                    id=player_data["id"],
                    first_name=player_data["first_name"],
                    last_name=player_data["last_name"],
                    position=player_data.get("position"),
                    position_abbreviation=player_data.get("position_abbreviation"),
                    jersey_number=player_data.get("jersey_number"),
                    team=BallDontLieNFLInjuryTeamSchema(
                        id=team_data["id"],
                        abbreviation=team_data["abbreviation"],
                        full_name=team_data["full_name"],
                        name=team_data["name"],
                        location=team_data["location"],
                        conference=team_data["conference"],
                        division=team_data["division"],
                    ),
                ),
                status=injury.get("status"),
                comment=injury.get("comment"),
                date=injury.get("date"),
            ))
        return BallDontLieNFLInjuriesResponse(injuries=injuries)
