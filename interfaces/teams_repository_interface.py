from abc import ABC, abstractmethod
from db.models.team import Team

class TeamsRepositoryInterface(ABC):
    @abstractmethod
    def insert_team(self, team: Team):
        return NotImplementedError("This method should be implemented by subclasses")

