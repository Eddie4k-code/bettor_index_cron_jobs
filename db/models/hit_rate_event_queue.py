from sqlalchemy import Column, Integer, String, JSON
from db.models.base import Base

class HitRateEventQueue(Base):
    __tablename__ = 'hit_rate_event_queue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String)
    bookmaker = Column(String)
    market_key = Column(String)
    outcome_name = Column(String)
    outcome_point = Column(String)
    outcome_description = Column(String)
    commence_time = Column(String)
    sport_key = Column(String, nullable=False, index=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    market_last_update = Column(String, nullable=False)
    outcome_price = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    status = Column(String, nullable=False, default='pending')
    event_type = Column(String, nullable=False)
    player_id = Column(Integer, nullable=True)
    player_team_id = Column(Integer, nullable=True)

