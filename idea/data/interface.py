import abc
from typing import Set


class DatabaseInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_nodes') and
                callable(subclass.load_data_source) and
                hasattr(subclass, 'get_gens') and
                callable(subclass.extract_text) and
                hasattr(subclass, 'get_branches') and
                callable(subclass.extract_text) or
                NotImplemented)

    @abc.abstractmethod
    def get_nodes(self, hours: Set[int] = {}) -> str:
        """Get data about nodes for a given hour."""
        pass

    @abc.abstractmethod
    def get_gens(self, hours: Set[int] = {}) -> dict:
        """Get data about nodes for a given hour."""
        pass

    @abc.abstractmethod
    def get_branches(self, hours: Set[int] = {}) -> dict:
        """Get data about nodes for a given hour."""
        pass
