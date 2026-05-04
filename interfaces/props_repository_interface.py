from abc import ABC, abstractmethod

class PropsRepositoryInterface(ABC):
    @abstractmethod
    def save_props(self, props):
        """
        Save a list of props to the database.
        Args:
            props (list): List of prop objects or dicts to save.
        """
        pass

    @abstractmethod
    def get_props_by_hours_ahead(self, hours_ahead: int):
        """
        Retrieve props from the database for a specific number of hours ahead.
        Args:
            hours_ahead (int): The number of hours ahead for which to retrieve props.
        Returns:
            list: List of props for the given number of hours ahead.
        """
        pass
