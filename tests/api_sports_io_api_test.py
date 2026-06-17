import pytest
import os
from clients.httpx_client import HTTPXClient
from apis.api_sports_io_api import SportsIOAPI
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from interfaces.sports_stats_api_interface import SportsStatsAPIInterface
from schemas.sports_stats_api_responses import SportsStatsAPIGamesResponse, SportsStatsApiTeamResponse, TeamSchema, SportsStatsAPIPlayersResponse, PlayersSchema

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
        "response": [
            {"id": 1, "name": "Team A", "nickname": "A", "code": "TA", "city": "CityA"},
            {"id": 2, "name": "Team B", "nickname": "B", "code": "TB", "city": "CityB"}
        ]
    }

    teams_response = api.get_teams(sport="basketball_nba")

    assert isinstance(teams_response, SportsStatsApiTeamResponse)
    assert hasattr(teams_response, "teams")
    assert isinstance(teams_response.teams, list)
    assert len(teams_response.teams) == 2
    assert teams_response.teams[0].name == "Team A"
    assert teams_response.teams[1].name == "Team B"


def test_sports_io_api_get_games_200(http_client_mock: HTTPClient, mock_api_config: APIConfig):
    api = SportsIOAPI(api_config=mock_api_config, http_client=http_client_mock)
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "response": [
            {
                "id": 1,
                "season": 2023,
                "date": {"start": "2023-10-01T00:00:00.000Z"},
                "status": {"long": "Finished"},
                "teams": {
                    "home": {"id": 1, "name": "Team A"},
                    "visitors": {"id": 2, "name": "Team B"}
                },
                "scores": {
                    "home": {"points": 100},
                    "visitors": {"points": 90}
                }
            },
            {
                "id": 2,
                "season": 2023,
                "date": {"start": "2023-10-02T00:00:00.000Z"},
                "status": {"long": "Finished"},
                "teams": {
                    "home": {"id": 2, "name": "Team B"},
                    "visitors": {"id": 1, "name": "Team A"}
                },
                "scores": {
                    "home": {"points": 95},
                    "visitors": {"points": 98}
                }
            }
        ]
    }

    games_response = api.get_games(sport="basketball_nba", season=2023, team_id=1)

    assert isinstance(games_response, SportsStatsAPIGamesResponse)
    assert hasattr(games_response, "games")
    assert isinstance(games_response.games, list)
    assert len(games_response.games) == 2   
    assert games_response.games[0].home_team == "Team A"
    assert games_response.games[0].away_team == "Team B"


def test_sports_io_api_get_players_200(http_client_mock: HTTPClient, mock_api_config: APIConfig):
    api = SportsIOAPI(api_config=mock_api_config, http_client=http_client_mock)
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "response": [
            {
                "id": 382,
                "firstname": "Dejounte",
                "lastname": "Murray",
                "birth": {"date": "1996-09-19", "country": "USA"},
                "nba": {"start": 2016, "pro": 4},
                "height": {"feets": "6", "inches": "4", "meters": "1.93"},
                "weight": {"pounds": "180", "kilograms": "81.6"},
                "college": "Washington",
                "affiliation": "Washington/USA",
                "leagues": {"standard": {"jersey": 5, "active": True, "pos": "G"}}
            }
        ]
    }

    players_response = api.get_players(team_id=1, season=2023)

    assert isinstance(players_response, SportsStatsAPIPlayersResponse)
    assert hasattr(players_response, "players")
    assert isinstance(players_response.players, list)
    assert len(players_response.players) == 1
    player = players_response.players[0]
    assert player.id == 382
    assert player.firstname == "Dejounte"
    assert player.lastname == "Murray"


def test_sports_io_api_get_injuries_raises_not_implemented(http_client_mock: HTTPClient, mock_api_config: APIConfig):
    api = SportsIOAPI(api_config=mock_api_config, http_client=http_client_mock)

    with pytest.raises(NotImplementedError, match="Injuries are not supported for SportsIO/NBA API."):
        api.get_injuries(team_ids=[1])






