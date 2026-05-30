from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
import datetime
from db.models.base import Base

class OddsAPIProp(Base):
    __tablename__ = 'odds_api_props'
    event_id = Column(String, primary_key=True)
    bookmaker = Column(String, primary_key=True)
    market_key = Column(String, primary_key=True)
    outcome_name = Column(String, primary_key=True)
    outcome_point = Column(Float)
    outcome_description = Column(String, primary_key=True)
    commence_time = Column(DateTime)
    sport_key = Column(String, nullable=False, index=True)
    sport_title = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    market_last_update = Column(DateTime, nullable=False)
    outcome_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    player_id = Column(Integer, nullable=True)  # New column for player association
