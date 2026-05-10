import logging

from interfaces.nba_player_stats_repository_interface import NBAPlayerStatsRepositoryInterface
from db.models.nba_player_stats import NBAPlayerStats


logger = logging.getLogger(__name__)

class NBAPlayerStatsRepository(NBAPlayerStatsRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_player_stats(self, player_stats: NBAPlayerStats):
        self.db.merge(player_stats)

        try:
            self.db.commit()
            logger.info(f"Inserted/Updated player stats for player ID: {player_stats.player_id}, season: {player_stats.season}, game ID: {player_stats.game_id}")
            return player_stats
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error inserting/updating player stats for player ID: {player_stats.player_id}, season: {player_stats.season}, game ID: {player_stats.game_id} - {str(e)}")
            raise e