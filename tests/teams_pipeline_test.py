import pytest
from unittest.mock import Mock
from pipelines.teams_pipeline import TeamsPipeline
from db.models.team import Team
from schemas.sports_stats_api_responses import BallDontLieMLBTeamSchema, TeamSchema

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

    inserted_team = mock_repository.insert_team.call_args_list[0].args[0]
    assert isinstance(inserted_team, Team)
    assert inserted_team.name == "team a"
    assert inserted_team.nickname == "a"
    assert inserted_team.code == "ta"
    assert inserted_team.city == "citya"
    assert inserted_team.sport_key == "basketball_nba"

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


def test_get_teams_inserts_mlb_teams_with_mapped_fields(pipeline, mock_repository, mock_api):
    mock_api.get_teams.return_value = {
        "teams": [
            BallDontLieMLBTeamSchema(
                id=1,
                abbreviation="NYY",
                display_name="New York Yankees",
                name="Yankees",
                location="New York",
                league="AL",
                division="AL East",
            ),
            BallDontLieMLBTeamSchema(
                id=2,
                abbreviation="BOS",
                display_name="Boston Red Sox",
                name="Red Sox",
                location="Boston",
                league="AL",
                division="AL East",
            ),
        ]
    }

    result = pipeline.get_teams(sport="baseball_mlb")

    assert mock_repository.insert_team.call_count == 2
    assert isinstance(result, list)
    assert result[0]["abbreviation"] == "NYY"
    assert result[1]["abbreviation"] == "BOS"

    first_insert = mock_repository.insert_team.call_args_list[0].args[0]
    second_insert = mock_repository.insert_team.call_args_list[1].args[0]

    assert isinstance(first_insert, Team)
    assert first_insert.name == "yankees"
    assert first_insert.nickname == "nyy"
    assert first_insert.code == "nyy"
    assert first_insert.city == "new york"
    assert first_insert.sport_key == "baseball_mlb"

    assert isinstance(second_insert, Team)
    assert second_insert.name == "red sox"
    assert second_insert.nickname == "bos"
    assert second_insert.code == "bos"
    assert second_insert.city == "boston"
    assert second_insert.sport_key == "baseball_mlb"


def test_get_teams_unsupported_sport_raises_value_error(pipeline, mock_repository, mock_api):
    mock_api.get_teams.return_value = {"teams": []}

    with pytest.raises(ValueError, match="Unsupported sport: hockey_nhl"):
        pipeline.get_teams(sport="hockey_nhl")

    mock_repository.insert_team.assert_not_called()
