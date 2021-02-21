from typing import Dict, Tuple, List

from .network_elements import Node, Branch
from .network_state import NetworkState
from .style import ANNOTATION_UNDERLINE
from ..data.interface import DatabaseInterface


class NetworkData:
    def __init__(self, db: DatabaseInterface):
        self._hour_to_nodes = db.get_hour_to_nodes()
        self._hour_to_branches = db.get_hour_to_branches()
        self._hour_to_gens = db.get_hour_to_gens()
        self._network_states: Dict[Tuple[int, int], NetworkState] = dict()

    def get_state(self, hour_from: int, hour_to: int) -> NetworkState:
        state_key = (hour_from, hour_to)

        if state_key not in self._network_states:
            simple_nodes = self._get_simple_nodes(hour_from, hour_to)
            gens = self._get_gens()
            branches = self._get_branches(hour_from, hour_to)
            self._network_states[state_key] = NetworkState(simple_nodes, gens, branches)

        return self._network_states[state_key]

    def _get_simple_nodes(self, hour_from: int, hour_to: int) -> List[Node]:
        nodes_from = self._hour_to_nodes[hour_from]
        nodes_to = self._hour_to_nodes[hour_to]
        simple_nodes: List[Node] = list()

        for node_id, node in nodes_to.items():
            node_type = node.get_type()

            if node_type == 1:  # Simple nodes have type = 1
                node_from_demand = nodes_from[node_id].get_demand()
                node_to_demand = node.get_demand()

                if node_id in nodes_from:
                    color = node_to_demand - node_from_demand
                else:
                    color = node_to_demand

                size = (abs(nodes_from[node_id].get_demand()) + abs(nodes_to[node_id].get_demand())) / 2.0
                text = 'Simple node #%d, type %d <br>' % (node_id, node.get_type()) + \
                       ANNOTATION_UNDERLINE + \
                       'demand on hour #%d = %.2f [MV] <br>' % (hour_from, node_from_demand) + \
                       'demand on hour #%d = %.2f [MV] <br>' % (hour_to, node_to_demand) + \
                       'demand diff = %.2f [MV] <br>' % color + \
                       'avg abs demand = %.2f [MV] <br>' % size
                simple_nodes.append(Node(node_id, size, color, node_type, text))

        return simple_nodes

    def _get_gens(self) -> List[Node]:
        gens = self._hour_to_gens[1]  # Generation is the same in each hour
        nodes = self._hour_to_nodes[1]  # Demand for generators is the same for each hour
        gens_list: List[Node] = list()

        for node_id, gen in gens.items():
            node = nodes[node_id]
            node_type = nodes[node_id].get_type()

            if node_type != 1:  # Generators have type != 1, it should always be true
                generation = gen.get_generation()
                demand = node.get_demand()
                size = generation - demand
                cost = gen.get_cost()
                color = cost if size >= 0 else -cost
                text = 'Generator node #%d, type %d <br>' % (node_id, node.get_type()) + \
                       ANNOTATION_UNDERLINE + \
                       'generation = %.2f [MV] <br>' % generation + \
                       'demand = %.2f [MV] <br>' % demand + \
                       'generation - demand = %.2f [MV] <br>' % size + \
                       'balance = %.2f [PLN] <br>' % cost
                gens_list.append(Node(node_id, abs(size), color, node_type, text))

        return gens_list

    def _get_branches(self, hour_from: int, hour_to: int) -> List[Branch]:
        branches_from = self._hour_to_branches[hour_from]
        branches_to = self._hour_to_branches[hour_to]
        branches_list: List[Branch] = list()

        for (node_from, node_to), branch in branches_to.items():
            if (node_from, node_to) in branches_from:
                # Flow difference is represented as arrow size, not a color of the line
                # because plotly do not have built-in color scale for lines
                color = branch.get_flow() - branches_from[(node_from, node_to)].get_flow()
                width = (abs(branch.get_flow()) + abs(branches_from[(node_from, node_to)].get_flow())) / 2
            elif (node_to, node_from) in branches_from:
                color = branch.get_flow() + branches_from[(node_to, node_from)].get_flow()
                width = (abs(branch.get_flow()) + abs(branches_from[(node_to, node_from)].get_flow())) / 2
            else:
                color = branch.get_flow()
                width = abs(branch.get_flow())

            if color >= 0:
                branch = Branch(node_from, node_to, width, arrow_size=color)
            else:
                branch = Branch(node_to, node_from, width, arrow_size=abs(color))

            branches_list.append(branch)

        return branches_list
