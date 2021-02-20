from typing import Dict, Tuple, List

import networkx as nx

import plotly.graph_objects as go

from .network_elements import Node, Branch, Arrow
from .style import ANNOTATION_UNDERLINE, NODE_TYPE_TO_SYMBOL
from .utils import get_arrow_from_branch, size_scale
from ..data.interface import DatabaseInterface


class NetworkState:
    def __init__(self, simple_nodes: List[Node], gens: List[Node], branches: List[Branch]):
        self._simple_nodes = simple_nodes
        self._gens = gens
        self._branches = branches
        self._arrows: List[Arrow] = []
        graph = nx.Graph()

        for simple_node in simple_nodes:
            graph.add_node(simple_node.id)

        for gen in gens:
            graph.add_node(gen.id)

        for branch in branches:
            graph.add_edge(branch.from_node, branch.to_node)

        self._nodes_positions = nx.spring_layout(graph, seed=9)
        # Generate the arrows
        for branch in branches:
            arrow = get_arrow_from_branch(branch.from_node, branch.to_node,
                                          branch.arrow_size, self._nodes_positions)
            arrow_annotation = 'Branch from node #%d to #%d <br>' % (branch.from_node, branch.to_node) + \
                               ANNOTATION_UNDERLINE + \
                               'abs avg flow = %.2f [MV] <br>' % branch.width + \
                               'flow diff = %.2f [MV] <br>' % branch.arrow_size
            arrow.set_annotation(arrow_annotation)
            self._arrows.append(arrow)

    def get_figure(self) -> go.Figure:
        data: List[go.Scatter] = list()
        branches_scatter = self._get_branches_scatters()
        data.extend(branches_scatter)
        data.append(self._get_simple_nodes_scatter())
        data.append(self._get_gens_scatter())
        # Append an arrow marker to show arrow in the legend
        data.append(go.Scatter(
            x=[0], y=[0],
            x0=2,
            mode='markers',
            visible='legendonly',
            text='flow diff representation',
            name='flow diff',
            opacity=0,
            showlegend=True,
            marker_symbol=48,
            marker=dict(
                color='Black',
                size=10)))
        fig = go.Figure(
            data=data,
            layout=go.Layout(
                showlegend=True,
                legend=dict(
                    yanchor="bottom",
                    y=0.01,
                    xanchor="left",
                    x=0.01
                ),
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=0),
                paper_bgcolor="#AAF",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

        for arrow in self._arrows:
            fig.add_annotation(
                x=arrow.head_x,
                y=arrow.head_y,
                ax=arrow.tail_x,
                ay=arrow.tail_y,
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                arrowsize=0.3 + arrow.size,
                arrowwidth=1,
                hovertext=arrow.get_annotation(),
                text="o",
                showarrow=True,
                arrowhead=1,
            )

        return fig

    def _get_simple_nodes_scatter(self) -> go.Scatter:
        return self._get_nodes_scatter('simple node', self._simple_nodes, dict(
            thickness=20,
            title='Difference between simple nodes demands [MV]',
            xanchor='left',
            titleside='right',
            x=1,
        ))

    def _get_gens_scatter(self) -> go.Scatter:
        return self._get_nodes_scatter('generator', self._gens, dict(
            thickness=20,
            ticks='',
            title='Generator balance [PLN]',
            titleside='right',
            xanchor='right',
            x=0
        ))

    def _get_branches_scatters(self) -> List[go.Scatter]:
        branches_scatters: List[go.Scatter] = list()

        for i, branch in enumerate(self._branches):
            x0, y0 = self._nodes_positions[branch.from_node]
            x1, y1 = self._nodes_positions[branch.to_node]
            x = [x0, x1]
            y = [y0, y1]
            width = branch.width
            branches_scatters.append(go.Scatter(
                showlegend=(i == 0),
                legendgroup='branches',
                name='flow',
                x=x, y=y,
                line=dict(width=width, color='#888'),
                mode='lines'))

        return branches_scatters

    def _get_nodes_scatter(self, name: str, nodes: List[Node], colorbar: dict) -> go.Scatter:
        xs: List[float] = list()
        ys: List[float] = list()

        for node in nodes:
            x, y = self._nodes_positions[node.id]
            xs.append(x)
            ys.append(y)

        texts = [node.desc for node in nodes]
        marker_symbols = [NODE_TYPE_TO_SYMBOL[node.type] for node in nodes]
        colors = [node.color for node in nodes]
        sizes = [size_scale(node.size) for node in nodes]
        max_abs_color = max([abs(color) for color in colors])

        return go.Scatter(
            x=xs, y=ys,
            text=texts,
            mode='markers',
            name=name,
            showlegend=True,
            marker_symbol=marker_symbols,
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='RdBu',
                cmax=max_abs_color,
                cmin=-max_abs_color,
                reversescale=False,
                color=colors,
                size=sizes,
                colorbar=colorbar,
                line=dict(
                    width=1,
                    color='Black',
                )))


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
