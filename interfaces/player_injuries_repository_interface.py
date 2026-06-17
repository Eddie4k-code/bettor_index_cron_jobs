from abc import ABC, abstractmethod


class PlayerInjuriesRepositoryInterface(ABC):
    @abstractmethod
    def insert_player_injury(self, player_injury):
        pass