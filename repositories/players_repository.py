from interfaces.players_repository_interface import PlayersRepositoryInterface
from db.models.player import Player
import logging

logger = logging.getLogger(__name__)

class PlayersRepository(PlayersRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_player(self, player: Player):
        self.db.merge(player)
        try:
            self.db.commit()
            logger.info(f"Inserted/Updated player: {player.first_name} {player.last_name} (ID: {player.id})")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error inserting/updating player: {player.id} - {str(e)}")
            raise e
