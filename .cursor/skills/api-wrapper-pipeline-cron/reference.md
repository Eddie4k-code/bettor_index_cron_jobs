# API Wrapper Pipeline Cron Reference

Concrete patterns from this repository.

## Pipelines and tests

| Pipeline | Test file | Public entrypoint |
|----------|-----------|-------------------|
| `GamesPipeline` | `tests/games_pipeline_test.py` | `get_games(sport, season)` |
| `PlayersPipeline` | `tests/players_pipeline_test.py` | `get_players(sport, season)` |
| `PlayerStatsPipeline` | `tests/player_stats_pipeline_test.py` | `get_player_stats(sport, season)` |
| `PropsPipeline` | `tests/props_pipeline_test.py` | `get_props(sport, hours_ahead, markets)` |
| `InjuriesPipeline` | `tests/injuries_pipeline_test.py` | `get_injuries(sport)` |
| `TeamsPipeline` | `tests/teams_pipeline_test.py` | `get_teams(sport)` |

## Pipeline shape

Inject repositories and API interfaces through the constructor. Branch by sport in the public method; delegate to private helpers.

```python
class PlayerStatsPipeline(PlayerStatsPipelineInterface):
    def __init__(
        self,
        sports_stats_api: SportsStatsAPIInterface,
        players_repository: PlayersRepositoryInterface,
        games_repository: GamesRepositoryInterface,
        nba_player_stats_repository: NBAPlayerStatsRepositoryInterface | None = None,
        mlb_player_stats_repository: MLBPlayerStatsRepositoryInterface | None = None,
    ):
        self.sports_stats_api = sports_stats_api
        # ...

    def get_player_stats(self, sport: str, season: int):
        if sport == "basketball_nba":
            self._process_nba_player_stats(sport=sport, season=season)
            return
        if sport == "baseball_mlb":
            self._process_mlb_player_stats(sport=sport, season=season)
            return
        raise ValueError(f"Unsupported sport: {sport}")
```

## CLI wiring in `main.py`

1. Add an argparse subparser for the new command.
2. Inside the sport-specific branch (`basketball_nba` or `baseball_mlb`):
   - initialize repositories
   - initialize `HTTPXClient`, `APIConfig`, and API wrappers
   - initialize the pipeline with injected dependencies
   - dispatch on `args.command`

```python
player_stats_parser = subparsers.add_parser("player_stats", help="Run the player stats pipeline")
player_stats_parser.add_argument("--sport", type=str, default="basketball_nba")
player_stats_parser.add_argument("--season", type=int, default=2023)

# Inside sport branch:
nba_player_stats_pipeline = PlayerStatsPipeline(
    sports_stats_api=sports_io_api,
    players_repository=players_repository,
    games_repository=games_repository,
    nba_player_stats_repository=nba_player_stats_repository,
)

if args.command == "player_stats":
    nba_player_stats_pipeline.get_player_stats(sport=args.sport, season=args.season)
```

Run via CLI:

```bash
python main.py player_stats --sport basketball_nba --season 2023
python main.py injuries --sport baseball_mlb
```

## Test shape

Mock repositories and API; assert wrapper calls, repository inserts, and normalized field values.

```python
def test_get_player_stats_nba_calls_api_and_inserts():
    mock_api = Mock()
    mock_nba_repo = Mock()
    mock_games_repo = Mock()
    mock_players_repo = Mock()
    pipeline = PlayerStatsPipeline(
        sports_stats_api=mock_api,
        players_repository=mock_players_repo,
        games_repository=mock_games_repo,
        nba_player_stats_repository=mock_nba_repo,
    )
    mock_api.get_player_stats.return_value = SportsStatsAPIPlayerStatsResponse(stats=[...])
    mock_players_repo.get_players.return_value = [Mock(id=23)]

    pipeline.get_player_stats(sport="basketball_nba", season=2023)

    mock_api.get_player_stats.assert_called_with(player_id=23, season=2023, sport="basketball_nba")
    mock_nba_repo.insert_player_stats.assert_called()
```

## Validation commands

```bash
pytest tests/player_stats_pipeline_test.py -v
pytest tests/games_pipeline_test.py -v
pytest tests/injuries_pipeline_test.py -v
```
