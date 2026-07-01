import os

import pytest

from apis.api_config import APIConfig
from apis.ball_dont_lie_nfl_api import BallDontLieNflAPI
from interfaces.http_client_interface import HTTPClient
from schemas.sports_stats_api_responses import (
    BallDontLieNFLGamesResponse,
    BallDontLieNFLInjuriesResponse,
    BallDontLieNFLPlayerStatsResponse,
    BallDontLieNFLTeamResponse,
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
    return BallDontLieNflAPI(api_config=mock_api_config, http_client=http_client_mock)


def _nfl_team(team_id: int, abbreviation: str, full_name: str, name: str):
    return {
        "id": team_id,
        "abbreviation": abbreviation,
        "full_name": full_name,
        "name": name,
        "location": full_name.rsplit(" ", 1)[0],
        "conference": "AFC",
        "division": "WEST",
    }


def test_get_teams_200(api: BallDontLieNflAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
            _nfl_team(2, "BUF", "Buffalo Bills", "Bills"),
        ]
    }

    result = api.get_teams(sport="football_nfl")

    assert isinstance(result, BallDontLieNFLTeamResponse)
    assert len(result.teams) == 2
    assert result.teams[0].abbreviation == "KC"
    assert result.teams[0].full_name == "Kansas City Chiefs"
    assert result.teams[0].name == "Chiefs"
    assert result.teams[1].abbreviation == "BUF"
    http_client_mock.get.assert_called_once_with(
        "https://api.balldontlie.io/nfl/v1/teams",
        headers={"Authorization": "test_api_key"},
    )


def test_get_games_200(api: BallDontLieNflAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "id": 101,
                "season": 2024,
                "week": 1,
                "date": "2024-09-05T20:20:00.000Z",
                "status": "Final",
                "postseason": False,
                "home_team": _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
                "visitor_team": _nfl_team(2, "BAL", "Baltimore Ravens", "Ravens"),
                "home_team_score": 27,
                "visitor_team_score": 20,
            }
        ]
    }

    result = api.get_games(sport="football_nfl", season=2024, team_id=1)

    assert isinstance(result, BallDontLieNFLGamesResponse)
    assert len(result.games) == 1
    game = result.games[0]
    assert game.id == 101
    assert game.season == 2024
    assert game.week == 1
    assert game.home_team_name == "Kansas City Chiefs"
    assert game.away_team_name == "Baltimore Ravens"
    assert game.home_team_score == 27
    assert game.away_team_score == 20


def test_get_players_200(api: BallDontLieNflAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {"id": 501, "first_name": "Patrick", "last_name": "Mahomes"},
            {"id": 502, "first_name": "Travis", "last_name": "Kelce"},
        ]
    }

    result = api.get_players(team_id=1, season=2024)

    assert isinstance(result, SportsStatsAPIPlayersResponse)
    assert len(result.players) == 2
    assert result.players[0].id == 501
    assert result.players[0].firstname == "Patrick"
    assert result.players[0].lastname == "Mahomes"


def test_get_player_stats_200(api: BallDontLieNflAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 501,
                    "first_name": "Patrick",
                    "last_name": "Mahomes",
                    "team": _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
                },
                "game": {"id": 101, "season": 2024},
                "passing_completions": 28,
                "passing_attempts": 39,
                "passing_yards": 291,
                "passing_touchdowns": 1,
                "passing_interceptions": 1,
                "rushing_attempts": 3,
                "rushing_yards": 14,
            }
        ]
    }

    result = api.get_player_stats(player_id=501, season=2024, sport="football_nfl")

    assert isinstance(result, BallDontLieNFLPlayerStatsResponse)
    assert len(result.stats) == 1
    stat = result.stats[0]
    assert stat.player_id == 501
    assert stat.firstname == "Patrick"
    assert stat.lastname == "Mahomes"
    assert stat.team_name == "Kansas City Chiefs"
    assert stat.game_id == 101
    assert stat.season == 2024
    assert stat.passing_yards == 291
    assert stat.rushing_yards == 14


def test_get_player_stats_accepts_mixed_type_numeric_fields(api: BallDontLieNflAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 701,
                    "first_name": "Josh",
                    "last_name": "Allen",
                    "team": _nfl_team(2, "BUF", "Buffalo Bills", "Bills"),
                },
                "game": {"id": 401, "season": 2024},
                "yards_per_pass_attempt": 7.5,
                "qbr": 85,
                "qb_rating": "101.2",
            }
        ]
    }

    result = api.get_player_stats(player_id=701, season=2024, sport="football_nfl")

    assert isinstance(result, BallDontLieNFLPlayerStatsResponse)
    assert len(result.stats) == 1
    stat = result.stats[0]
    assert stat.game_id == 401
    assert stat.season == 2024
    assert stat.yards_per_pass_attempt == 7.5
    assert stat.qbr == 85
    assert stat.qb_rating == "101.2"


def test_get_injuries_200(api: BallDontLieNflAPI, http_client_mock):
    http_client_mock.get.return_value.status_code = 200
    http_client_mock.get.return_value.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 208,
                    "first_name": "Isiah",
                    "last_name": "Pacheco",
                    "position": "Running Back",
                    "position_abbreviation": "RB",
                    "jersey_number": "10",
                    "team": _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
                },
                "status": "Out",
                "comment": "Leg injury",
                "date": "2024-11-05T23:32:00.000Z",
            }
        ]
    }

    result = api.get_injuries(team_ids=[1])

    assert isinstance(result, BallDontLieNFLInjuriesResponse)
    assert len(result.injuries) == 1
    injury = result.injuries[0]
    assert injury.player.id == 208
    assert injury.player.first_name == "Isiah"
    assert injury.player.last_name == "Pacheco"
    assert injury.player.team.id == 1
    assert injury.player.team.abbreviation == "KC"
    assert injury.status == "Out"
    assert injury.comment == "Leg injury"
    assert injury.date == "2024-11-05T23:32:00.000Z"


def test_get_injuries_paginates_until_next_cursor_is_null(api: BallDontLieNflAPI, http_client_mock, mocker):
    page_1_response = mocker.Mock()
    page_1_response.status_code = 200
    page_1_response.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 6309,
                    "first_name": "Player",
                    "last_name": "One",
                    "position": "WR",
                    "position_abbreviation": "WR",
                    "jersey_number": "11",
                    "team": _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
                },
                "status": "Questionable",
                "comment": "Page 1 injury.",
                "date": "2026-06-03T17:31:00.000Z",
            }
        ],
        "meta": {"next_cursor": 62089, "per_page": 100},
    }

    page_2_response = mocker.Mock()
    page_2_response.status_code = 200
    page_2_response.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 1101,
                    "first_name": "Player",
                    "last_name": "Two",
                    "position": "QB",
                    "position_abbreviation": "QB",
                    "jersey_number": "15",
                    "team": _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
                },
                "status": "Out",
                "comment": "Page 2 injury.",
                "date": "2026-05-28T14:25:00.000Z",
            }
        ],
        "meta": {"per_page": 100},
    }

    http_client_mock.get.side_effect = [page_1_response, page_2_response]

    result = api.get_injuries(team_ids=[1])

    assert isinstance(result, BallDontLieNFLInjuriesResponse)
    assert len(result.injuries) == 2
    assert result.injuries[0].player.id == 6309
    assert result.injuries[1].player.id == 1101
    assert result.injuries[0].status == "Questionable"
    assert result.injuries[1].status == "Out"
    assert http_client_mock.get.call_count == 2
    assert http_client_mock.get.call_args_list[0].kwargs["params"] == {
        "team_ids[]": [1],
        "per_page": 100,
    }
    assert http_client_mock.get.call_args_list[1].kwargs["params"] == {
        "team_ids[]": [1],
        "per_page": 100,
        "cursor": 62089,
    }


def test_get_games_paginates_until_next_cursor_is_null(api: BallDontLieNflAPI, http_client_mock, mocker):
    page_1_response = mocker.Mock()
    page_1_response.status_code = 200
    page_1_response.json.return_value = {
        "data": [
            {
                "id": 201,
                "season": 2024,
                "week": 1,
                "date": "2024-09-08T17:00:00.000Z",
                "status": "Final",
                "postseason": False,
                "home_team": _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
                "visitor_team": _nfl_team(2, "BUF", "Buffalo Bills", "Bills"),
                "home_team_score": 24,
                "visitor_team_score": 21,
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
                "week": 2,
                "date": "2024-09-15T17:00:00.000Z",
                "status": "Final",
                "postseason": False,
                "home_team": _nfl_team(2, "BUF", "Buffalo Bills", "Bills"),
                "visitor_team": _nfl_team(1, "KC", "Kansas City Chiefs", "Chiefs"),
                "home_team_score": 17,
                "visitor_team_score": 20,
            }
        ],
        "meta": {"next_cursor": None, "per_page": 100, "prev_cursor": 300},
    }

    http_client_mock.get.side_effect = [page_1_response, page_2_response]

    result = api.get_games(sport="football_nfl", season=2024, team_id=1)

    assert isinstance(result, BallDontLieNFLGamesResponse)
    assert len(result.games) == 2
    assert result.games[0].id == 201
    assert result.games[1].id == 202
    assert result.games[0].away_team_name == "Buffalo Bills"
    assert result.games[1].away_team_name == "Kansas City Chiefs"
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


def test_get_players_paginates_until_next_cursor_is_null(api: BallDontLieNflAPI, http_client_mock, mocker):
    page_1_response = mocker.Mock()
    page_1_response.status_code = 200
    page_1_response.json.return_value = {
        "data": [
            {"id": 601, "first_name": "Patrick", "last_name": "Mahomes"}
        ],
        "meta": {"next_cursor": 900, "per_page": 100, "prev_cursor": None},
    }

    page_2_response = mocker.Mock()
    page_2_response.status_code = 200
    page_2_response.json.return_value = {
        "data": [
            {"id": 602, "first_name": "Travis", "last_name": "Kelce"}
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


def test_get_player_stats_paginates_until_next_cursor_is_null(api: BallDontLieNflAPI, http_client_mock, mocker):
    page_1_response = mocker.Mock()
    page_1_response.status_code = 200
    page_1_response.json.return_value = {
        "data": [
            {
                "player": {
                    "id": 701,
                    "first_name": "Josh",
                    "last_name": "Allen",
                    "team": _nfl_team(2, "BUF", "Buffalo Bills", "Bills"),
                },
                "game": {"id": 401, "season": 2024},
                "passing_yards": 250,
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
                    "first_name": "Josh",
                    "last_name": "Allen",
                    "team": _nfl_team(2, "BUF", "Buffalo Bills", "Bills"),
                },
                "game": {"id": 402, "season": 2024},
                "passing_yards": 310,
            }
        ],
        "meta": {"next_cursor": None, "per_page": 100, "prev_cursor": 1200},
    }

    http_client_mock.get.side_effect = [page_1_response, page_2_response]

    result = api.get_player_stats(player_id=701, season=2024, sport="football_nfl")

    assert isinstance(result, BallDontLieNFLPlayerStatsResponse)
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
