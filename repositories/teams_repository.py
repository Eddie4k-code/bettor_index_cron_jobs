import logging

from interfaces.teams_repository_interface import TeamsRepositoryInterface
from db.models.team import Team

logger = logging.getLogger(__name__)

class TeamsRepository(TeamsRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_team(self, team: Team):
        """
        Inserts a Team record into the database.
        Args:
            team (Team): The Team object to insert.
        """
        self.db.merge(team)  # Use merge to handle both insert and update scenarios

        try:
            self.db.commit()
            logger.info(f"Inserted/Updated team: {team.name} (ID: {team.id})")
        except Exception as e:
            logger.error(f"Error inserting/updating team: {team.name} (ID: {team.id}) - {str(e)}")
            self.db.rollback()
            raise e
        
    def get_teams(self, sport: str):
        """
        Fetch all teams for a given sport.
        Args:
            sport (str): The sport key to filter teams by.
        Returns:
            list[Team]: List of Team objects for the sport.
        """
        from db.models.team import Team
        try:
            return self.db.query(Team).filter_by(sport_key=sport).all()
        except Exception as e:
            logger.error(f"Error fetching teams for sport: {sport} - {str(e)}")
            raise e