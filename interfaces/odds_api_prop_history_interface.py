from abc import ABC, abstractmethod
from db.models.odds_api_props_history import OddsAPIPropHistory

class OddsAPIPropsHistoryInterface(ABC):
    @abstractmethod
    def insert_props_history(self, props_history: OddsAPIPropHistory):
        """
        Insert a prop history record into the database.
        Args:
            props_history (OddsAPIPropHistory): Prop history record to insert.
        """
        pass