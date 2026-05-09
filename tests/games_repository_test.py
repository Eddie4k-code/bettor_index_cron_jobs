import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import team
from db.models.base import Base
from repositories.games_repository import GamesRepository
from db.models.games import Game
from datetime import datetime

@pytest.fixture(scope="function")
def db_session():
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repository(db_session):
    return GamesRepository(db_session)

def test_insert_game(repository):
    # Arrange: create a game instance
    game = Game(
        id=1,
        season=2023,
        date=datetime.fromisoformat("2023-10-01T19:00:00+00:00"),
        status="scheduled",
        home_team="Team A",
        home_team_id=1,
        away_team="Team B",
        away_team_id=2,
        home_team_score=0,
        away_team_score=0
    )

    # Act: insert the game
    repository.insert_games(game)
    repository.db.commit()

    # Assert: query the database for the game
    result = repository.db.query(Game).filter_by(id=1).first()
    assert result is not None
    assert result.home_team == "Team A"
    assert result.away_team == "Team B"
    assert result.home_team_score == 0
    assert result.away_team_score == 0


def test_insert_error_raises(repository):
    # Arrange: create a game instance with missing required fields
    game = Game(
        id=1,
        season=2023,
        date=datetime.fromisoformat("2023-10-01T19:00:00+00:00"),
        home_team="Team A",
        home_team_id=1,
        away_team="Team B",
        away_team_id=2,
        home_team_score=0,
        away_team_score=0
    )

    with pytest.raises(Exception):
        repository.insert_games(game)
        repository.db.commit()