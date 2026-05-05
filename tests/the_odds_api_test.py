from pytest_mock import mocker
from apis.api_config import APIConfig
import pytest

from apis.the_odds_api import TheOddsAPI
from interfaces.betting_data_api_interface import BettingDataAPIInterface
from interfaces.http_client_interface import HTTPClient
import os
from schemas.OddsAPIResponses import OddsAPIEvent, OddsAPIProp
from datetime import datetime, timedelta

@pytest.fixture
def mock_api_config():
    os.environ["DUMMY_API_KEY"] = "test_api_key"  # Set a dummy API key in the environment for testing
    dummy_api_config = APIConfig(api_key_env_var="DUMMY_API_KEY")
    return dummy_api_config
    

@pytest.fixture
def http_client_mock(mocker):
    http_client_mock = mocker.Mock(spec=HTTPClient)
    return http_client_mock


def test_odds_api_get_events(mocker, mock_api_config: APIConfig, http_client_mock: HTTPClient):
    api_config = mock_api_config
    odds_api: BettingDataAPIInterface = TheOddsAPI(api_config=api_config, http_client=http_client_mock)
    http_client_mock.get.return_value.json.return_value = [
        {
            "id": "event1",
            "sport_key": "basketball_nba",
            "sport_title": "NBA Basketball",
            "commence_time": "2024-06-01T00:00:00Z",
            "home_team": "Lakers",
            "away_team": "Warriors"
        },
        {
            "id": "event2",
            "sport_key": "basketball_nba",
            "sport_title": "NBA Basketball",
            "commence_time": "2024-06-01T02:00:00Z",
            "home_team": "Celtics",
            "away_team": "Bulls"
        }
    ]

    events = odds_api.get_events(sport="basketball_nba", hours_ahead=24)

    assert len(events) == 2
    assert events[0].id == "event1"
    assert events[0].home_team == "Lakers"
    assert events[0].away_team == "Warriors"
    assert events[1].id == "event2"
    assert events[1].home_team == "Celtics"
    assert events[1].away_team == "Bulls"
    assert isinstance(events, list)
    assert all(isinstance(event, OddsAPIEvent) for event in events)


def test_odds_api_get_events_empty_response(mocker, mock_api_config: APIConfig, http_client_mock: HTTPClient):
    api_config = mock_api_config
    odds_api: BettingDataAPIInterface = TheOddsAPI(api_config=api_config, http_client=http_client_mock)
    http_client_mock.get.return_value.json.return_value = []

    events = odds_api.get_events(sport="basketball_nba", hours_ahead=24)

    assert isinstance(events, list)
    assert len(events) == 0


def test_odds_api_get_events_invalid_response(mocker, mock_api_config: APIConfig, http_client_mock: HTTPClient):
    api_config = mock_api_config
    odds_api: BettingDataAPIInterface = TheOddsAPI(api_config=api_config, http_client=http_client_mock)
    http_client_mock.get.return_value.json.return_value = {"unexpected": "data"}

    with pytest.raises(TypeError):
        odds_api.get_events(sport="basketball_nba", hours_ahead=24)



def test_odds_api_get_props_based_on_events_parses_full_prop_response(mock_api_config: APIConfig, http_client_mock: HTTPClient):
    from schemas.OddsAPIResponses import OddsAPIProp
    api_config = mock_api_config
    odds_api: BettingDataAPIInterface = TheOddsAPI(api_config=api_config, http_client=http_client_mock)
    events = [
        OddsAPIEvent(
            id="event1",
            sport_key="basketball_nba",
            sport_title="NBA Basketball",
            commence_time="2024-06-01T00:00:00Z",
            home_team="Lakers",
            away_team="Warriors"
        )
    ]

    # Sample full OddsAPIProp response
    sample_prop_response = {
        "id": "event1",
        "sport_key": "basketball_nba",
        "sport_title": "NBA Basketball",
        "commence_time": "2024-06-01T00:00:00Z",
        "home_team": "Lakers",
        "away_team": "Warriors",
        "bookmakers": [
            {
                "key": "draftkings",
                "title": "DraftKings",
                "markets": [
                    {
                        "key": "player_points",
                        "last_update": "2024-06-01T00:00:00Z",
                        "outcomes": [
                            {"name": "Over", "description": "LeBron James", "price": -110, "point": 27.5},
                            {"name": "Under", "description": "LeBron James", "price": -110, "point": 27.5}
                        ]
                    }
                ]
            }
        ]
    }
    http_client_mock.get.return_value.json.return_value = sample_prop_response

    props = odds_api.get_props_based_on_events(sport="basketball_nba", events=events, markets="player_points")
    # If your method returns a list of dicts, parse to OddsAPIProp here for the test
    # parsed = [OddsAPIProp(**prop) if not isinstance(prop, OddsAPIProp) else prop for prop in props]
    assert len(props) == 1
    assert props[0].id == "event1"
    assert props[0].bookmakers[0].key == "draftkings"
    assert props[0].bookmakers[0].markets[0].key == "player_points"
    assert props[0].bookmakers[0].markets[0].outcomes[0].name == "Over"
    assert props[0].bookmakers[0].markets[0].outcomes[0].description == "LeBron James"
    assert props[0].bookmakers[0].markets[0].outcomes[0].price == -110
    assert props[0].bookmakers[0].markets[0].outcomes[0].point == 27.5