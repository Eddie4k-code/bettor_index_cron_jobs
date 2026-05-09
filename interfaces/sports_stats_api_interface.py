from abc import abstractmethod, ABC
from typing import Optional

class SportsStatsAPIInterface(ABC):
    @abstractmethod
    def get_teams(self, sport: str) -> dict:
        pass