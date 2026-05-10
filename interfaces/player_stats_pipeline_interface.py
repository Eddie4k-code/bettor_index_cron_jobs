from abc import ABC, abstractmethod

class PlayerStatsPipelineInterface(ABC):
    @abstractmethod
    def get_player_stats(self, sport: str, season:int):
        pass