from interfaces.games_pipeline_interface import GamesPipelineInterface
from interfaces.games_repository_interface import GamesRepositoryInterface
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from interfaces.teams_repository_interface import TeamsRepositoryInterface

class GamesPipeline(GamesPipelineInterface):
    def __init__(self, games_repository: GamesRepositoryInterface, teams_repository: TeamsRepositoryInterface, api: SportsStatsAPIInterface):
        self.games_repository = games_repository
        self.teams_repository = teams_repository
        self.api = api

    def get_games(self, sport: str, season: int) -> list[dict]:
        pass