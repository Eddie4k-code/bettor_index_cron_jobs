from sqlalchemy import Column, Integer, String
from db.models.base import Base

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    team_id = Column(Integer, nullable=False)
    sport_key = Column(String, nullable=False, index=True)
