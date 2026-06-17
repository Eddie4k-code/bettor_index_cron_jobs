from contextlib import contextmanager

import pytest

import main


@contextmanager
def fake_db_context(db):
    yield db


def test_main_runs_mlb_injuries_pipeline(monkeypatch, mocker):
    db = mocker.Mock()
    db.get_bind.return_value = mocker.Mock()
    teams_repository = mocker.Mock()
    players_repository = mocker.Mock()
    games_repository = mocker.Mock()
    mlb_player_stats_repository = mocker.Mock()
    hit_rate_event_queue_repository = mocker.Mock()
    odds_api_prop_history_repository = mocker.Mock()
    props_repository = mocker.Mock()
    http_client = mocker.Mock()
    api_config = mocker.Mock()
    odds_api = mocker.Mock()
    ball_dont_lie_api = mocker.Mock()
    injuries_repository = mocker.Mock()
    injuries_pipeline = mocker.Mock()

    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "injuries", "--sport", "baseball_mlb"],
    )
    mocker.patch.object(main, "get_db", return_value=fake_db_context(db))
    mocker.patch.object(main.Base.metadata, "create_all")
    mocker.patch.object(main, "TeamsRepository", return_value=teams_repository)
    mocker.patch.object(main, "PlayersRepository", return_value=players_repository)
    mocker.patch.object(main, "GamesRepository", return_value=games_repository)
    mocker.patch.object(main, "MLBPlayerStatsRepository", return_value=mlb_player_stats_repository)
    mocker.patch.object(main, "HitRateEventQueueRepository", return_value=hit_rate_event_queue_repository)
    mocker.patch.object(main, "OddsAPIPropsHistoryRepository", return_value=odds_api_prop_history_repository)
    mocker.patch.object(main, "PropsRepository", return_value=props_repository)
    mocker.patch.object(main, "HTTPXClient", return_value=http_client)
    mocker.patch.object(main, "APIConfig", return_value=api_config)
    mocker.patch.object(main, "TheOddsAPI", return_value=odds_api)
    mocker.patch.object(main, "BallDontLieMlbAPI", return_value=ball_dont_lie_api)
    mocker.patch.object(main, "TeamsPipeline")
    mocker.patch.object(main, "GamesPipeline")
    mocker.patch.object(main, "PlayersPipeline")
    mocker.patch.object(main, "PropsPipeline")
    mocker.patch.object(main, "PlayerStatsPipeline")
    mocker.patch.object(main, "MLBPlayerInjuriesRepository", return_value=injuries_repository)
    mocker.patch.object(main, "InjuriesPipeline", return_value=injuries_pipeline)

    main.main()

    main.MLBPlayerInjuriesRepository.assert_called_once_with(db)
    main.InjuriesPipeline.assert_called_once_with(
        teams_repository=teams_repository,
        player_injuries_repository=injuries_repository,
        api=ball_dont_lie_api,
    )
    injuries_pipeline.get_injuries.assert_called_once_with(sport="baseball_mlb")


def test_main_exits_for_nba_injuries_command(monkeypatch, mocker):
    db = mocker.Mock()
    db.get_bind.return_value = mocker.Mock()

    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "injuries", "--sport", "basketball_nba"],
    )
    mocker.patch.object(main, "get_db", return_value=fake_db_context(db))
    mocker.patch.object(main.Base.metadata, "create_all")
    mocker.patch.object(main, "TeamsRepository", return_value=mocker.Mock())
    mocker.patch.object(main, "PlayersRepository", return_value=mocker.Mock())
    mocker.patch.object(main, "GamesRepository", return_value=mocker.Mock())
    mocker.patch.object(main, "NBAPlayerStatsRepository", return_value=mocker.Mock())
    mocker.patch.object(main, "HitRateEventQueueRepository", return_value=mocker.Mock())
    mocker.patch.object(main, "OddsAPIPropsHistoryRepository", return_value=mocker.Mock())
    mocker.patch.object(main, "PropsRepository", return_value=mocker.Mock())
    mocker.patch.object(main, "HTTPXClient", return_value=mocker.Mock())
    mocker.patch.object(main, "APIConfig", return_value=mocker.Mock())
    mocker.patch.object(main, "TheOddsAPI", return_value=mocker.Mock())
    mocker.patch.object(main, "SportsIOAPI", return_value=mocker.Mock())
    mocker.patch.object(main, "TeamsPipeline")
    mocker.patch.object(main, "GamesPipeline")
    mocker.patch.object(main, "PlayersPipeline")
    mocker.patch.object(main, "PropsPipeline")
    mocker.patch.object(main, "PlayerStatsPipeline")
    mocker.patch.object(main.logging, "error")

    with pytest.raises(SystemExit) as exc_info:
        main.main()

    assert exc_info.value.code == 1
    main.logging.error.assert_called_once_with("Injuries pipeline is only supported for baseball_mlb")