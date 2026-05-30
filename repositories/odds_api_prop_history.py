from db.models.odds_api_props_history import OddsAPIPropHistory
from interfaces.odds_api_prop_history_interface import OddsAPIPropsHistoryInterface
import logging

logger = logging.getLogger(__name__)

class OddsAPIPropsHistoryRepository(OddsAPIPropsHistoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_props_history(self, props_history):
        self.db.add(props_history)
        try:
            logger.info(f"Inserting prop history for event_id: {props_history.event_id}, bookmaker: {props_history.bookmaker}, market: {props_history.market_key}, outcome: {props_history.outcome_name}, change_type: {props_history.change_type}, old_price: {props_history.old_price}, new_price: {props_history.new_price}")
            self.db.commit()
        except Exception as e:
            logger.error(f"Error inserting prop history: {str(e)}")
            self.db.rollback()
            raise e