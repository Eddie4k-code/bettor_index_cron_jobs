import logging
from db.models.hit_rate_event_queue import HitRateEventQueue
from interfaces.hit_rate_event_queue_repository_interface import HitRateEventQueueRepositoryInterface

logger = logging.getLogger(__name__)

class HitRateEventQueueRepository(HitRateEventQueueRepositoryInterface):
    def __init__(self, db):
        self.db = db

    def produce_event(self, event: HitRateEventQueue) -> None:
        try:
            self.db.merge(event)  # Upsert by composite PK for idempotency
            self.db.commit()
            logger.info(f"Produced hit rate event: event_id={event.event_id}, sport_key={event.sport_key}, created_at={event.created_at}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error producing hit rate event: event_id={event.event_id}, sport_key={event.sport_key}, created_at={event.created_at} - {str(e)}")
            raise
