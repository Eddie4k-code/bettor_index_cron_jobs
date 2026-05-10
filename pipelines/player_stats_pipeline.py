from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from interfaces.player_stats_pipeline_interface import PlayerStatsPipelineInterface
from interfaces.players_repository_interface import PlayersRepositoryInterface
from interfaces.nba_player_stats_repository_interface import NBAPlayerStatsRepositoryInterface
from db.models.nba_player_stats import NBAPlayerStats


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



                for stat in player_stats_response.stats:
                    print(f"Processing stats for player ID: {player.id}, season: {stat.season}, game ID: {stat.game_id}")
                    self.nba_player_stats_repository.insert_player_stats(player_stats=NBAPlayerStats(
                        player_id=player.id,
                        first_name=stat.firstname.lower() if stat.firstname else None,
                        last_name=stat.lastname.lower() if stat.lastname else None,
                        team_id=stat.team_id,
                        game_id=stat.game_id,
                        season=stat.season,
                        min=stat.min,
                        points=stat.points,
                        pos=stat.pos.lower() if stat.pos else None,
                        fgm=stat.fgm,
                        fga=stat.fga,
                        fgp=stat.fgp,
                        ftm=stat.ftm,
                        fta=stat.fta,
                        ftp=stat.ftp,
                        tpm=stat.tpm,
                        tpa=stat.tpa,
                        tpp=stat.tpp,
                        offReb=stat.offReb,
                        defReb=stat.defReb,
                        totReb=stat.totReb,
                        assists=stat.assists,
                        pFouls=stat.pFouls,
                        steals=stat.steals,
                        turnovers=stat.turnovers,
                        blocks=stat.blocks,
                        sport_key=sport
                    ))
            
