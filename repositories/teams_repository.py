from interfaces.teams_repository_interface import TeamsRepositoryInterface
from db.models.team import Team

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
        except Exception as e:
            self.db.rollback()
            raise e