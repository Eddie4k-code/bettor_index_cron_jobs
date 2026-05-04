from interfaces.props_pipeline_interface import PropsPipelineInterface
from repositories.props_repository import PropsRepository
import logging
from interfaces.betting_data_api_interface import BettingDataAPIInterface

logger = logging.getLogger(__name__)

class PropsPipeline(PropsPipelineInterface):
    """
    Pipeline for fetching player props for a specific date from the balldontlie API
    and storing them in the database.
    """
    def __init__(self, db: PropsRepository, api: BettingDataAPIInterface):
        self.db = db
        self.api = api

    def get_props(self, hours_ahead: int, sport: str, markets: str):
        """
        Fetch props for the given date from the Betting Data API and store them in the database.
        Args:
            hours_ahead (int): The number of hours ahead to look for events.
            sport (str): The sport key (e.g., 'basketball_nba').
            markets (str): The market key (e.g., 'player_points').
        """

        logger.info(f"Fetching events for sport: {sport} with cutoff time of {hours_ahead} hours ahead.")
        events = self.api.get_events(sport=sport, hours_ahead=hours_ahead)
        logger.info(f"Fetched {len(events)} events. Fetching props for these events.")
        props = self.api.get_props_based_on_events(sport=sport, events=events, markets=markets)
        logger.info(f"Fetched props for {len(props)} events. Storing in database.")
        self.db.save_props(props)
        logger.info("Props stored in database successfully.")



       
