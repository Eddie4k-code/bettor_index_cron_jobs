from db.models.base import Base
from sqlalchemy import Column, Integer, String, Float, DateTime


class OddsAPIPropHistory(Base):
    __tablename__ = 'odds_api_props_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String, index=True)
    bookmaker = Column(String)
    market_key = Column(String)
    outcome_name = Column(String)
    old_point = Column(Float)
    new_point = Column(Float)
    old_price = Column(Float)
    new_price = Column(Float)
    outcome_description = Column(String)
    change_time = Column(DateTime)
    commence_time = Column(DateTime)
    sport_key = Column(String, index=True)
    home_team = Column(String)
    away_team = Column(String)
    change_type = Column(String)  # e.g., 'PointChange', 'PriceChange'
    player_id = Column(Integer, nullable=True)  # New field to link to player if applicable
    
