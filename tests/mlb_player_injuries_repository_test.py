from datetime import datetime
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models.base import Base
from db.models.mlb_player_injuries import MLBPlayerInjuries
from repositories.mlb_player_injuries_repository import MLBPlayerInjuriesRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def repo(db_session):
    return MLBPlayerInjuriesRepository(db_session)


def test_insert_player_injury_persists_record(repo):
    player_injury = MLBPlayerInjuries(
        player_id=208,
        team_id=14,
        date=datetime.fromisoformat("2024-11-05T23:32:00+00:00"),
        return_date=datetime.fromisoformat("2025-02-01T00:00:00+00:00"),
        display_name="Shohei Ohtani",
        position="Designated Hitter",
        type="Shoulder",
        detail="Surgery",
        side="Left",
        status="Out",
        long_comment="Long injury context.",
        short_comment="Short injury context.",
    )

    inserted_player_injury = repo.insert_player_injury(player_injury)

    result = repo.db.query(MLBPlayerInjuries).filter_by(player_id=208).first()

    assert inserted_player_injury == player_injury
    assert result is not None
    assert result.team_id == 14
    assert result.display_name == "Shohei Ohtani"
    assert result.position == "Designated Hitter"
    assert result.type == "Shoulder"
    assert result.status == "Out"


def test_insert_player_injury_raises_when_commit_fails():
    mock_db = Mock()
    mock_db.commit.side_effect = RuntimeError("commit failed")
    repo = MLBPlayerInjuriesRepository(mock_db)
    player_injury = MLBPlayerInjuries(
        player_id=208,
        team_id=14,
        status="Out",
    )

    with pytest.raises(RuntimeError, match="commit failed"):
        repo.insert_player_injury(player_injury)

    mock_db.merge.assert_called_once_with(player_injury)
    mock_db.rollback.assert_called_once()