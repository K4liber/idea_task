from os.path import join

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


def get_scatters(hour_from: int, hour_to: int) -> list:
    nodes_from = hour_to_nodes[hour_from]
    branches_from = hour_to_branches[hour_from]
    nodes_to = hour_to_nodes[hour_to]
    branches_to = hour_to_branches[hour_to]
    # TODO add info about gens to the graph
    # gens_from = hour_to_gens[hour_from]
    # gens_to = hour_to_gens[hour_to]

    for node_id in nodes_from:
        G.add_node(node_id)

    for node_id in nodes_to:
        G.add_node(node_id)

    for branch in branches_from:
        G.add_edge(branch[0], branch[1])

    for branch in branches_to:
        G.add_edge(branch[0], branch[1])

    pos = nx.spring_layout(G, seed=42)
    scatters = list()

    for (node_from, node_to), branch in branches_to.items():
        x0, y0 = pos[node_from]
        x1, y1 = pos[node_to]

        if (node_from, node_to) in branches_from:
            width = branch.get_flow() - branches_from[(node_from, node_to)].get_flow()
        elif (node_to, node_from) in branches_from:
            width = branch.get_flow() + branches_from[(node_to, node_from)].get_flow()
        else:
            width = branch.get_flow()
        # TODO visualize the direction of the flow
        if width >= 0:
            x = [x0, x1, None]
            y = [y0, y1, None]
            text = 'Flow diff #%d -> #%d = %f [MW]' % (node_from, node_to, width)
        else:
            x = [x1, x0, None]
            y = [y1, y0, None]
            width = abs(width)
            text = 'Flow diff #%d -> #%d = %f [MW]' % (node_to, node_from, width)

        scatters.append(go.Scatter(
            x=x, y=y,
            line=dict(width=width, color='#888'),
            hovertext=text,
            hoverinfo='text',
            mode='lines+text'))

    is_first = True
    # TODO visualize node differences
    for node_id, node in nodes_from.items():
        x, y = pos[node_id]
        scatters.append(go.Scatter(
            x=[x], y=[y],
            text='node %d' % node_id,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=is_first,
                # colorscale options
                # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='YlGnBu',
                reversescale=True,
                color=node.get_demand(),
                size=node.get_demand(),
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2)))
        is_first = False

    return scatters


def get_figure(hour_from: int, hour_to: int) -> go.Figure:
    return go.Figure(
        data=get_scatters(hour_from, hour_to),
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


app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=get_figure(6, 12), id='network', style={'width': '90vw', 'height': '80vh', 'margin': '0 auto'}),
    html.Div(
        [
            dcc.Input(id='hour_from', type='number', value=6, min=1, max=24),
            dcc.RangeSlider(
                id='slider',
                min=1,
                max=24,
                marks={x+1: str(x+1) for x in range(24)},
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
