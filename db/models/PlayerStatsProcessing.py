from sqlalchemy import Column, Integer, String
from db.models.base import Base

class PlayerStatsProcessing(Base):
    __tablename__ = 'player_stats_processing'
    player_id = Column(Integer, nullable=False)
    sport_key = Column(String, nullable=False, index=True, primary_key=True)
    season = Column(Integer, nullable=False, primary_key=True)
    game_id = Column(Integer, nullable=False, primary_key=True)