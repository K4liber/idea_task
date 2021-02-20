import os
from os.path import join

import dash
import dash_core_components as dcc
import dash_html_components as html

from ..data.in_memory import DatabaseInMemory
from ..definitions import ROOT_DIR
from ..vis.network import NetworkData

hd5_files_dir = join(ROOT_DIR, 'data/hd5/files/')
db = DatabaseInMemory(hd5_files_dir)
network_data = NetworkData(db)
assets_path = join(ROOT_DIR, 'vis/assets/')
app = dash.Dash(assets_folder=assets_path)
app.layout = html.Div([
    dcc.Graph(figure=network_data.get_state(6, 12).get_figure(),
              id='network', style={'width': '90vw', 'height': '95vh', 'margin': '0 auto'}),
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
        style={'display': 'grid', 'grid-template-columns': '5% 90% 5%', 'height': '5vh'}),
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
    return [new_values[0], new_values[1], network_data.get_state(new_values[0], new_values[1]).get_figure()]


app.run_server(host='0.0.0.0', debug=False, use_reloader=True)
