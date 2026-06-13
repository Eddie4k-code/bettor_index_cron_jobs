import pytest
import os
from apis.ball_dont_lie_mlb_api import BallDontLieMlbAPI
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import (
    BallDontLieMLBTeamResponse,
    BallDontLieMLBGamesResponse,
    BallDontLieMLBPlayerStatsResponse,
    SportsStatsAPIPlayersResponse,
)


@pytest.fixture
def mock_api_config():
    os.environ["DUMMY_API_KEY"] = "test_api_key"
    return APIConfig(api_key_env_var="DUMMY_API_KEY")


@pytest.fixture
def http_client_mock(mocker):
    return mocker.Mock(spec=HTTPClient)


@pytest.fixture
def api(mock_api_config, http_client_mock):
    return BallDontLieMlbAPI(api_config=mock_api_config, http_client=http_client_mock)


def test_get_teams_200(api: BallDontLieMlbAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "id": 1,
                "abbreviation": "NYY",
                "display_name": "New York Yankees",
                "name": "Yankees",
                "location": "New York",
                "league": "AL",
                "division": "AL East",
            },
            {
                "id": 2,
                "abbreviation": "BOS",
                "display_name": "Boston Red Sox",
                "name": "Red Sox",
                "location": "Boston",
                "league": "AL",
                "division": "AL East",
            },
        ]
    }

    result = api.get_teams(sport="mlb")

    assert isinstance(result, BallDontLieMLBTeamResponse)
    assert len(result.teams) == 2
    assert result.teams[0].abbreviation == "NYY"
    assert result.teams[0].display_name == "New York Yankees"
    assert result.teams[1].abbreviation == "BOS"


def test_get_games_200(api: BallDontLieMlbAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "id": 101,
                "season": 2024,
                "date": "2024-04-01",
                "status": "Final",
                "home_team": {"id": 1, "name": "Yankees"},
                "away_team": {"id": 2, "name": "Red Sox"},
                "home_team_data": {"runs": 5},
                "away_team_data": {"runs": 3},
            }
        ]
    }

    result = api.get_games(sport="mlb", season=2024, team_id=1)

    assert isinstance(result, BallDontLieMLBGamesResponse)
    assert len(result.games) == 1
    game = result.games[0]
    assert game.id == 101
    assert game.season == 2024
    assert game.home_team_name == "Yankees"
    assert game.away_team_name == "Red Sox"
    assert game.home_runs == 5
    assert game.away_runs == 3


def test_get_players_200(api: BallDontLieMlbAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {"id": 501, "first_name": "Aaron", "last_name": "Judge"},
            {"id": 502, "first_name": "Giancarlo", "last_name": "Stanton"},
        ]
    }

    result = api.get_players(team_id=1, season=2024)

    assert isinstance(result, SportsStatsAPIPlayersResponse)
    assert len(result.players) == 2
    assert result.players[0].id == 501
    assert result.players[0].firstname == "Aaron"
    assert result.players[0].lastname == "Judge"


def test_get_player_stats_200(api: BallDontLieMlbAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 501,
                    "first_name": "Aaron",
                    "last_name": "Judge",
                    "team": {"name": "Yankees"},
                },
                "game_id": 101,
                "at_bats": 4,
                "hits": 2,
                "hr": 1,
                "rbi": 2,
                "bb": 1,
                "k": 1,
                "avg": 0.300,
                "obp": 0.380,
                "slg": 0.600,
                "doubles": 0,
                "triples": 0,
                "stolen_bases": 0,
                "plate_appearances": 5,
                "total_bases": 5,
            }
        ]
    }

    result = api.get_player_stats(player_id=501, season=2024, sport="mlb")

    assert isinstance(result, BallDontLieMLBPlayerStatsResponse)
    assert len(result.stats) == 1
    stat = result.stats[0]
    assert stat.player_id == 501
    assert stat.firstname == "Aaron"
    assert stat.lastname == "Judge"
    assert stat.team_name == "Yankees"
    assert stat.game_id == 101
    assert stat.season == 2024
    assert stat.hr == 1
    assert stat.avg == 0.300


def test_get_player_stats_accepts_mixed_type_pitching_fields(api: BallDontLieMlbAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 701,
                    "first_name": "Gerrit",
                    "last_name": "Cole",
                    "team": {"name": "Yankees"},
                },
                "game_id": 401,
                "ip": 6,
                "p_k": 8,
                "era": 0,
            }
        ]
    }

    result = api.get_player_stats(player_id=701, season=2024, sport="mlb")

    assert isinstance(result, BallDontLieMLBPlayerStatsResponse)
    assert len(result.stats) == 1
    stat = result.stats[0]
    assert stat.game_id == 401
    assert stat.season == 2024
    assert stat.ip == 6
    assert stat.era == 0


def test_get_games_paginates_until_next_cursor_is_null(api: BallDontLieMlbAPI, http_client_mock, mocker):
    page_1_response = mocker.Mock()
    page_1_response.status_code = 200
    page_1_response.json.return_value = {
        "data": [
            {
                "id": 201,
                "season": 2024,
                "date": "2024-04-10",
                "status": "Final",
                "home_team": {"id": 1, "name": "Yankees"},
                "away_team": {"id": 2, "name": "Red Sox"},
                "home_team_data": {"runs": 6},
                "away_team_data": {"runs": 4},
            }
        ],
        "meta": {"next_cursor": 300, "per_page": 100, "prev_cursor": None},
    }

    page_2_response = mocker.Mock()
    page_2_response.status_code = 200
    page_2_response.json.return_value = {
        "data": [
            {
                "id": 202,
                "season": 2024,
                "date": "2024-04-11",
                "status": "Final",
                "home_team": {"id": 2, "name": "Red Sox"},
                "away_team": {"id": 1, "name": "Yankees"},
                "home_team_data": {"runs": 2},
                "away_team_data": {"runs": 3},
            }
        ],
        "meta": {"next_cursor": None, "per_page": 100, "prev_cursor": 300},
    }

    http_client_mock.get.side_effect = [page_1_response, page_2_response]

    result = api.get_games(sport="mlb", season=2024, team_id=1)

    assert isinstance(result, BallDontLieMLBGamesResponse)
    assert len(result.games) == 2
    assert result.games[0].id == 201
    assert result.games[1].id == 202
    assert http_client_mock.get.call_count == 2
    assert http_client_mock.get.call_args_list[0].kwargs["params"] == {
        "team_ids[]": 1,
        "seasons[]": 2024,
        "per_page": 100,
    }
    assert http_client_mock.get.call_args_list[1].kwargs["params"] == {
        "team_ids[]": 1,
        "seasons[]": 2024,
        "per_page": 100,
        "cursor": 300,
    }


def test_get_players_paginates_until_next_cursor_is_null(api: BallDontLieMlbAPI, http_client_mock, mocker):
    page_1_response = mocker.Mock()
    page_1_response.status_code = 200
    page_1_response.json.return_value = {
        "data": [
            {"id": 601, "first_name": "Juan", "last_name": "Soto"}
        ],
        "meta": {"next_cursor": 900, "per_page": 100, "prev_cursor": None},
    }

    page_2_response = mocker.Mock()
    page_2_response.status_code = 200
    page_2_response.json.return_value = {
        "data": [
            {"id": 602, "first_name": "Anthony", "last_name": "Volpe"}
        ],
        "meta": {"next_cursor": None, "per_page": 100, "prev_cursor": 900},
    }

    http_client_mock.get.side_effect = [page_1_response, page_2_response]

    result = api.get_players(team_id=1, season=2024)

    assert isinstance(result, SportsStatsAPIPlayersResponse)
    assert len(result.players) == 2
    assert result.players[0].id == 601
    assert result.players[1].id == 602
    assert http_client_mock.get.call_count == 2
    assert http_client_mock.get.call_args_list[0].kwargs["params"] == {
        "team_ids[]": 1,
        "per_page": 100,
    }
    assert http_client_mock.get.call_args_list[1].kwargs["params"] == {
        "team_ids[]": 1,
        "per_page": 100,
        "cursor": 900,
    }


def test_get_player_stats_paginates_until_next_cursor_is_null(api: BallDontLieMlbAPI, http_client_mock, mocker):
    page_1_response = mocker.Mock()
    page_1_response.status_code = 200
    page_1_response.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 701,
                    "first_name": "Gerrit",
                    "last_name": "Cole",
                    "team": {"name": "Yankees"},
                },
                "game_id": 401,
                "ip": "6.0",
                "p_k": 8,
                "era": "2.80",
            }
        ],
        "meta": {"next_cursor": 1200, "per_page": 100, "prev_cursor": None},
    }

    page_2_response = mocker.Mock()
    page_2_response.status_code = 200
    page_2_response.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 701,
                    "first_name": "Gerrit",
                    "last_name": "Cole",
                    "team": {"name": "Yankees"},
                },
                "game_id": 402,
                "ip": "7.0",
                "p_k": 10,
                "era": "2.70",
            }
        ],
        "meta": {"next_cursor": None, "per_page": 100, "prev_cursor": 1200},
    }

    http_client_mock.get.side_effect = [page_1_response, page_2_response]

    result = api.get_player_stats(player_id=701, season=2024, sport="mlb")

    assert isinstance(result, BallDontLieMLBPlayerStatsResponse)
    assert len(result.stats) == 2
    assert result.stats[0].game_id == 401
    assert result.stats[1].game_id == 402
    assert http_client_mock.get.call_count == 2
    assert http_client_mock.get.call_args_list[0].kwargs["params"] == {
        "player_ids[]": 701,
        "seasons[]": 2024,
        "per_page": 100,
    }
    assert http_client_mock.get.call_args_list[1].kwargs["params"] == {
        "player_ids[]": 701,
        "seasons[]": 2024,
        "per_page": 100,
        "cursor": 1200,
    }
