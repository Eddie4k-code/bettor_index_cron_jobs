from interfaces.betting_data_api_interface import BettingDataAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from datetime import datetime, timedelta
from schemas.OddsAPIResponses import OddsAPIEvent, OddsAPIProp

class TheOddsAPI(BettingDataAPIInterface):
    def __init__(self, api_config: APIConfig, http_client: HTTPClient):
        self.api_key = api_config.get_api_key()
        self.http_client = http_client

    def get_events(self, sport: str, hours_ahead: int) -> list[OddsAPIEvent]:
        """
        Fetch upcoming events for a given sport up to a specified cutoff time from The Odds API.
        Args:
            sport (str): The sport for which to fetch events (e.g., 'basketball_nba').
            hours_ahead (int): The number of hours ahead to look for events.
        Returns:
            list[OddsAPIEvent]: A list of events with their details.
        """

        commence_time_to = (datetime.utcnow() + timedelta(hours=hours_ahead)).replace(microsecond=0).isoformat() + 'Z'

        url = f"https://api.the-odds-api.com/v4/sports/{sport}/events"

        params = {"apiKey": self.api_key, "commenceTimeTo": commence_time_to}


        response = self.http_client.get(url, params=params)

        return [OddsAPIEvent(**event) for event in response.json()]
    

    def get_props_based_on_events(self, sport: str, events: list[OddsAPIEvent], markets:str, regions: str = "us") -> list[OddsAPIProp]:
        """
        For each event in the provided list, fetch prop (market) data using the Odds API event odds endpoint.
        Args:
            sport (str): The sport key (e.g., 'basketball_nba').
            events (list[OddsAPIEvent]): List of event objects for which to fetch props.
            markets (str): The market key (e.g., 'player_points').
        Returns:
            list[OddsAPIProp]: List of event prop data responses (one per event).
        """
        results = []
        for event in events:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/events/{event.id}/odds"
            params = {"apiKey": self.api_key, "markets": markets, "regions": regions, "oddsFormat": "american"}
            response = self.http_client.get(url, params=params)
            results.append(OddsAPIProp(**response.json()))
        return results