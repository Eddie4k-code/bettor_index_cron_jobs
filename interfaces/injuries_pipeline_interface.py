from abc import ABC, abstractmethod


class InjuriesPipelineInterface(ABC):
    @abstractmethod
    def get_injuries(self, sport: str) -> list[dict]:
        pass