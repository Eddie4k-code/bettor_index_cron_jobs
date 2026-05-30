from abc import ABC, abstractmethod
from db.models.hit_rate_event_queue import HitRateEventQueue

class HitRateEventQueueRepositoryInterface(ABC):
    @abstractmethod
    def produce_event(self, event: HitRateEventQueue) -> None:
        """
        Insert a new event into the hit rate event queue.
        Args:
            event (HitRateEventQueue): The event to insert.
        Raises:
            Exception: If the event could not be inserted.
        """
        pass
