import pytest
from unittest.mock import Mock
from apis.api_sports_io_api import SportsIOAPI
from schemas.sports_stats_api_responses import SportsStatsAPIPlayerStatsResponse, PlayerStatsSchemaNBA

@pytest.fixture
def mock_http_client():
    return Mock()

@pytest.fixture
def mock_api_config():
    mock = Mock()
    mock.get_api_key.return_value = "fake_api_key"
    return mock

@pytest.fixture
def api(mock_api_config, mock_http_client):
    return SportsIOAPI(mock_api_config, mock_http_client)

def test_get_player_stats_success(api, mock_http_client):
    # Arrange
    player_id = 123
    season = 2023
    api_response = {
        "response": [
            {
                "player": {"id": player_id, "firstname": "LeBron", "lastname": "James"},
                "team": {"id": 10},
                "game": {"id": 555},
                "season": season,
                "min": "30",
                "points": 6,
                "pos": None,
                "fgm": 2,
                "fga": 5,
                "fgp": "40.0",
                "ftm": 2,
                "fta": 2,
                "ftp": "100.0",
                "tpm": 0,
                "tpa": 2,
                "tpp": "0",
                "offReb": 1,
                "defReb": 9,
                "totReb": 10,
                "assists": 2,
                "pFouls": 4,
                "steals": 1,
                "turnovers": 1,
                "blocks": 0
            }
        ]
    }
    mock_http_client.get.return_value.json.return_value = api_response

    # Act
    result = api.get_player_stats(player_id, season, sport="basketball_nba")

    # Assert
    assert isinstance(result, SportsStatsAPIPlayerStatsResponse)
    stats = result.stats
    assert stats.player_id == player_id
    assert stats.firstname == "LeBron"
    assert stats.lastname == "James"
    assert stats.team_id == 10
    assert stats.game_id == 555
    assert stats.season == season
    assert stats.points == 6
    assert stats.min == "30"
    assert stats.fgm == 2
    assert stats.fga == 5
    assert stats.fgp == "40.0"
    assert stats.ftm == 2
    assert stats.fta == 2
    assert stats.ftp == "100.0"
    assert stats.tpm == 0
    assert stats.tpa == 2
    assert stats.tpp == "0"
    assert stats.offReb == 1
    assert stats.defReb == 9
    assert stats.totReb == 10
    assert stats.assists == 2
    assert stats.pFouls == 4
    assert stats.steals == 1
    assert stats.turnovers == 1
    assert stats.blocks == 0
