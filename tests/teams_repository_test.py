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


def test_get_teams_by_sport(repository):
    from db.models.team import Team
    # Arrange: insert multiple teams with different sport_key values
    team1 = Team(id=1, name="Team A", nickname="A", code="TA", city="CityA", sport_key="basketball_nba")
    team2 = Team(id=2, name="Team B", nickname="B", code="TB", city="CityB", sport_key="basketball_nba")
    team3 = Team(id=3, name="Team C", nickname="C", code="TC", city="CityC", sport_key="football_nfl")
    repository.insert_team(team1)
    repository.insert_team(team2)
    repository.insert_team(team3)
    repository.db.commit()

    # Act: fetch teams for basketball_nba
    teams = repository.get_teams("basketball_nba")

    # Assert: only basketball_nba teams are returned
    assert len(teams) == 2
    team_names = {team.name for team in teams}
    assert "Team A" in team_names
    assert "Team B" in team_names
    assert all(team.sport_key == "basketball_nba" for team in teams)