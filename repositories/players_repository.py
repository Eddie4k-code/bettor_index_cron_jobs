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
        
    def get_players(self, sport: str):
        try:
            return self.db.query(Player).filter_by(sport_key=sport).all()
        except Exception as e:
            logger.error(f"Error fetching players for sport: {sport} - {str(e)}")
            raise e
        
    def get_player_by_name(self, first_name: str, last_name: str, sport: str):
        try:
            return self.db.query(Player).filter_by(first_name=first_name, last_name=last_name, sport_key=sport).all()
        except Exception as e:
            logger.error(f"Error fetching player by name: {first_name} {last_name} for sport: {sport} - {str(e)}")
            raise e
