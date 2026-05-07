from abc import abstractmethod, ABC

class TeamsPipelineInterface(ABC):
    @abstractmethod
    def get_teams(self) -> list[dict]:
        pass