from abc import ABC, abstractmethod

from db.models.mlb_player_stats import MLBPlayerStats


class MLBPlayerStatsRepositoryInterface(ABC):
    @abstractmethod
    def insert_player_stats(self, player_stats: MLBPlayerStats):
        pass