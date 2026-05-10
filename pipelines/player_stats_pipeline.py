from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from interfaces.player_stats_pipeline_interface import PlayerStatsPipelineInterface
from interfaces.players_repository_interface import PlayersRepositoryInterface
from interfaces.nba_player_stats_repository_interface import NBAPlayerStatsRepositoryInterface

class PlayerStatsPipeline(PlayerStatsPipelineInterface):
    def __init__(self, sports_stats_api: SportsStatsAPIInterface, players_repository: PlayersRepositoryInterface, nba_player_stats_repository: NBAPlayerStatsRepositoryInterface):
        self.sports_stats_api = sports_stats_api
        self.players_repository = players_repository
        self.nba_player_stats_repository = nba_player_stats_repository

    def get_player_stats(self, sport: str, season: int):
        if sport == 'basketball_nba':
            # Fetch all players for the sport and season
            players = self.players_repository.get_players(sport)

            for player in players:
                # Fetch stats for each player
                player_stats_response = self.sports_stats_api.get_player_stats(player_id=player.id, season=season, sport=sport)
                self.nba_player_stats_repository.insert_player_stats(player.id, player_stats_response.stats)
            
