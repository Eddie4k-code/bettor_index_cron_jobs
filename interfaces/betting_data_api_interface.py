from abc import ABC, abstractmethod
from schemas.OddsAPIResponses import OddsAPIEvent

class BettingDataAPIInterface(ABC):
    @abstractmethod
    def get_events(self, sport: str, hours_ahead: int):
        pass

    @abstractmethod
    def get_props_based_on_events(self, events: list[OddsAPIEvent], markets: str, sport:str):
        pass


