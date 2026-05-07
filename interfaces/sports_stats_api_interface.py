from abc import abstractmethod, ABC
from typing import Optional

class SportsStatsAPIInterface(ABC):
    @abstractmethod
    def get_teams(self, sport: str, season: Optional[int] = None) -> dict:
        pass