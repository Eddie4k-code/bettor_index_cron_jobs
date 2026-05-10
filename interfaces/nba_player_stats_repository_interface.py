from abc import ABC, abstractmethod
from db.models.nba_player_stats import NBAPlayerStats


class NBAPlayerStatsRepositoryInterface(ABC):
    @abstractmethod
    def insert_player_stats(self, player_stats: NBAPlayerStats):
        pass