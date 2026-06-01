import logging

from db.models.mlb_player_stats import MLBPlayerStats
from interfaces.mlb_player_stats_repository_interface import MLBPlayerStatsRepositoryInterface


logger = logging.getLogger(__name__)


class MLBPlayerStatsRepository(MLBPlayerStatsRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_player_stats(self, player_stats: MLBPlayerStats):
        self.db.merge(player_stats)

        try:
            self.db.commit()
            logger.info(
                f"Inserted/Updated MLB player stats for player ID: {player_stats.player_id}, "
                f"season: {player_stats.season}, game ID: {player_stats.game_id}"
            )
            return player_stats
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error inserting/updating MLB player stats for player ID: {player_stats.player_id}, "
                f"season: {player_stats.season}, game ID: {player_stats.game_id} - {str(e)}"
            )
            raise e