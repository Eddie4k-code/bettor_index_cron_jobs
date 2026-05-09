from interfaces.games_pipeline_interface import GamesPipelineInterface
from interfaces.games_repository_interface import GamesRepositoryInterface
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from interfaces.teams_repository_interface import TeamsRepositoryInterface
from db.models.games import Game

class GamesPipeline(GamesPipelineInterface):
    def __init__(self, games_repository: GamesRepositoryInterface, teams_repository: TeamsRepositoryInterface, api: SportsStatsAPIInterface):
        self.games_repository = games_repository
        self.teams_repository = teams_repository
        self.api = api

    def get_games(self, sport: str, season: int) -> list[dict]:
        
        # Get Teams
        teams = self.teams_repository.get_teams(sport)

        for team in teams:
            team_id = team.id
            response = self.api.get_games(sport, season, team_id)
            games_data = response["games"] if isinstance(response, dict) else getattr(response, "games", [])
            for game_schema in games_data:
                self.games_repository.insert_games(Game(
                    id=game_schema.id,
                    season=game_schema.season,
                    date=game_schema.date,
                    status=game_schema.status,
                    home_team=game_schema.home_team.lower() if game_schema.home_team else "unknown",
                    home_team_id=game_schema.home_team_id,
                    away_team=game_schema.away_team.lower() if game_schema.away_team else "unknown",
                    away_team_id=game_schema.away_team_id,
                    home_team_score=game_schema.home_team_score if game_schema.home_team_score is not None else 0,
                    away_team_score=game_schema.away_team_score if game_schema.away_team_score is not None else 0
                ))