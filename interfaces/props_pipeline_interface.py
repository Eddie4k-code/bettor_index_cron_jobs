from abc import ABC, abstractmethod

class PropsPipelineInterface(ABC):
    @abstractmethod
    def get_props(self, date):
        pass