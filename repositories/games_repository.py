from interfaces.games_repository_interface import GamesRepositoryInterface
import logging


logger = logging.getLogger(__name__)

class GamesRepository(GamesRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_games(self, game):
        self.db.merge(game)  # Use merge to handle both insert and update scenarios

        try:
            self.db.commit()
            logger.info(f"Inserted/Updated game: {game.id}")
        except Exception as e:
            logger.error(f"Error inserting/updating game: {game.id} - {str(e)}")
            self.db.rollback()
            raise e