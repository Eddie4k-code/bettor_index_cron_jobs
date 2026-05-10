from abc import ABC, abstractmethod
from db.models.PlayerStatsProcessing import PlayerStatsProcessing

class PlayerStatsProcessingRepositoryInterface(ABC):
    @abstractmethod
    def insert_player_stats_processing(self, player_stats_processing: PlayerStatsProcessing):
        """
        Insert a record into the player_stats_processing table to track processing status.
        Args:
            player_stats_processing (PlayerStatsProcessing): The record to insert.
        """
        pass