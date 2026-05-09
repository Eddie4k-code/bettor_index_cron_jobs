from abc import ABC, abstractmethod
from db.models.team import Team

class TeamsRepositoryInterface(ABC):
    @abstractmethod
    def insert_team(self, team: Team):
        return NotImplementedError("This method should be implemented by subclasses")

    @abstractmethod
    def get_teams(self, sport: str):
        """
        Fetch all teams for a given sport.
        Args:
            sport (str): The sport key to filter teams by.
        Returns:
            list[Team]: List of Team objects for the sport.
        """
        return NotImplementedError("This method should be implemented by subclasses")

