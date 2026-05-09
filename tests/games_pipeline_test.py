
import pytest
from pytest_mock import mocker
from schemas.sports_stats_api_responses import TeamSchema



@pytest.fixture
def mock_repository(mocker):
    return mocker.Mock()

@pytest.fixture
def mock_api(mocker):
    return mocker.Mock()

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
