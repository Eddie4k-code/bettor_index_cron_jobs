import pytest
from unittest.mock import Mock
from pipelines.player_stats_pipeline import PlayerStatsPipeline
from schemas.sports_stats_api_responses import PlayerStatsSchemaNBA, SportsStatsAPIPlayerStatsResponse

def test_get_player_stats_nba_calls_api_and_inserts():
    # Arrange
    mock_api = Mock()
    mock_nba_repo = Mock()
    mock_games_repo = Mock()
    mock_players_repo = Mock()
    mock_processing_repo = Mock()
    pipeline = PlayerStatsPipeline(
        sports_stats_api=mock_api,
        nba_player_stats_repository=mock_nba_repo,
        games_repository=mock_games_repo,
        players_repository=mock_players_repo,
    )
    player_id = 23
    season = 2023
    sport = "basketball_nba"
    nba_stats = [PlayerStatsSchemaNBA(player_id=player_id, firstname="lebron", lastname="james", team_id=1, game_id=100, season=season)]
    mock_api.get_player_stats.return_value = SportsStatsAPIPlayerStatsResponse(stats=nba_stats)
    mock_players_repo.get_players.return_value = [Mock(id=player_id)]
    mock_processing_repo.is_processed.return_value = False

    # Mock the game object with a date
    mock_game = Mock()
    mock_game.date = "2024-01-01T19:00:00"
    mock_games_repo.get_game.return_value = mock_game

    # Act
    pipeline.get_player_stats(sport=sport, season=season)

    # Assert
    mock_api.get_player_stats.assert_called_with(player_id=player_id, season=season, sport=sport)
    mock_games_repo.get_game.assert_called_with(100, sport)
    # Check that commence_time is set from the game date
    args, kwargs = mock_nba_repo.insert_player_stats.call_args
    player_stats_obj = kwargs.get('player_stats') or (args[0] if args else None)
    assert player_stats_obj.commence_time.isoformat().startswith("2024-01-01T19:00:00"), "commence_time should be set from game.date"