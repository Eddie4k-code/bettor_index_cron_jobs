# Model Repository CRUD Reference

Concrete patterns from this repository.

## Repositories and interfaces

| Repository | Interface | Test file |
|------------|-----------|-----------|
| `PlayersRepository` | `PlayersRepositoryInterface` | `tests/players_repository_test.py` |
| `MLBPlayerStatsRepository` | `MLBPlayerStatsRepositoryInterface` | `tests/mlb_player_stats_repository_test.py` |
| `MLBPlayerInjuriesRepository` | `MLBPlayerInjuriesRepositoryInterface` | `tests/mlb_player_injuries_repository_test.py` |
| `GamesRepository` | `GamesRepositoryInterface` | `tests/games_repository_test.py` |
| `TeamsRepository` | `TeamsRepositoryInterface` | `tests/teams_repository_test.py` |
| `PropsRepository` | `PropsRepositoryInterface` | `tests/props_repository_test.py` |

All repositories live in `repositories/` and accept `db` in the constructor.

## Write method shape

```python
import logging
from db.models.mlb_player_stats import MLBPlayerStats
from interfaces.mlb_player_stats_repository_interface import MLBPlayerStatsRepositoryInterface

logger = logging.getLogger(__name__)

class MLBPlayerStatsRepository(MLBPlayerStatsRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def insert_player_stats(self, player_stats: MLBPlayerStats):
        self.db.merge(player_stats)

        try:
            self.db.commit()
            logger.info(
                f"Inserted/Updated MLB player stats for player ID: {player_stats.player_id}, "
                f"season: {player_stats.season}, game ID: {player_stats.game_id}"
            )
            return player_stats
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Error inserting/updating MLB player stats for player ID: {player_stats.player_id}, "
                f"season: {player_stats.season}, game ID: {player_stats.game_id} - {str(e)}"
            )
            raise e
```

## Read method shape

```python
def get_players(self, sport: str):
    try:
        return self.db.query(Player).filter_by(sport_key=sport).all()
    except Exception as e:
        logger.error(f"Error fetching players for sport: {sport} - {str(e)}")
        raise e
```

## Interface shape

Keep interfaces narrow — only abstract methods that exist on the repository.

```python
from abc import ABC, abstractmethod
from db.models.mlb_player_stats import MLBPlayerStats

class MLBPlayerStatsRepositoryInterface(ABC):
    @abstractmethod
    def insert_player_stats(self, player_stats: MLBPlayerStats):
        pass
```

## Test patterns

**DB-backed write test** (when the repo family already uses in-memory SQLite):

```python
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_insert_player_stats_persists_record(repo):
    inserted = repo.insert_player_stats(player_stats)
    result = repo.db.query(MLBPlayerStats).filter_by(player_id=99).first()
    assert result is not None
    assert inserted == player_stats
```

**Mock rollback test** (required for write error path):

```python
def test_insert_player_stats_raises_when_commit_fails():
    mock_db = Mock()
    mock_db.commit.side_effect = RuntimeError("commit failed")
    repo = MLBPlayerStatsRepository(mock_db)

    with pytest.raises(RuntimeError, match="commit failed"):
        repo.insert_player_stats(player_stats)

    mock_db.merge.assert_called_once_with(player_stats)
    mock_db.rollback.assert_called_once()
```

## Validation commands

```bash
pytest tests/mlb_player_stats_repository_test.py -v
pytest tests/players_repository_test.py -v
pytest tests/mlb_player_injuries_repository_test.py -v
```
