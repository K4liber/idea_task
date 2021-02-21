import abc
from typing import Set, Dict, Tuple

from ..data.entities import Node, Generator, Branch


class DatabaseInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_hour_to_nodes') and
                callable(subclass.get_hour_to_nodes) and
                hasattr(subclass, 'get_hour_to_gens') and
                callable(subclass.get_hour_to_gens) and
                hasattr(subclass, 'get_hour_to_branches') and
                callable(subclass.get_hour_to_branches) or
                hasattr(subclass, 'get_branch_to_cluster') and
                callable(subclass.get_branch_to_cluster) or
                NotImplemented)

    @abc.abstractmethod
    def get_hour_to_nodes(self, hours: Set[int] = None) -> Dict[int, Dict[int, Node]]:
        """Get data about nodes for given hours.
        If 'hours' argument is None, returns data for all of the hours."""
        pass

    @abc.abstractmethod
    def get_hour_to_gens(self, hours: Set[int] = None) -> Dict[int, Dict[int, Generator]]:
        """Get data about nodes for given hours.
        If 'hours' argument is None, returns data for all of the hours."""
        pass

    @abc.abstractmethod
    def get_hour_to_branches(self, hours: Set[int] = None) -> Dict[int, Dict[Tuple[int, int], Branch]]:
        """Get data about nodes for given hours.
        If 'hours' argument is None, returns data for all of the hours."""
        pass

    @abc.abstractmethod
    def get_branch_to_cluster(self, n_clusters: int, hours: Set[int] = None) -> Dict[Tuple[int, int], int]:
        """Get branch clusters based on averaged data through given hours.
        If 'hours' argument is None, returns data for all of the hours."""
        pass
