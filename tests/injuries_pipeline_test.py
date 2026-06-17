from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from pipelines.injuries_pipeline import InjuriesPipeline
from schemas.sports_stats_api_responses import BallDontLieMLBInjuriesResponse


@pytest.fixture
def teams_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def player_injuries_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def api(mocker):
    return mocker.Mock()


@pytest.fixture
def pipeline(teams_repository, player_injuries_repository, api):
    return InjuriesPipeline(teams_repository, player_injuries_repository, api)


def test_get_injuries_raises_for_unsupported_sport(pipeline):
    with pytest.raises(ValueError, match="Unsupported sport: basketball_nba"):
        pipeline.get_injuries(sport="basketball_nba")


def test_get_injuries_returns_empty_list_when_no_teams_found(pipeline, teams_repository, api, player_injuries_repository):
    teams_repository.get_teams.return_value = []

    result = pipeline.get_injuries(sport="baseball_mlb")

    assert result == []
    api.get_injuries.assert_not_called()
    player_injuries_repository.insert_player_injury.assert_not_called()


def test_get_injuries_fetches_all_team_ids_in_one_request_and_persists_records(
    pipeline,
    teams_repository,
    api,
    player_injuries_repository,
):
    teams_repository.get_teams.return_value = [
        SimpleNamespace(id=14),
        SimpleNamespace(id=15),
    ]
    api.get_injuries.return_value = BallDontLieMLBInjuriesResponse(
        injuries=[
            {
                "player": {
                    "id": 101,
                    "first_name": "Clayton",
                    "last_name": "Kershaw",
                    "full_name": "Clayton Kershaw",
                    "team": {
                        "id": 14,
                        "slug": "los-angeles-dodgers",
                        "abbreviation": "LAD",
                        "display_name": "Los Angeles Dodgers",
                        "short_display_name": "Dodgers",
                        "name": "Dodgers",
                        "location": "Los Angeles",
                        "league": "National",
                        "division": "West",
                    },
                },
                "date": "2024-03-01T00:00:00Z",
                "return_date": "2024-04-15T00:00:00Z",
                "type": "shoulder",
                "detail": "left",
                "side": "left",
                "status": "10-day-il",
                "long_comment": "Recovering from shoulder surgery",
                "short_comment": "shoulder surgery",
            },
            {
                "player": {
                    "id": 202,
                    "first_name": "Player",
                    "last_name": "Two",
                    "full_name": "Player Two",
                    "team": {
                        "id": 15,
                        "slug": "san-diego-padres",
                        "abbreviation": "SDP",
                        "display_name": "San Diego Padres",
                        "short_display_name": "Padres",
                        "name": "Padres",
                        "location": "San Diego",
                        "league": "National",
                        "division": "West",
                    },
                },
                "date": "2024-03-10T00:00:00Z",
                "return_date": None,
                "type": "hamstring",
                "detail": "strain",
                "side": "right",
                "status": "day-to-day",
                "long_comment": "Limited in team activities",
                "short_comment": "hamstring strain",
            },
        ]
    )

    result = pipeline.get_injuries(sport="baseball_mlb")

    api.get_injuries.assert_called_once_with(team_ids=[14, 15])
    assert player_injuries_repository.insert_player_injury.call_count == 2

    first_record = player_injuries_repository.insert_player_injury.call_args_list[0].args[0]
    assert first_record.player_id == 101
    assert first_record.team_id == 14
    assert first_record.display_name == "Clayton Kershaw"
    assert first_record.date == datetime(2024, 3, 1, 0, 0, tzinfo=timezone.utc)
    assert first_record.return_date == datetime(2024, 4, 15, 0, 0, tzinfo=timezone.utc)

    second_record = player_injuries_repository.insert_player_injury.call_args_list[1].args[0]
    assert second_record.player_id == 202
    assert second_record.team_id == 15
    assert second_record.return_date is None
    assert second_record.short_comment == "hamstring strain"

    assert len(result) == 2
    assert result[0]["player"]["id"] == 101
    assert result[1]["player"]["team"]["id"] == 15