import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from repositories.teams_repository import TeamsRepository

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
    return TeamsRepository(db_session)

def test_insert_team(repository):
    from db.models.team import Team
    # Arrange: create a team instance
    team = Team(id=1, name="Team A", nickname="A", code="TA", city="CityA", sport_key="basketball_nba")

    # Act: insert the team
    repository.insert_team(team)
    repository.db.commit()

    # Assert: query the database for the team
    result = repository.db.query(Team).filter_by(id=1, sport_key="basketball_nba").first()
    assert result is not None
    assert result.name == "Team A"
    assert result.nickname == "A"
    assert result.code == "TA"
    assert result.city == "CityA"
    assert result.sport_key == "basketball_nba"