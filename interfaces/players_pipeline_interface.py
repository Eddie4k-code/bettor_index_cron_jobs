from abc import ABC, abstractmethod

class PlayersPipelineInterface(ABC):
    @abstractmethod
    def get_players(self, sport: str, season: int):
        """
        Fetch and insert players for all teams in a sport and season.
        Args:
            sport (str): The sport key.
            season (int): The season year.
        """
        pass
