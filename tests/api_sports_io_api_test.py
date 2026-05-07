
import pytest
import os
from clients.httpx_client import HTTPXClient
from apis.api_sports_io_api import SportsIOAPI
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from schemas.sports_stats_api_responses import SportsStatsApiTeamResponse, TeamSchema

@pytest.fixture
def mock_api_config():
    os.environ["DUMMY_API_KEY"] = "test_api_key"  # Set a dummy API key in the environment for testing
    dummy_api_config = APIConfig(api_key_env_var="DUMMY_API_KEY")
    return dummy_api_config
    

@pytest.fixture
def http_client_mock(mocker):
    http_client_mock = mocker.Mock(spec=HTTPClient)
    return http_client_mock


def test_sports_io_api_get_teams_200(http_client_mock: HTTPClient, mock_api_config: APIConfig):
    api = SportsIOAPI(api_config=mock_api_config, http_client=http_client_mock)
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "teams": [
            {"id": 1, "name": "Team A", "nickname": "A", "code": "TA", "city": "CityA"},
            {"id": 2, "name": "Team B", "nickname": "B", "code": "TB", "city": "CityB"}
        ]
    }

    teams_response = api.get_teams(sport="basketball_nba", season=2023)

    assert hasattr(teams_response, "teams")
    assert isinstance(teams_response.teams, list)
    assert len(teams_response.teams) == 2
    assert teams_response.teams[0].name == "Team A"
    assert teams_response.teams[1].name == "Team B"






