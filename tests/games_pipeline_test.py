from datetime import datetime
from types import SimpleNamespace

import pytest

from pipelines.games_pipeline import GamesPipeline
from schemas.sports_stats_api_responses import BallDontLieMLBGameSchema, GamesSchema


@pytest.fixture
def games_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def teams_repository(mocker):
    return mocker.Mock()


@pytest.fixture
def api(mocker):
    return mocker.Mock()


@pytest.fixture
def pipeline(games_repository, teams_repository, api):
    return GamesPipeline(games_repository, teams_repository, api)


def test_get_games_processes_finished_nba_games(pipeline, games_repository, teams_repository, api):
    teams_repository.get_teams.return_value = [SimpleNamespace(id=10)]
    api.get_games.return_value = {
        "games": [
            GamesSchema(
                id=101,
                season=2024,
                date=datetime.fromisoformat("2024-04-01T19:00:00+00:00"),
                status="Finished",
                home_team="Lakers",
                home_team_id=1,
                away_team="Celtics",
                away_team_id=2,
                home_team_score=120,
                away_team_score=118,
            )
        ]
    }

    pipeline.get_games(sport="basketball_nba", season=2024)

    games_repository.insert_games.assert_called_once()
    inserted_game = games_repository.insert_games.call_args.args[0]
    assert inserted_game.id == 101
    assert inserted_game.home_team == "lakers"
    assert inserted_game.away_team == "celtics"
    assert inserted_game.home_team_score == 120
    assert inserted_game.away_team_score == 118
    assert inserted_game.sport_key == "basketball_nba"


def test_get_games_processes_final_mlb_games(pipeline, games_repository, teams_repository, api):
    teams_repository.get_teams.return_value = [SimpleNamespace(id=20)]
    api.get_games.return_value = {
        "games": [
            BallDontLieMLBGameSchema(
                id=202,
                season=2024,
                date="2024-04-01T19:00:00Z",
                status="Final",
                home_team_name="Yankees",
                home_team_id=3,
                away_team_name="Red Sox",
                away_team_id=4,
                home_runs=5,
                away_runs=3,
            )
        ]
    }

    pipeline.get_games(sport="baseball_mlb", season=2024)

    games_repository.insert_games.assert_called_once()
    inserted_game = games_repository.insert_games.call_args.args[0]
    assert inserted_game.id == 202
    assert inserted_game.date == datetime.fromisoformat("2024-04-01T19:00:00+00:00")
    assert inserted_game.home_team == "yankees"
    assert inserted_game.away_team == "red sox"
    assert inserted_game.home_team_score == 5
    assert inserted_game.away_team_score == 3
    assert inserted_game.sport_key == "baseball_mlb"


def test_get_games_skips_non_final_mlb_games(pipeline, games_repository, teams_repository, api):
    teams_repository.get_teams.return_value = [SimpleNamespace(id=20)]
    api.get_games.return_value = {
        "games": [
            BallDontLieMLBGameSchema(
                id=203,
                season=2024,
                date="2024-04-02",
                status="Scheduled",
                home_team_name="Yankees",
                home_team_id=3,
                away_team_name="Blue Jays",
                away_team_id=5,
                home_runs=None,
                away_runs=None,
            )
        ]
    }

    pipeline.get_games(sport="baseball_mlb", season=2024)

    games_repository.insert_games.assert_not_called()


def test_get_games_raises_for_unsupported_sport(pipeline, teams_repository):
    teams_repository.get_teams.return_value = [SimpleNamespace(id=99)]

    with pytest.raises(ValueError, match="Unsupported sport"):
        pipeline.get_games(sport="football_nfl", season=2024)
