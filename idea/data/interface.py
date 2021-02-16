import abc
from typing import Set


class DatabaseInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_nodes') and
                callable(subclass.get_nodes) and
                hasattr(subclass, 'get_gens') and
                callable(subclass.get_gens) and
                hasattr(subclass, 'get_branches') and
                callable(subclass.get_branches) or
                NotImplemented)

    @abc.abstractmethod
    def get_nodes(self, hours: Set[int] = None) -> dict:
        """Get data about nodes for a given hour."""
        pass

    @abc.abstractmethod
    def get_gens(self, hours: Set[int] = None) -> dict:
        """Get data about nodes for a given hour."""
        pass

    @abc.abstractmethod
    def get_branches(self, hours: Set[int] = None) -> dict:
        """Get data about nodes for a given hour."""
        pass
