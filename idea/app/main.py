import math
from os.path import join
from typing import Dict, Tuple

import plotly.graph_objects as go

import networkx as nx

import dash
import dash_core_components as dcc
import dash_html_components as html

from ..data.in_memory import DatabaseInMemory
from ..definitions import ROOT_DIR

# TODO refactor this file
hd5_files_dir = join(ROOT_DIR, 'data/hd5/files/')
db = DatabaseInMemory(hd5_files_dir)
hour_to_nodes = db.get_hour_to_nodes()
hour_to_branches = db.get_hour_to_branches()
hour_to_gens = db.get_hour_to_gens()
G = nx.Graph()


def size_scale(size: float) -> float:
    return math.sqrt(100*size)

# TODO Relative if hour_from != hour_to, otherwise just a network state
# TODO Divide node by simple and generators (scale on the left for the generators costs)
# TODO Annotate info about nodes and branches
# TODO Refactor this ugly code


class Arrow:
    def __init__(self, head_x: float, head_y: float, tail_x: float = 0, tail_y: float = 0, size: float = 0):
        self.head_x = head_x
        self.head_y = head_y
        self.tail_x = tail_x
        self.tail_y = tail_y
        self.size = size


def get_arrow_from_branch(node_1: int, node_2: int, width: float, nodes_pos: Dict[int, Tuple[float, float]]) -> Arrow:
    x0, y0 = nodes_pos[node_1]
    x1, y1 = nodes_pos[node_2]
    return Arrow(x0 + (x1 - x0)/2, y0 + (y1 - y0)/2, x1, y1, math.sqrt(width))


def get_figure(hour_from: int, hour_to: int) -> go.Figure:
    nodes_from = hour_to_nodes[hour_from]
    branches_from = hour_to_branches[hour_from]
    nodes_to = hour_to_nodes[hour_to]
    branches_to = hour_to_branches[hour_to]
    gens_from = hour_to_gens[hour_from]
    gens_to = hour_to_gens[hour_to]

    for node_id in nodes_from:
        G.add_node(node_id)

    for node_id in nodes_to:
        G.add_node(node_id)

    for branch in branches_from:
        G.add_edge(branch[0], branch[1])

    for branch in branches_to:
        G.add_edge(branch[0], branch[1])

    pos = nx.spring_layout(G, seed=9)
    scatters = list()
    arrows = list()

    for (node_from, node_to), branch in branches_to.items():
        x0, y0 = pos[node_from]
        x1, y1 = pos[node_to]

        if (node_from, node_to) in branches_from:
            color = branch.get_flow() - branches_from[(node_from, node_to)].get_flow()
            width = (abs(branch.get_flow()) + abs(branches_from[(node_from, node_to)].get_flow()))/2
        elif (node_to, node_from) in branches_from:
            color = branch.get_flow() + branches_from[(node_to, node_from)].get_flow()
            width = (abs(branch.get_flow()) + abs(branches_from[(node_to, node_from)].get_flow())) / 2
        else:
            color = branch.get_flow()
            width = abs(branch.get_flow())

        if color >= 0:
            x = [x0, x1, None]
            y = [y0, y1, None]
            text = 'Flow diff #%d -> #%d = %f [MW]' % (node_from, node_to, color)
            arrows.append(get_arrow_from_branch(node_from, node_to, width, pos))
        else:
            x = [x1, x0, None]
            y = [y1, y0, None]
            color = abs(color)
            text = 'Flow diff #%d -> #%d = %f [MW]' % (node_to, node_from, color)
            arrows.append(get_arrow_from_branch(node_to, node_from, width, pos))

        scatters.append(go.Scatter(
            x=x, y=y,
            line=dict(width=width, color='#888'),
            hovertext='asdasd',
            text='',
            mode='lines+text'))

    x_list = []
    y_list = []
    gen_base_list = []
    gen_diff_list = []
    cost_list = []
    demand_diff_list = []
    node_size_list = []
    text_list = []
    types_list = []

    for node_id, node in nodes_to.items():
        gen_base = 0
        gen_diff = 0
        cost = 0

        if node_id in gens_to:
            gen_base = gens_to[node_id].get_generation()
            cost = gens_to[node_id].get_cost()

            if node_id in gens_from:
                gen_diff = gens_to[node_id].get_generation() - gens_from[node_id].get_generation()
            else:
                gen_diff = gens_to[node_id].get_generation()

        if node_id in nodes_from:
            demand_diff = node.get_demand() - nodes_from[node_id].get_demand()
        else:
            demand_diff = node.get_demand()

        x, y = pos[node_id]
        x_list.append(x)
        y_list.append(y)
        gen_base_list.append(gen_base)
        gen_diff_list.append(gen_diff)
        cost_list.append(cost)
        demand_diff_list.append(demand_diff)
        text_list.append(
            'Node #%d, type %d <br>' % (node_id, node.get_type()) +
            'demand diff = %.2f [MV] <br>' % demand_diff +
            'generation = %.2f [MV] <br>' % gen_base
        )
        types_list.append(node.get_type() - 1)
        node_size_list.append((abs(nodes_from[node_id].get_demand()) + abs(nodes_to[node_id].get_demand())) / 2.0)

    type_to_symbol = {
        0: 0,
        1: 27,
        2: 28,
    }
    types_list = [type_to_symbol[x] for x in types_list]
    scatters.append(go.Scatter(
        x=x_list, y=y_list,
        text=text_list,
        mode='markers',
        marker_symbol=types_list,
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='RdBu',
            cmax=30,
            cmin=-30,
            reversescale=False,
            color=demand_diff_list,
            size=[size_scale(x + gen_base_list[i]) for i, x in enumerate(node_size_list)],
            colorbar=dict(
                thickness=15,
                title='Difference between node demands [MV]',
                xanchor='left',
                titleside='right'
            ),
            line=dict(
                width=[size_scale(x) for x in gen_base_list],
                color=cost_list,
                colorscale='Greens',
            ),
        )
    ))

    figure = go.Figure(
        data=scatters,
        layout=go.Layout(
            title='<br>Difference between electricity network states',
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            paper_bgcolor="#AAF",
            annotations=[dict(
                text="Idea task",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002)],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )

    for arrow in arrows:
        figure.add_annotation(
            x=arrow.head_x,  # arrows' head
            y=arrow.head_y,  # arrows' head
            ax=arrow.tail_x,  # arrows' tail
            ay=arrow.tail_y,  # arrows' tail
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            arrowsize=0.3 + arrow.size,
            arrowwidth=1,
            text="",
            showarrow=True,
            arrowhead=1
        )
    return figure


app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=get_figure(6, 12), id='network', style={'width': '90vw', 'height': '90vh', 'margin': '0 auto'}),
    html.Div(
        [
            dcc.Input(id='hour_from', type='number', value=6, min=1, max=24),
            dcc.RangeSlider(
                id='slider',
                min=1,
                max=24,
                marks={x + 1: str(x + 1) for x in range(24)},
                value=[6, 12],
                allowCross=True
            ),
            dcc.Input(id='hour_to', type='number', value=12, min=1, max=24)
        ],
        id='range',
        style={"display": "grid", "grid-template-columns": "5% 90% 5%"}),
],
    style={'background-color': '#AAF', 'margin': '0px'},
)


@app.callback(
    dash.dependencies.Output('slider', 'value'),
    [dash.dependencies.Input('hour_from', 'value'),
     dash.dependencies.Input('hour_to', 'value')])
def hours_changed(new_hour_from, new_hour_to):
    return [new_hour_from, new_hour_to]


@app.callback(
    [
        dash.dependencies.Output('hour_from', 'value'),
        dash.dependencies.Output('hour_to', 'value'),
        dash.dependencies.Output('network', 'figure')
    ],
    dash.dependencies.Input('slider', 'value'))
def slider_changed(new_values):
    return [new_values[0], new_values[1], get_figure(new_values[0], new_values[1])]


app.run_server(host='0.0.0.0', debug=False, use_reloader=True)
