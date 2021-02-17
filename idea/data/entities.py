from typing import Tuple


class Node:
    def __init__(self, node_id: int, node_type: int, demand: float):
        self._id = node_id
        self._type = node_type
        self._demand = demand  # [MV]

    def get_id(self) -> int:
        return self._id

    def get_type(self) -> int:
        return self._type

    def get_demand(self) -> float:
        return self._demand

    def __eq__(self, other) -> bool:
        return self._id == other.get_id() and \
            self._type == other.get_type() and \
            self._demand == other.get_demand()


class Generator:
    def __init__(self, node_id: int, generation: float, cost: float):
        self._node_id = node_id
        self._generation = generation  # [MV]
        self._cost = cost  # [PLN]

    def get_node_id(self) -> int:
        return self._node_id

    def get_generation(self) -> float:
        return self._generation

    def get_cost(self) -> float:
        return self._cost


class Branch:
    def __init__(self, node_from: int, node_to: int, flow: float):
        if flow >= 0.0:
            self._node_from = node_from
            self._node_to = node_to
        else:
            self._node_to = node_from
            self._node_from = node_to

        self._flow = abs(flow)  # [MV]

    def get_node_from(self) -> int:
        return self._node_from

    def get_node_to(self) -> int:
        return self._node_to

    def get_key(self) -> Tuple[int, int]:
        return self._node_from, self._node_to

    def get_flow(self) -> float:
        return self._flow
