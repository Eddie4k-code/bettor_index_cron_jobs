import logging

from db.models.mlb_player_injuries import MLBPlayerInjuries
from interfaces.mlb_player_injuries_repository_interface import MLBPlayerInjuriesRepositoryInterface


logger = logging.getLogger(__name__)


class MLBPlayerInjuriesRepository(MLBPlayerInjuriesRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_player_injury(self, player_injury: MLBPlayerInjuries):
        self.db.merge(player_injury)

        try:
            self.db.commit()
            logger.info(
                f"Inserted/Updated MLB player injury for player ID: {player_injury.player_id}, "
                f"team ID: {player_injury.team_id}, status: {player_injury.status}"
            )
            return player_injury
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error inserting/updating MLB player injury for player ID: {player_injury.player_id}, "
                f"team ID: {player_injury.team_id}, status: {player_injury.status} - {str(e)}"
            )
            raise e