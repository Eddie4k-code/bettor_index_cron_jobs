import pytest
from unittest.mock import Mock
from pipelines.players_pipeline import PlayersPipeline

@pytest.fixture
def mock_teams_repository():
    return Mock()

@pytest.fixture
def mock_players_repository():
    return Mock()

@pytest.fixture
def mock_api():
    return Mock()

@pytest.fixture
def pipeline(mock_teams_repository, mock_players_repository, mock_api):
    return PlayersPipeline(mock_teams_repository, mock_players_repository, mock_api)

def test_players_pipeline_get_players_inserts_players(pipeline, mock_teams_repository, mock_players_repository, mock_api):
    # Arrange
    mock_teams_repository.get_teams.return_value = [
        Mock(id=1, sport_key="basketball_nba"),
        Mock(id=2, sport_key="basketball_nba")
    ]
    mock_api.get_players.side_effect = [
        # Players for team 1
        Mock(players=[Mock(id=101, firstname="LeBron", lastname="James")]),
        # Players for team 2
        Mock(players=[Mock(id=201, firstname="Stephen", lastname="Curry")])
    ]

    # Act
    pipeline.get_players(sport="basketball_nba", season=2023)

    # Assert
    assert mock_teams_repository.get_teams.called
    assert mock_api.get_players.call_count == 2
    assert mock_players_repository.insert_player.call_count == 2