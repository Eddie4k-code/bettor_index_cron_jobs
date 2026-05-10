from sqlalchemy import Column, Integer, String, JSON
from db.models.base import Base

class HitRateEventQueue(Base):
    __tablename__ = 'hit_rate_event_queue'
    event_type = Column(String, nullable=False)
    prop_id = Column(Integer, nullable=False, primary_key=True)
    sport_key = Column(String, nullable=False, index=True, primary_key=True)
    status = Column(String, nullable=False, default='pending')
    payload = Column(JSON, nullable=True)
    processed_at = Column(String, nullable=True)
    error_message = Column(String, nullable=True)    
    created_at = Column(String, nullable=False, primary_key=True)
