import pytest
from unittest.mock import Mock
from pipelines.teams_pipeline import TeamsPipeline
from db.models.team import Team
from schemas.sports_stats_api_responses import TeamSchema

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def mock_api():
    return Mock()

@pytest.fixture
def pipeline(mock_repository, mock_api):
    from pipelines.teams_pipeline import TeamsPipeline
    return TeamsPipeline(mock_repository, mock_api)

def test_get_teams_inserts_teams(pipeline, mock_repository, mock_api):
    # Arrange
    mock_api.get_teams.return_value = {
        "teams": [
            TeamSchema(id=1, name="Team A", nickname="A", code="TA", city="CityA"),
            TeamSchema(id=2, name="Team B", nickname="B", code="TB", city="CityB"),
        ]
    }

    # Act
    result = pipeline.get_teams(sport="basketball_nba")

    # Assert
    assert mock_repository.insert_team.call_count == 2
    assert isinstance(result, list)
    assert result[0]["name"] == "Team A"
    assert result[1]["name"] == "Team B"

def test_get_teams_empty_list(pipeline, mock_repository, mock_api):
    mock_api.get_teams.return_value = {"teams": []}
    result = pipeline.get_teams(sport="basketball_nba")
    assert mock_repository.insert_team.call_count == 0
    assert result == []

def test_get_teams_api_failure(pipeline, mock_repository, mock_api):
    mock_api.get_teams.side_effect = Exception("API error")
    with pytest.raises(Exception):
        pipeline.get_teams(sport="basketball_nba")

def test_get_teams_repository_failure(pipeline, mock_repository, mock_api):
    mock_api.get_teams.return_value = {
        "teams": [
            TeamSchema(id=1, name="Team A", nickname="A", code="TA", city="CityA"),
        ]
    }
    mock_repository.insert_team.side_effect = Exception("DB error")
    with pytest.raises(Exception):
        pipeline.get_teams(sport="basketball_nba")
