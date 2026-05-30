from db.models.games import Game
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
        
    def get_game(self, game_id: int, sport_key: str):
        try:
            game = self.db.query(Game).filter_by(id=game_id, sport_key=sport_key).first()
            if game:
                logger.info(f"Retrieved game: {game_id} for sport: {sport_key}")
            else:
                logger.info(f"No game found with ID: {game_id} for sport: {sport_key}")
            return game
        except Exception as e:
            logger.error(f"Error retrieving game: {game_id} for sport: {sport_key} - {str(e)}")
            raise e